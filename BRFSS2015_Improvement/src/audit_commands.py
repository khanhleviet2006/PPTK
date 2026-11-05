"""Audit commands isolated from ML dependencies; no models or split operations."""
import json, hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from data_io import read_xpt, inspect_xpt
SEED=2026

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
