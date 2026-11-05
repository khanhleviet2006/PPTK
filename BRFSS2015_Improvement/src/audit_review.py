"""Evidence checks only. Never fits, splits, selects models or grants VERIFIED."""
import copy
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd


def sha256(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024**2),b''): h.update(b)
    return h.hexdigest()


def migrate_bp_schema(path, columns):
    """Preserve Drive edits; require actual header evidence, back up before rename."""
    path=Path(path);original=path.read_bytes();s=json.loads(original)
    f=s['features']; columns=set(columns)
    if 'HIGHBP3' not in f: return {'changed':False,'reason':'No legacy HIGHBP3 entry.'}
    if 'BPHIGH4' not in columns or 'HIGHBP3' in columns:
        return {'changed':False,'reason':'Header does not establish the proposed rename; review required.'}
    if 'BPHIGH4' in f:
        return {'changed':False,'reason':'Both schema keys exist; resolve manually without discarding either.'}
    old=f['HIGHBP3'];new=copy.deepcopy(old)
    # Definitions/citations for another variable never count as BPHIGH4 verification.
    new.update(verification_status='UNVERIFIED_PROPOSAL',leakage_review='pending',citation_page=None,
               timing_assessment='Pending official definition and cross-sectional timing review.')
    s['features']={('BPHIGH4' if k=='HIGHBP3' else k):(new if k=='HIGHBP3' else v) for k,v in f.items()}
    s['composites']={name:{('BPHIGH4' if k=='HIGHBP3' else k):v for k,v in parts.items()} for name,parts in s.get('composites',{}).items()}
    s['roles']={k:('BPHIGH4' if v=='HIGHBP3' else v) for k,v in s.get('roles',{}).items()}
    s['codebook_reviewed']=False
    s['audit_only']=True
    item='BPHIGH4 replacement requires its own official codebook citation, domains, raw-code and timing review.'
    if item not in s.setdefault('unverified_items',[]):s['unverified_items'].append(item)
    s.setdefault('migration_history',[]).append({'from':'HIGHBP3','to':'BPHIGH4','basis':'Actual XPT header: BPHIGH4 present, HIGHBP3 absent','old_entry_preserved':old})
    backup=path.with_name(path.stem+'.before_bphigh4_'+hashlib.sha256(original).hexdigest()[:12]+'.json')
    if backup.exists():
        if backup.read_bytes()!=original: raise ValueError('Backup mismatch; refusing migration.')
    else:
        with backup.open('xb') as f:f.write(original)
    temporary=path.with_name(path.name+'.migrating')
    with temporary.open('x',encoding='utf8') as f:json.dump(s,f,indent=2)
    temporary.replace(path)
    return {'changed':True,'backup':str(backup),'codebook_reviewed':False}


def readiness(s):
    issues=list(s.get('unverified_items',[]))
    if not s.get('codebook_reviewed'):issues.append('Official codebook review not approved.')
    for n,v in list(s['features'].items())+[(s['target'],s.get('target_review',{})),('survey_design',s.get('design_review',{}))]:
        if v.get('verification_status')!='VERIFIED':issues.append(f'{n}: source verification incomplete.')
        if not isinstance(v.get('citation_page'),int) or v.get('citation_page',0)<1:issues.append(f'{n}: actual codebook PDF page missing.')
        if n in s['features'] and v.get('leakage_review')!='safe':issues.append(f'{n}: leakage/timing review pending.')
        if n in s['features'] and v.get('leakage_review')=='safe':
            timing=v.get('timing_assessment',{})
            if not isinstance(timing,dict) or timing.get('status')!='REVIEWED' or not timing.get('reason'):
                issues.append(f'{n}: safe flag lacks a documented reviewed timing assessment.')
    for role in ['weight','strata','psu']:
        item=s.get('design_review',{}).get('variables',{}).get(role,{})
        if item.get('column')!=s.get(role) or item.get('verification_status')!='VERIFIED' or not isinstance(item.get('citation_page'),int) or item.get('citation_page',0)<1:
            issues.append(f'{role}: individual official definition/page verification missing.')
    if not s.get('codebook_access',{}).get('sha256'):issues.append('Official document SHA256 missing.')
    if s.get('split_history',{}).get('status')!='REVIEWED':issues.append('Existing split/prior Test-use history unknown.')
    return sorted(set(issues))


def compare_raw_codes(schema_path, counts_path, metadata_path, preflight_path, output):
    """Compare every observed code with PROPOSED domains, never approve their meaning."""
    s=json.loads(Path(schema_path).read_text());counts=pd.read_csv(counts_path,keep_default_na=False)
    meta=json.loads(Path(metadata_path).read_text());pre=json.loads(Path(preflight_path).read_text())
    if not {'variable','raw_value','count'}<=set(counts): raise ValueError('Invalid raw-code CSV columns.')
    numeric=pd.to_numeric(counts['count'],errors='raise')
    if not np.isfinite(numeric).all() or (numeric<0).any() or (numeric%1!=0).any():raise ValueError('Counts must be finite nonnegative integers.')
    counts['count']=numeric
    if counts.duplicated(['variable','raw_value']).any(): raise ValueError('Duplicate variable/code rows in raw audit.')
    out=Path(output)
    if out.exists():raise FileExistsError('Review output already exists.')
    out.mkdir(parents=True)
    report=[]
    specs={**s['features'],**s.get('alternatives',{}),s['target']:{'raw_valid_values':[float(k) for k in s['label_map']], 'missing_codes':s.get('target_review',{}).get('missing_codes',[])}}
    for n,spec in specs.items():
        part=counts[counts.variable.eq(n)];unknown=[];missing=0
        for row in part.itertuples():
            if row.raw_value=='__SYSTEM_MISSING__':missing+=int(row.count);continue
            try: v=float(row.raw_value)
            except ValueError:unknown.append(row.raw_value);continue
            if not np.isfinite(v):unknown.append(row.raw_value);continue
            if v in spec.get('missing_codes',[]):missing+=int(row.count);continue
            if 'raw_valid_values' in spec:valid=v in spec['raw_valid_values']
            else:
                recode=spec.get('recode',{});v=recode.get(str(int(v)) if v.is_integer() else str(v),v)
                valid=v in spec['valid_values'] if 'valid_values' in spec else spec.get('valid_range',[-np.inf,np.inf])[0]<=v<=spec.get('valid_range',[-np.inf,np.inf])[1]
            if not valid:unknown.append(row.raw_value)
        total=int(part['count'].sum())
        report.append(dict(variable=n,present=not part.empty,total_count=total,
                           row_total_matches=bool(total==meta.get('rows') and not part.empty),
                           proposed_missing_count=missing,unexpected_codes=json.dumps(unknown),
                           source_verified=spec.get('verification_status')=='VERIFIED',citation_page=spec.get('citation_page'),
                           note='Agreement with a proposal does not verify CDC meaning.'))
    pd.DataFrame(report).to_csv(out/'variable_evidence_review.csv',index=False)
    provenance=pre.get('input_provenance',pre);rawprov=meta.get('input_provenance',{})
    container=pre.get('container_sha256');same=bool(container and container==meta.get('container_sha256'))
    member_match=bool(provenance.get('member_sha256') and provenance.get('member_sha256')==rawprov.get('member_sha256'))
    integrity=dict(container_hash_matches=same,member_hash_matches=member_match,
                   raw_counts_hash_matches=meta.get('raw_code_counts_sha256')==sha256(counts_path),
                   crc_checked=provenance.get('crc_checked') is True and rawprov.get('crc_checked') is True,
                   row_count_matches=pre.get('xpt_reported_rows')==meta.get('rows'),
                   authenticity_verified=False,note='Hashes/CRC identify consistency, not trusted CDC origin.')
    summary=dict(integrity=integrity,actual_rows=meta.get('rows'),
                 input_hashes={str(p):sha256(p) for p in [schema_path,counts_path,metadata_path,preflight_path]},
                 survey_design=meta.get('survey_design_audit',{'status':'Missing; regenerate audit with current code.'}),
                 issues=readiness(s),unexpected_codes_are_proposal_mismatches=True,
                 training_permitted=False,train_cv_run=False,final_test_run=False,
                 composites_enabled=list(s.get('composites',{})),split_history=s.get('split_history',{'status':'UNKNOWN'}))
    summary['composite_audit']={name:{'definition':parts,'unknown_predictors':sorted(set(parts)-set(s['features'])),
        'weighting':'Equal-count exploratory index only','missing_policy':'Missing if any component missing',
        'validated_clinical_scale':False,'review_status':'REQUIRES_EXPLICIT_DEFINITION_AND_TIMING_REVIEW'}
        for name,parts in s.get('composites',{}).items()}
    (out/'review_summary.json').write_text(json.dumps(summary,indent=2))
    return summary


def extract_codebook_evidence(pdf_path,schema_path,output):
    """Index actual PDF page text for manual review; never approve coded meanings."""
    from pypdf import PdfReader
    import re
    s=json.loads(Path(schema_path).read_text())
    names=set(s['features'])|set(s.get('alternatives',{}))|set(s.get('excluded_predictors',{}))|{s['target']}
    names|={s[k] for k in ['weight','strata','psu'] if s.get(k)}
    pages={n:[] for n in sorted(names)}
    for number,page in enumerate(PdfReader(pdf_path).pages,1):
        text=page.extract_text() or ''
        for n in pages:
            if re.search(r'(?<![A-Za-z0-9_])'+re.escape(n)+r'(?![A-Za-z0-9_])',text):
                pages[n].append({'pdf_page_1based':number,'text':text})
    result={'document_sha256':sha256(pdf_path),'candidate_pages':pages,
            'verification_status':'TEXT_LOCATED_ONLY_NOT_SEMANTICALLY_REVIEWED',
            'year_and_document_version_verified':False}
    with Path(output).open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
    return result
