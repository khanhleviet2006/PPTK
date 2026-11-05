"""Synthetic integration and leakage guard checks, never research evidence."""
import sys,json,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import research as r
import numpy as np
import pandas as pd
from argparse import Namespace

def main():
    rng=np.random.default_rng(12)
    with tempfile.TemporaryDirectory() as d:
        d=Path(d); n=240
        df=pd.DataFrame({'x':rng.normal(size=n),'cat':rng.integers(1,4,n),'age':rng.integers(1,6,n),'years':rng.integers(18,81,n),'activity':rng.integers(0,2,n),'y':rng.integers(0,2,n)})
        df.loc[::13,'x']=np.nan
        df=pd.concat([df,df.iloc[:10]],ignore_index=True)
        df.to_csv(d/'data.csv',index=False)
        spec={'task':'binary','codebook_reviewed':True,'codebook_source':'SYNTHETIC TEST ONLY','target':'y','label_map':{'0':0,'1':1},'features':{},'roles':{'bmi':'x','age':'years','activity':'activity'},'composites':{'synthetic_count':{'cat':[1],'activity':[0]}}}
        for k,t in [('x','continuous'),('cat','categorical'),('age','ordinal'),('years','continuous'),('activity','categorical')]:
            spec['features'][k]=dict(type=t,missing_codes=[],valid_range=[-10,10],leakage_review='safe',rationale='Synthetic',codebook_reference='Synthetic')
        spec['features']['years']['valid_range']=[18,80]
        spec['features']['activity']['valid_range']=[0,1]
        spec['features']['age']['order']=[1,2,3,4,5]
        (d/'schema.json').write_text(json.dumps(spec))
        X,y,g,s,a,info,tr,te=r.load(d/'data.csv',d/'schema.json')
        assert not set(g.iloc[tr])&set(g.iloc[te]); assert len(tr)+len(te)==len(df)
        for method in ['mi','l1','rfe','rf','permutation']:
            sel=r.Selector(s,method,2).fit(X.iloc[tr],y.iloc[tr],groups=g.iloc[tr]); assert len(sel.selected_)==2
        for b in ['B0','B1','B2','B3']:
            c=dict(preprocessing=b,engineering='D3',selection='all',model='LR')
            pipe=r.pipeline(s,c,X).fit(X.iloc[tr],y.iloc[tr]); assert pipe.predict_proba(X.iloc[te]).shape==(len(te),2)
        args=Namespace(data=str(d/'data.csv'),schema=str(d/'schema.json'),output=str(d/'run'),folds=3,hours=.1,trials=0,smoke=True,unlock_final=True)
        r.train(args)
        assert (d/'run/model.joblib').exists()
        args.unlock_final=False
        try: r.final(args)
        except PermissionError: pass
        else: raise AssertionError('Final Test must remain locked by default')
        assert not (d/'run/06_Final_Evaluation/FINAL_EVALUATION_STARTED').exists()
        args.unlock_final=True
        try: r.final(args)
        except ValueError as e: assert 'Smoke' in str(e)
        else: raise AssertionError('Synthetic final research results must be forbidden')
        spec['features']['y']=spec['features']['cat']; (d/'bad.json').write_text(json.dumps(spec))
        try:r.load(d/'data.csv',d/'bad.json')
        except ValueError:pass
        else:raise AssertionError('Target leakage accepted')
        if '--full' in sys.argv:
            args.output=str(d/'full_run'); args.smoke=False; args.trials=1
            r.train(args)
            failures=json.loads((d/'full_run/failures.json').read_text())
            assert not failures, failures
            r.final(args)
            scores=pd.read_csv(d/'full_run/06_Final_Evaluation/final_test_results.csv')
            assert len(scores)==2 and scores.accuracy.between(0,1).all()
            ci=json.loads((d/'full_run/06_Final_Evaluation/paired_accuracy_ci.json').read_text())
            assert ci['ci95'][0]<=ci['accuracy_difference']<=ci['ci95'][1]
            try: r.final(args)
            except FileExistsError: pass
            else: raise AssertionError('Repeated final test accepted')
            print('PASS: full synthetic sweep, all six models, Optuna, paired bootstrap, final one-time lock')
        print('PASS: selectors, preprocessing, grouped split, training artifacts, synthetic final guard, target guard')
if __name__=='__main__': main()
