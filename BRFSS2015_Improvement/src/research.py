"""Leakage-conscious BRFSS experiments. No clinical results ship with this project."""
import argparse, hashlib, json, platform, time, warnings
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.feature_selection import mutual_info_classif, RFE
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, balanced_accuracy_score, recall_score,
 precision_score, f1_score, roc_auc_score, average_precision_score, confusion_matrix)
from sklearn.model_selection import StratifiedGroupKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler
from data_io import read_xpt, inspect_xpt

SEED = 2026

def digest(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()

def write_json(path,obj):
    Path(path).write_text(json.dumps(obj,indent=2,default=str),encoding='utf8')

def read_data(path):
    p=Path(path)
    if p.suffix.lower() in ['.xpt', '.zip']: return read_xpt(p)
    if p.suffix.lower()=='.parquet': return pd.read_parquet(p)
    return pd.read_csv(p,low_memory=False)

def load(path,schema_path):
    s=json.loads(Path(schema_path).read_text())
    if not s.get('codebook_reviewed') or not s.get('codebook_source'):
        raise ValueError('Review official 2015 codebook and set codebook_reviewed first.')
    if s.get('unverified_items'):
        raise ValueError('Resolve documented unverified_items before training; do not just flip the review flag.')
    df=read_data(path)
    if s.get('task')!='binary': raise ValueError('Only an explicitly defined binary cohort is accepted.')
    features=s['features']; target=s['target']; names=list(features)
    prohibited={'DIABETE3','DIABAGE2','INSULIN','BLDSUGAR','FEETCHK2','DOCTDIAB','CHKHEMO3','FEETCHK','EYEEXAM','DIABEYE','DIABEDU'}
    if any(n.upper() in prohibited or n.upper().startswith('DIAB') for n in names):
        raise ValueError('Known diabetes diagnosis/treatment variable in predictors; explicit leakage exclusion required.')
    if target in names or not names: raise ValueError('Target must be excluded; features required.')
    if s.get('population_inference',False):
        raise ValueError('Population inference requires a survey-design analysis; this runner is predictive only.')
    design=[s.get(k) for k in ['weight','strata','psu','group_column','split_column'] if s.get(k)]
    if set(names)&set(design): raise ValueError('Design/ID/split columns cannot be predictors.')
    required=set(names+[target]+design)
    if required-set(df): raise ValueError(f'Missing columns: {required-set(df)}')
    for n,spec in features.items():
        if spec.get('type') not in ['continuous','categorical','ordinal']: raise ValueError(f'Unknown type: {n}')
        if spec.get('leakage_review')!='safe' or not spec.get('rationale') or not spec.get('codebook_reference'):
            raise ValueError(f'Explicit leakage review, rationale and codebook citation required: {n}')
        if 'missing_codes' not in spec or 'valid_values' not in spec and 'valid_range' not in spec:
            raise ValueError(f'Explicit missing and valid codes/range required: {n}')
        if spec['type']=='ordinal' and not spec.get('order'): raise ValueError(f'Ordinal order required: {n}')
    for role,n in s.get('roles',{}).items():
        if n not in features: raise ValueError(f'Role references missing feature: {role}={n}')
        if role in ['age','bmi','physical_days','mental_days'] and features[n]['type']!='continuous':
            raise ValueError(f'{role} must be expressed in physical units, not ordinal category codes.')
        if role=='activity':
            spec=features[n]
            if spec.get('valid_values') != [0,1] and spec.get('valid_range') != [0,1]:
                raise ValueError('Activity interactions require explicit 0/1 recoding and valid domain.')
    mapping={str(k):v for k,v in s['label_map'].items()}
    if set(v for v in mapping.values() if v is not None)!={0,1}: raise ValueError('label_map must define 0 and 1.')
    # Numeric BRFSS codes normalize identically in CSV and XPT.
    def key(v):
        if pd.isna(v): return '__missing__'
        try: return str(int(v)) if float(v).is_integer() else str(v)
        except (ValueError,TypeError): return str(v)
    raw=df[target].map(key)
    unknown=set(raw)-set(mapping)-{'__missing__'}
    if unknown: raise ValueError(f'Unmapped target codes: {unknown}')
    labels=raw.map(mapping); keep=labels.notna()
    X=df.loc[keep,names].copy(); y=labels[keep].astype(int).reset_index(drop=True)
    audit=[]
    for n,spec in features.items():
        a=X[n]; clean=a.replace(spec['missing_codes'],np.nan)
        if 'raw_valid_values' in spec:
            invalid_raw=clean.notna() & ~clean.isin(spec['raw_valid_values'])
            if invalid_raw.any(): raise ValueError(f'{n}: unexpected raw codes before recode; review codebook.')
        clean=clean.replace({float(k):v for k,v in spec.get('recode',{}).items()})
        if 'valid_values' in spec: invalid=clean.notna() & ~clean.isin(spec['valid_values'])
        else: invalid=clean.notna() & ~clean.between(*spec['valid_range'])
        if invalid.any(): raise ValueError(f'{n}: {invalid.sum()} unexpected values; review codebook.')
        audit.append(dict(feature=n,type=spec['type'],raw_missing=int(a.isna().sum()),
                          coded_missing=int(clean.isna().sum()),unique=int(clean.nunique()),
                          leakage_review=spec['leakage_review'],source=spec['codebook_reference']))
        X[n]=clean
    X=X.reset_index(drop=True)
    # Identical predictor profiles stay in one partition; no rows are dropped.
    hashes=pd.util.hash_pandas_object(X,index=False).astype(str)
    group=hashes.copy()
    if s.get('group_column'):
        if df.loc[keep,s['group_column']].isna().any(): raise ValueError('Missing group IDs.')
        # Union duplicate profiles and respondent/site groups to prevent either crossing partitions.
        parent=list(range(len(X)))
        def root(i):
            while parent[i]!=i: parent[i]=parent[parent[i]]; i=parent[i]
            return i
        for vals in [hashes,df.loc[keep,s['group_column']].reset_index(drop=True)]:
            first={}
            for i,v in enumerate(vals):
                if v in first: parent[root(i)]=root(first[v])
                else: first[v]=i
        group=pd.Series([str(root(i)) for i in range(len(X))])
    info=dict(input_provenance=df.attrs.get('input_provenance',{}),detected_survey_columns=[n for n in ['_LLCPWT','_STSTR','_PSU'] if n in df],raw_rows=len(df),cohort_rows=len(X),excluded_target_rows=int((~keep).sum()),
              features=len(names),label_counts=y.value_counts().to_dict(),
              duplicate_full_records=int(df.duplicated().sum()),duplicate_profiles=int(hashes.duplicated().sum()),
              conflicting_label_profiles=int(pd.DataFrame({'h':hashes,'y':y}).groupby('h').y.nunique().gt(1).sum()),
              survey_design={k:s.get(k) for k in ['weight','strata','psu']},
              estimand='Unweighted predictive performance in the defined cohort; not population inference',
              cohort_definition=s.get('cohort_definition'),label_map=mapping)
    if s.get('split_column'):
        split=df.loc[keep,s['split_column']].reset_index(drop=True)
        if not split.isin(['train','test']).all(): raise ValueError('Split column must contain train/test.')
        tr=np.flatnonzero(split.eq('train')); te=np.flatnonzero(split.eq('test'))
        if set(group.iloc[tr])&set(group.iloc[te]): raise ValueError('Existing split leaks groups/duplicate profiles.')
        info['split_reason']='Reused supplied train/test assignment; prior test-use history must be documented.'
    else:
        tr,te=next(StratifiedGroupKFold(5,shuffle=True,random_state=SEED).split(X,y,group))
        info['split_reason']='No supplied split. First fixed stratified group fold held out (~20%). No old test scores used.'
    if min(y.iloc[tr].nunique(),y.iloc[te].nunique())<2: raise ValueError('Both partitions require both classes.')
    return X,y,group,s,pd.DataFrame(audit),info,np.asarray(tr),np.asarray(te)

class Features(BaseEstimator,TransformerMixin):
    def __init__(self,schema,variant='B0',engineering='D0'):
        self.schema=schema; self.variant=variant; self.engineering=engineering
    def fit(self,X,y=None): return self
    def transform(self,X):
        X=X.copy(); roles=self.schema.get('roles',{})
        def col(role):
            n=roles.get(role); return X[n] if n in X else None
        bmi=col('bmi'); age=col('age'); activity=col('activity')
        if self.variant=='B3':
            if bmi is not None:
                # Physical units must be defined by schema scale; e.g. _BMI5 scale=0.01.
                b=bmi*self.schema['features'][roles['bmi']].get('scale',1)
                X['eng_bmi_group']=pd.cut(b,[-np.inf,18.5,25,30,np.inf],right=False,labels=False).astype(float)
            for role in ['physical_days','mental_days']:
                c=col(role)
                if c is not None: X['eng_log_'+role]=np.log1p(c)
        if self.engineering in ['D1','D3','D4']:
            if bmi is not None and age is not None: X['eng_age_bmi']=age*bmi
            if bmi is not None and activity is not None: X['eng_bmi_activity']=bmi*activity
            if age is not None and activity is not None: X['eng_age_activity']=age*activity
        if self.engineering in ['D2','D3','D4']:
            for name,definition in self.schema.get('composites',{}).items():
                # Explicit equal-count exploratory indices; missing if any component is missing.
                parts=[X[n].isin(codes).astype(float).where(X[n].notna()) for n,codes in definition.items()]
                X['eng_'+name]=pd.concat(parts,axis=1).sum(axis=1,min_count=len(parts))
        return X

def processor(s,X,variant):
    categorical=[n for n in X if n in s['features'] and s['features'][n]['type']=='categorical']
    ordinal=[n for n in X if n in s['features'] and s['features'][n]['type']=='ordinal']
    numeric=[n for n in X if n not in categorical+ordinal]
    if 'eng_bmi_group' in numeric: numeric.remove('eng_bmi_group'); categorical.append('eng_bmi_group')
    # B2 preserves declared order; B0/B1 use OHE even for ordinal categories.
    if variant!='B2': categorical+=ordinal; ordinal=[]
    blocks=[]
    if numeric: blocks.append(('num',Pipeline([('imp',SimpleImputer(strategy='median',add_indicator=variant=='B1',keep_empty_features=True)),('scale',StandardScaler())]),numeric))
    if categorical:
        imp=SimpleImputer(strategy='constant',fill_value=-999,keep_empty_features=True) if variant=='B1' else SimpleImputer(strategy='most_frequent',keep_empty_features=True)
        blocks.append(('cat',Pipeline([('imp',imp),('enc',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),categorical))
    if ordinal:
        blocks.append(('ord',Pipeline([('imp',SimpleImputer(strategy='most_frequent',keep_empty_features=True)),('enc',OrdinalEncoder(categories=[s['features'][n]['order'] for n in ordinal],handle_unknown='use_encoded_value',unknown_value=-1))]),ordinal))
    return ColumnTransformer(blocks,verbose_feature_names_out=True)

def model(name,params=None):
    p=params or {}
    if name=='LR': return LogisticRegression(max_iter=1500,random_state=SEED,**p)
    if name=='RF': return RandomForestClassifier(n_estimators=200,n_jobs=2,random_state=SEED,**p)
    if name=='ET': return ExtraTreesClassifier(n_estimators=200,n_jobs=2,random_state=SEED,**p)
    if name=='LGBM':
        from lightgbm import LGBMClassifier
        return LGBMClassifier(n_estimators=250,n_jobs=2,verbosity=-1,random_state=SEED,**p)
    if name=='XGB':
        from xgboost import XGBClassifier
        return XGBClassifier(n_estimators=250,n_jobs=2,tree_method='hist',random_state=SEED,**p)
    if name=='CAT':
        from catboost import CatBoostClassifier
        return CatBoostClassifier(iterations=250,thread_count=2,verbose=False,allow_writing_files=False,random_seed=SEED,**p)
    raise ValueError(name)

class Selector(BaseEstimator,TransformerMixin):
    """Raw feature ranking, fitted solely inside each outer training partition."""
    def __init__(self,schema,method='all',k=20,seed=SEED): self.schema=schema; self.method=method; self.k=k; self.seed=seed
    def fit(self,X,y,groups=None):
        self.ranking_=pd.Series(0.,index=X.columns)
        if self.method=='all': self.selected_=list(X); return self
        prep=processor(self.schema,X,'B2'); Z=prep.fit_transform(X,y)
        # Recover raw columns from ColumnTransformer output slices; sum encoded importances.
        raw=[]
        for name,trans,cols in prep.transformers_:
            if name=='remainder': continue
            if name=='cat':
                for c,cats in zip(cols,trans.named_steps['enc'].categories_): raw.extend([c]*len(cats))
            else: raw.extend(cols)
        if self.method=='mi': score=mutual_info_classif(Z,y,discrete_features=np.array([self.schema['features'].get(c,{}).get('type')!='continuous' and not c.startswith('eng_') for c in raw]),random_state=self.seed)
        elif self.method=='l1':
            m=LogisticRegression(penalty='l1',solver='liblinear',C=.05,max_iter=1500,random_state=self.seed).fit(Z,y); score=np.abs(m.coef_[0])
        elif self.method=='rfe':
            m=RFE(LogisticRegression(max_iter=1000),n_features_to_select=1,step=.2).fit(Z,y); score=1/m.ranking_
        elif self.method=='rf': score=RandomForestClassifier(n_estimators=100,n_jobs=2,random_state=self.seed).fit(Z,y).feature_importances_
        elif self.method=='permutation':
            # Nested holdout is part of outer TRAIN. No final test or outer validation used.
            hashes=pd.util.hash_pandas_object(X,index=False) if groups is None else np.asarray(groups)
            a,b=next(StratifiedGroupKFold(3,shuffle=True,random_state=self.seed).split(X,y,hashes))
            p=Pipeline([('prep',processor(self.schema,X,'B2')),('model',model('LR'))]).fit(X.iloc[a],np.asarray(y)[a])
            score=permutation_importance(p,X.iloc[b],np.asarray(y)[b],scoring='balanced_accuracy',n_repeats=3,random_state=self.seed,n_jobs=2).importances_mean
            raw=list(X)
        else: raise ValueError(self.method)
        self.ranking_=pd.Series(score,index=raw).groupby(level=0).sum().reindex(X.columns).sort_values(ascending=False)
        self.selected_=self.ranking_.head(min(self.k,len(X.columns))).index.tolist(); return self
    def transform(self,X): return X[self.selected_]

class NativeCat(BaseEstimator):
    def __init__(self,schema,params=None): self.schema=schema; self.params=params
    def prepare(self,X):
        X=X.copy()
        for n in X:
            if n in self.cats_: X[n]=X[n].map(lambda v:'__MISSING__' if pd.isna(v) else str(v))
        return X
    def fit(self,X,y):
        self.cats_=[n for n in X if self.schema['features'].get(n,{}).get('type') in ['categorical','ordinal'] or n=='eng_bmi_group']
        self.estimator_=model('CAT',self.params); self.estimator_.fit(self.prepare(X),y,cat_features=self.cats_); self.classes_=self.estimator_.classes_; return self
    def predict_proba(self,X): return self.estimator_.predict_proba(self.prepare(X))

def pipeline(s,c,X):
    eng=Features(s,c['preprocessing'],c['engineering']); probe=eng.transform(X.iloc[:1])
    select=Selector(s,c.get('selection','all'),c.get('k',20))
    # Processor is built after selection: callable column selection avoids assuming selected names.
    if c['model']=='CAT' and c.get('native',False): end=[('model',NativeCat(s,c.get('params')))]
    else:
        # Dynamic preprocessing learns schema after selector has run.
        end=[('prep',DynamicPrep(s,c['preprocessing'])),('model',model(c['model'],c.get('params')))]
    return Pipeline([('features',eng),('selection',select)]+end)

class DynamicPrep(BaseEstimator,TransformerMixin):
    def __init__(self,schema,variant): self.schema=schema; self.variant=variant
    def fit(self,X,y=None): self.prep_=processor(self.schema,X,self.variant).fit(X,y); return self
    def transform(self,X): return self.prep_.transform(X)

def metrics(y,p,threshold=.5):
    pred=np.asarray(p)>=threshold; tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel()
    return dict(accuracy=accuracy_score(y,pred),balanced_accuracy=balanced_accuracy_score(y,pred),
      sensitivity=recall_score(y,pred,zero_division=0),specificity=tn/max(tn+fp,1),precision=precision_score(y,pred,zero_division=0),
      f1=f1_score(y,pred,zero_division=0),roc_auc=roc_auc_score(y,p),pr_auc=average_precision_score(y,p),tn=int(tn),fp=int(fp),fn=int(fn),tp=int(tp))

def evaluate_cv(X,y,g,s,c,folds,deadline):
    rows=[]; ranks=[]; sets=[]
    for f,(a,b) in enumerate(StratifiedGroupKFold(folds,shuffle=True,random_state=SEED).split(X,y,g)):
        if time.monotonic()>deadline: raise TimeoutError('Budget exhausted; incomplete experiment is not scored.')
        p=pipeline(s,c,X).fit(X.iloc[a],y.iloc[a],selection__groups=g.iloc[a]); probs=p.predict_proba(X.iloc[b])[:,1]
        rows.append(dict(fold=f,**metrics(y.iloc[b],probs)))
        sel=p.named_steps['selection']; sets.append(set(sel.selected_))
        ranks.extend(dict(fold=f,feature=n,importance=float(v),selected=n in sel.selected_) for n,v in sel.ranking_.items())
    stability=np.mean([len(a&b)/len(a|b) for i,a in enumerate(sets) for b in sets[i+1:]])
    result={k:float(np.mean([r[k] for r in rows])) for k in ['accuracy','sensitivity','balanced_accuracy','specificity','precision','f1','roc_auc','pr_auc']}
    result.update({k+'_std':float(np.std([r[k] for r in rows],ddof=1)) for k in ['accuracy','sensitivity','balanced_accuracy']})
    result['stability_jaccard']=stability
    return result,rows,ranks

def candidates():
    base=dict(preprocessing='B0',engineering='D0',selection='all',model='LR',k=20)
    out=[dict(base,id='baseline')]
    for b in ['B1','B2','B3']: out.append(dict(base,id=b,preprocessing=b))
    for m in ['RF','ET','XGB','LGBM','CAT']: out.append(dict(base,id=m,model=m,native=m=='CAT'))
    # Controlled FS comparison: all methods and sizes use the same estimator/protocol.
    for method in ['mi','l1','rfe','permutation','rf']:
        for k in [5,10,15,20]: out.append(dict(base,id=f'FS_{method}_{k}',selection=method,k=k))
    for d in ['D1','D2','D3','D4']:
        out.append(dict(base,id=d,engineering=d,selection='rf' if d=='D4' else 'all',k=20))
    # Prioritized boosted models with fixed engineering to test useful combinations.
    for m in ['CAT','LGBM']:
        for d in ['D0','D3','D4']:
            out.append(dict(base,id=f'{m}_{d}_B1',model=m,preprocessing='B1',engineering=d,selection='rf' if d=='D4' else 'all',native=m=='CAT'))
    return out

def train(args):
    if json.loads(Path(args.schema).read_text()).get('audit_only'):
        raise PermissionError('This schema is audit-only. Train/CV is not authorized in this phase.')
    out=Path(args.output)
    if out.exists(): raise ValueError('Use a new output directory; never overwrite prior experiments.')
    out.mkdir(parents=True)
    for n in ['00_Audit','01_Preprocessing','02_Feature_Selection','03_Feature_Engineering','04_Model_Training','05_Optimization','06_Final_Evaluation','07_Reports']: (out/n).mkdir()
    X,y,g,s,audit,info,tr,te=load(args.data,args.schema)
    audit.to_csv(out/'00_Audit/data_audit.csv',index=False)
    info.update(train_rows=len(tr),test_rows=len(te),train_labels=y.iloc[tr].value_counts().to_dict(),test_labels=y.iloc[te].value_counts().to_dict())
    write_json(out/'00_Audit/cohort.json',info)
    np.savez(out/'00_Audit/split.npz',train=tr,test=te)
    provenance=dict(source_sha256=digest(__file__),io_source_sha256=digest(Path(__file__).with_name('data_io.py')),seed=SEED,data_sha256=digest(args.data),schema_sha256=digest(args.schema),args=vars(args),python=platform.python_version())
    import importlib.metadata as md
    provenance['versions']={n:md.version(n) for n in ['numpy','pandas','scipy','scikit-learn','joblib']}
    for n in ['catboost','lightgbm','xgboost','optuna']:
        try: provenance['versions'][n]=md.version(n)
        except md.PackageNotFoundError: pass
    write_json(out/'provenance.json',provenance); write_json(out/'schema.json',s)
    X=X.iloc[tr].reset_index(drop=True); y=y.iloc[tr].reset_index(drop=True); g=g.iloc[tr].reset_index(drop=True)
    deadline=time.monotonic()+args.hours*3600; results=[]; failures=[]; configs={}; allranks=[]; foldrows=[]
    def run(c):
        scores,rows,ranks=evaluate_cv(X,y,g,s,c,args.folds,deadline)
        results.append(dict(experiment=c['id'],features=f"{c['engineering']}/{c['selection']}/k={c['k']}",model=c['model'],**scores))
        configs[c['id']]=c
        allranks.extend(dict(experiment=c['id'],**r) for r in ranks)
        foldrows.extend(dict(experiment=c['id'],**r) for r in rows)
        pd.DataFrame(results).to_csv(out/'04_Model_Training/model_cv_comparison.csv',index=False)
        print(c['id'],scores,flush=True)
        return scores
    for c in candidates():
        if args.smoke and c['id'] not in ['baseline','B1','FS_rf_5','D3']: continue
        if time.monotonic()>deadline: failures.append(dict(experiment=c['id'],status='unrun_budget')); continue
        try: run(c)
        except Exception as e:
            failures.append(dict(experiment=c['id'],status='failed',error=repr(e)))
            if c['id']=='baseline': write_json(out/'failures.json',failures); raise
    # Preregistered selection constraint: tolerate <=2 percentage points sensitivity loss
    # versus baseline, then near ties (0.2pp accuracy) favor balanced accuracy / PR-AUC.
    def choose(rows):
        baseline=next(r for r in results if r['experiment']=='baseline')
        eligible=[r for r in rows if r['sensitivity']>=baseline['sensitivity']-.02]
        if not eligible: return baseline
        top=max(r['accuracy'] for r in eligible)
        return max([r for r in eligible if r['accuracy']>=top-.002],key=lambda r:(r['balanced_accuracy'],r['pr_auc'],r['sensitivity']))
    if not args.smoke and args.trials:
        import optuna
        bymodel={}
        for r in results:
            if r['model'] in ['CAT','LGBM','XGB']: bymodel.setdefault(r['model'],[]).append(r)
        leaders=sorted([max(v,key=lambda r:r['balanced_accuracy']) for v in bymodel.values()],key=lambda r:r['balanced_accuracy'],reverse=True)[:2]
        for leader in leaders:
            original=configs[leader['experiment']]
            def objective(trial):
                params={'learning_rate':trial.suggest_float('learning_rate',.02,.15,log=True)}
                if original['model']=='CAT': params['depth']=trial.suggest_int('depth',4,8)
                else: params.update(max_depth=trial.suggest_int('max_depth',3,8),reg_lambda=trial.suggest_float('reg_lambda',.1,10,log=True))
                c=dict(original,id=f"tune_{original['model']}_{trial.number}",params=params)
                v=run(c)
                baseline=results[0]
                return v['accuracy'] if v['sensitivity']>=baseline['sensitivity']-.02 else v['accuracy']-1
            study=optuna.create_study(direction='maximize',sampler=optuna.samplers.TPESampler(seed=SEED))
            study.optimize(objective,n_trials=args.trials,timeout=max(1,deadline-time.monotonic()),catch=(Exception,))
            write_json(out/f"05_Optimization/{original['model']}_trials.json",study.trials_dataframe().to_dict('records'))
    best=choose(results); c=configs[best['experiment']]
    baseline=pipeline(s,configs['baseline'],X).fit(X,y,selection__groups=g); fitted=pipeline(s,c,X).fit(X,y,selection__groups=g)
    joblib.dump(baseline,out/'baseline.joblib'); joblib.dump(fitted,out/'model.joblib')
    write_json(out/'best_model_config.json',dict(config=c,threshold=.5,selection_rule='Sensitivity >= baseline - .02; accuracy ties within .002 favor balanced accuracy then PR-AUC',selected_features=fitted.named_steps['selection'].selected_,smoke=args.smoke))
    pd.DataFrame(allranks).to_csv(out/'02_Feature_Selection/feature_ranking.csv',index=False)
    pd.DataFrame(foldrows).to_csv(out/'04_Model_Training/fold_scores.csv',index=False)
    table=pd.DataFrame(results)
    table[table.experiment.str.startswith('FS_')].to_csv(out/'02_Feature_Selection/feature_selection_results.csv',index=False)
    table[table.experiment.str.match('D[0-4]')|table.experiment.eq('baseline')].to_csv(out/'03_Feature_Engineering/ablation_results.csv',index=False)
    table[table.experiment.str.match('D[0-4]')|table.experiment.eq('baseline')].to_csv(out/'03_Feature_Engineering/feature_engineering_results.csv',index=False)
    table[table.experiment.isin(['baseline','B1','B2','B3'])].to_csv(out/'01_Preprocessing/preprocessing_results.csv',index=False)
    write_json(out/'failures.json',failures)
    write_json(out/'frozen.json',{n:digest(out/n) for n in ['model.joblib','baseline.joblib','best_model_config.json','00_Audit/split.npz','schema.json']})
    report(out,table,args.smoke)

def report(out,table,smoke=False):
    lines=['# Research summary','', '**Software smoke test only; synthetic data are not BRFSS evidence.**' if smoke else 'CV selection completed; final test is a separate one-time command.',
      '', '## Research Question','Do feature selection, explicit exploratory interactions and boosting improve binary prediction while preserving sensitivity?',
      '## Research Gap','Incremental effects require controlled internal baselines; literature comparability is unverified.',
      '## Dataset and Cohort','See 00_Audit/cohort.json and reviewed schema.json. No mixing with the three-class branch.',
      '## Preprocessing Methodology','B0 median/mode + OHE; B1 missing category + numeric indicators; B2 declared ordinal order; B3 BMI groups and log1p health-day features. Fold-fitted throughout.',
      '## Feature Selection Methodology','MI, L1, RFE, nested-holdout permutation and RF; raw-feature top 5/10/15/20; pairwise Jaccard stability. Full features are the baseline.',
      '## Model Comparison','Same fixed group CV folds, unweighted metrics, fixed threshold 0.5. See failures.json for skipped/failed work.',
      '## Ablation Study','D0 original; D1 interactions; D2 equal-count exploratory composites; D3 both; D4 fold-selected combined variables. Composites are not validated clinical scales.',
      '## Statistical Evaluation','Final test remains locked until final command. Paired group bootstrap estimates conditional predictive differences; it is not survey population inference.',
      '## Limitations','CV reused for experiment selection gives optimistic selection estimates. Finite tuning budget; no causal or population claims. No matched Chang protocol verified. Sensitivity constraint is relative, not a clinical guarantee.',
      '## Conclusion','No claim of exceeding 82.26% is warranted before final evaluation. Internal baseline improvement and literature comparison are separate.',
      '', '|Experiment|Features|Model|CV Accuracy|CV Sensitivity|CV Balanced Accuracy|','|---|---|---|---:|---:|---:|']
    for r in table.to_dict('records'): lines.append(f"|{r['experiment']}|{r['features']}|{r['model']}|{r['accuracy']:.4f}|{r['sensitivity']:.4f}|{r['balanced_accuracy']:.4f}|")
    (out/'07_Reports/research_summary.md').write_text('\n'.join(lines),encoding='utf8')

def final(args):
    if not getattr(args,'unlock_final',False):
        raise PermissionError('Final Test is locked. Explicit --unlock-final is required after independent protocol review.')
    out=Path(args.output); prov=json.loads((out/'provenance.json').read_text())
    if digest(__file__)!=prov['source_sha256']: raise ValueError('Research code changed after freezing.')
    if digest(Path(__file__).with_name('data_io.py'))!=prov['io_source_sha256']: raise ValueError('Input reader changed after freezing.')
    if digest(args.data)!=prov['data_sha256']: raise ValueError('Data changed.')
    for n,h in json.loads((out/'frozen.json').read_text()).items():
        if digest(out/n)!=h: raise ValueError(f'Frozen artifact changed: {n}')
    if json.loads((out/'best_model_config.json').read_text())['smoke']: raise ValueError('Smoke runs cannot generate research final results.')
    X,y,g,s,_,_,_,_=load(args.data,out/'schema.json')
    te=np.load(out/'00_Audit/split.npz')['test']; X=X.iloc[te]; y=y.iloc[te]; g=g.iloc[te]
    # Exclusive lock precedes any test prediction, to discourage repeated test-driven selection.
    lock=out/'06_Final_Evaluation/FINAL_EVALUATION_STARTED'
    with lock.open('x') as f: f.write('Do not tune or rerun based on test outcomes.\n')
    p0=joblib.load(out/'baseline.joblib').predict_proba(X)[:,1]; p1=joblib.load(out/'model.joblib').predict_proba(X)[:,1]
    rows=[dict(model=n,**metrics(y,p)) for n,p in [('baseline',p0),('selected',p1)]]
    pd.DataFrame(rows).to_csv(out/'06_Final_Evaluation/final_test_results.csv',index=False)
    pd.DataFrame({'original_row':te,'y':np.asarray(y),'baseline_probability':p0,'selected_probability':p1}).to_csv(out/'06_Final_Evaluation/test_predictions.csv',index=False)
    diff=((p1>=.5)==np.asarray(y)).astype(float)-((p0>=.5)==np.asarray(y)).astype(float)
    agg=pd.DataFrame({'g':np.asarray(g),'d':diff}).groupby('g').d.agg(['sum','count']).to_numpy()
    rng=np.random.default_rng(SEED); boot=[]
    for _ in range(2000):
        sample=agg[rng.integers(0,len(agg),len(agg))]; boot.append(sample[:,0].sum()/sample[:,1].sum())
    ci=dict(accuracy_difference=float(diff.mean()),ci95=np.quantile(boot,[.025,.975]).tolist(),method='Paired profile/group cluster percentile bootstrap, 2000 replicates; conditional predictive inference, not survey-design inference',benchmark=.8226,selected_point_estimate_above_benchmark=rows[1]['accuracy']>.8226,literature_comparability_verified=False)
    write_json(out/'06_Final_Evaluation/paired_accuracy_ci.json',ci)
    with (out/'07_Reports/research_summary.md').open('a') as f:
        f.write('\n\n## Final Test (one-time evaluation)\n\n|Model|Accuracy|Sensitivity|Balanced Accuracy|\n|---|---:|---:|---:|\n')
        for r in rows: f.write(f"|{r['model']}|{r['accuracy']:.4f}|{r['sensitivity']:.4f}|{r['balanced_accuracy']:.4f}|\n")
        f.write('\n'+json.dumps(ci,indent=2)+'\nA point estimate above the literature benchmark does not establish a fair improvement over Chang et al. (2022).\n')

def inspect(args):
    s=json.loads(Path(args.schema).read_text())
    _,info=inspect_xpt(args.data)
    required=set(s['features'])|{s['target']}|{s[k] for k in ['weight','strata','psu','group_column','split_column'] if s.get(k)}
    info.update(container_sha256=digest(args.data),missing_required_columns=sorted(required-set(info['columns'])),
                codebook_reviewed=s.get('codebook_reviewed',False),unverified_items=s.get('unverified_items',[]),
                final_test_locked=True,seed=SEED)
    out=Path(args.output)
    # Never overwrite a previous preflight report.
    with out.open('x',encoding='utf8') as f: json.dump(info,f,indent=2)
    print(json.dumps(info,indent=2))

def audit_codes(args):
    """Full raw code frequencies for source review; no fit/split/selection/scoring."""
    out=Path(args.output)
    if out.exists(): raise FileExistsError('Raw audit output already exists.')
    s=json.loads(Path(args.schema).read_text())
    frame=read_data(args.data)
    names=list(dict.fromkeys(list(s['features'])+list(s.get('alternatives',{}))+[s['target']]))
    rows=[]
    for n in names:
        if n not in frame: continue
        counts=frame[n].value_counts(dropna=False)
        rows.extend(dict(variable=n,raw_value='__SYSTEM_MISSING__' if pd.isna(v) else str(v),count=int(count)) for v,count in counts.items())
    out.mkdir(parents=True)
    pd.DataFrame(rows).to_csv(out/'raw_code_counts.csv',index=False)
    design={}
    for role in ['weight','strata','psu']:
        n=s.get(role)
        if not n or n not in frame:
            design[role]={'column':n,'present':False};continue
        a=frame[n];v=pd.to_numeric(a,errors='coerce')
        finite=v[np.isfinite(v)]
        design[role]=dict(column=n,present=True,missing=int(a.isna().sum()),unique=int(a.nunique()),
                          nonnumeric=int((a.notna() & v.isna()).sum()),nonfinite=int((v.notna() & ~np.isfinite(v)).sum()),
                          minimum=None if finite.empty else float(finite.min()),maximum=None if finite.empty else float(finite.max()))
        if role=='weight':design[role]['nonpositive']=int(v.le(0).sum())
    joint=[s.get(k) for k in ['strata','psu']]
    if all(n and n in frame for n in joint):
        design['observed_strata_psu_pairs']=int(frame[joint].drop_duplicates().shape[0])
        design['psu_ids_in_multiple_strata']=int(frame.groupby(joint[1])[joint[0]].nunique().gt(1).sum())
    design['interpretation']='Observed diagnostics only; definitions and survey-design inference remain unverified.'
    write_json(out/'raw_code_audit.json',dict(rows=len(frame),columns=len(frame.columns),
               raw_code_counts_sha256=digest(out/'raw_code_counts.csv'),survey_design_audit=design,
               missing_candidate_columns=sorted(set(names)-set(frame)),container_sha256=digest(args.data),
               input_provenance=frame.attrs.get('input_provenance',{}),
               source_verification_complete=False,learned_preprocessing=False,final_test_locked=True,
               note='Observed frequencies are not proof of official code meanings. No split or model was fitted.'))

def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='command',required=True)
    t=sub.add_parser('train'); t.add_argument('--data',required=True); t.add_argument('--schema',required=True); t.add_argument('--output',required=True); t.add_argument('--folds',type=int,default=5); t.add_argument('--hours',type=float,default=60); t.add_argument('--trials',type=int,default=12); t.add_argument('--smoke',action='store_true')
    f=sub.add_parser('final'); f.add_argument('--data',required=True); f.add_argument('--output',required=True); f.add_argument('--unlock-final',action='store_true')
    i=sub.add_parser('inspect'); i.add_argument('--data',required=True); i.add_argument('--schema',required=True); i.add_argument('--output',required=True)
    a=sub.add_parser('audit-codes'); a.add_argument('--data',required=True); a.add_argument('--schema',required=True); a.add_argument('--output',required=True)
    a=p.parse_args(); {'train':train,'final':final,'inspect':inspect,'audit-codes':audit_codes}[a.command](a)
if __name__=='__main__': main()
