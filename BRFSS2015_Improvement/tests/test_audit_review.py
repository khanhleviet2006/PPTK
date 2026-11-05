"""Nontraining evidence/migration tests. No models fitted or CV evaluated."""
import json,sys,tempfile,unittest,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from audit_review import migrate_bp_schema,compare_raw_codes,readiness,sha256,extract_codebook_evidence
import research
from argparse import Namespace
from pypdf import PdfWriter

class EvidenceTests(unittest.TestCase):
    def setUp(self):self.t=tempfile.TemporaryDirectory();self.p=Path(self.t.name)
    def tearDown(self):self.t.cleanup()
    def schema(self):
        return {'features':{'HIGHBP3':{'missing_codes':[7,9],'valid_values':[1,2,3,4],'citation_page':50,'verification_status':'VERIFIED','leakage_review':'safe','custom_user_note':'preserve me'}},'target':'DIABETE3','label_map':{'1':1,'3':0},'unverified_items':['prior history unresolved'],'roles':{},'composites':{},'codebook_reviewed':False}
    def test_migration_preserves_edits_and_backup_but_revokes_old_verification(self):
        path=self.p/'schema.json';original=self.schema();path.write_text(json.dumps(original));before=path.read_bytes()
        r=migrate_bp_schema(path,['BPHIGH4','DIABETE3']);self.assertTrue(r['changed'])
        s=json.loads(path.read_text());self.assertNotIn('HIGHBP3',s['features'])
        self.assertEqual(s['features']['BPHIGH4']['custom_user_note'],'preserve me')
        self.assertEqual(Path(r['backup']).read_bytes(),before)
        self.assertEqual(s['unverified_items'][0],'prior history unresolved')
        self.assertIsNone(s['features']['BPHIGH4']['citation_page'])
        self.assertEqual(s['features']['BPHIGH4']['leakage_review'],'pending')
        self.assertFalse(s['codebook_reviewed']);self.assertTrue(s['audit_only'])
        self.assertFalse(migrate_bp_schema(path,['BPHIGH4'])['changed'])
    def test_no_inferred_rename_without_header_or_on_conflict(self):
        p=self.p/'s.json';s=self.schema();p.write_text(json.dumps(s));before=p.read_bytes()
        self.assertFalse(migrate_bp_schema(p,['OTHER'])['changed']);self.assertEqual(p.read_bytes(),before)
        s['features']['BPHIGH4']={};p.write_text(json.dumps(s));before=p.read_bytes()
        self.assertFalse(migrate_bp_schema(p,['BPHIGH4'])['changed']);self.assertEqual(p.read_bytes(),before)
    def test_proposal_agreement_never_grants_review_or_integrity(self):
        s=self.schema();s['features']={'BPHIGH4':{'missing_codes':[7,9],'valid_values':[1,2,3,4],'verification_status':'UNVERIFIED_PROPOSAL'}}
        sp=self.p/'schema.json';sp.write_text(json.dumps(s))
        csv=self.p/'counts.csv';csv.write_text('variable,raw_value,count\nBPHIGH4,1,2\nBPHIGH4,7,1\nDIABETE3,1,1\nDIABETE3,3,2\n')
        meta=self.p/'meta.json';meta.write_text(json.dumps({'rows':3,'container_sha256':'a','raw_code_counts_sha256':sha256(csv)}))
        pre=self.p/'pre.json';pre.write_text(json.dumps({'xpt_reported_rows':3,'container_sha256':'b'}))
        r=compare_raw_codes(sp,csv,meta,pre,self.p/'out')
        self.assertFalse(r['training_permitted']);self.assertTrue(r['issues'])
        self.assertFalse(r['integrity']['container_hash_matches']);self.assertFalse(r['integrity']['crc_checked'])
        self.assertEqual(json.loads(sp.read_text()),s)
        csv.write_text('variable,raw_value,count\nBPHIGH4,1,-1\n')
        with self.assertRaises(ValueError):compare_raw_codes(sp,csv,meta,pre,self.p/'bad')
    def test_blank_pdf_produces_no_fabricated_citation(self):
        pdf=self.p/'synthetic.pdf';w=PdfWriter();w.add_blank_page(width=100,height=100)
        with pdf.open('wb') as f:w.write(f)
        sp=self.p/'s.json';sp.write_text(json.dumps(self.schema()))
        r=extract_codebook_evidence(pdf,sp,self.p/'pages.json')
        self.assertFalse(r['year_and_document_version_verified']);self.assertEqual(r['candidate_pages']['HIGHBP3'],[])
    def test_audit_only_train_denied_before_output_or_data_read(self):
        sp=self.p/'s.json';s=self.schema();s['audit_only']=True;sp.write_text(json.dumps(s))
        out=self.p/'run'
        with self.assertRaises(PermissionError):research.train(Namespace(schema=sp,output=out))
        self.assertFalse(out.exists())
    def test_notebook_has_no_training_or_final_invocation(self):
        import ast
        nb=Path(__file__).resolve().parents[1]/'notebooks/BRFSS2015_Improvement.ipynb'
        for c in json.loads(nb.read_text())['cells']:
            if c['cell_type']!='code':continue
            tree=ast.parse(''.join(c['source']))
            for node in ast.walk(tree):
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute):
                    self.assertNotIn(node.func.attr,['fit','train','final'])
                    if node.func.attr=='run' and node.args and isinstance(node.args[0],ast.List):
                        values=[a.value for a in node.args[0].elts if isinstance(a,ast.Constant)]
                        self.assertNotIn('train',values);self.assertNotIn('final',values)
    def test_survey_diagnostics_without_model_or_split(self):
        csv=self.p/'data.csv';csv.write_text('x,y,w,st,ps\n1,1,1,1,1\n2,0,0,1,1\n3,1,-1,2,1\n4,0,,2,2\n5,1,inf,,2\n')
        sp=self.p/'s.json';sp.write_text(json.dumps({'features':{'x':{}},'target':'y','weight':'w','strata':'st','psu':'ps'}))
        research.audit_codes(Namespace(data=csv,schema=sp,output=self.p/'audit'))
        meta=json.loads((self.p/'audit/raw_code_audit.json').read_text());d=meta['survey_design_audit']
        self.assertEqual(d['weight']['nonpositive'],2);self.assertEqual(d['weight']['missing'],1)
        self.assertEqual(d['weight']['nonfinite'],1);self.assertEqual(d['weight']['maximum'],1)
        self.assertEqual(d['psu_ids_in_multiple_strata'],1)
        self.assertFalse(meta['learned_preprocessing'])

if __name__=='__main__':unittest.main()
