"""Run with unittest. Uses a tiny synthetic SAS V5 fixture, never BRFSS."""
import copy,json,sys,tempfile,unittest,zipfile,stat,struct
from pathlib import Path
from argparse import Namespace
from unittest.mock import patch
import pandas as pd
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import data_io
import research
ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/'tests/fixtures/synthetic.xpt'

class ZipInputTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
    def tearDown(self): self.tmp.cleanup()
    def archive(self,name='LLCP2015.XPT',payload=None):
        p=self.root/'test.zip'
        with zipfile.ZipFile(p,'w',compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr(name,FIXTURE.read_bytes() if payload is None else payload)
        return p
    def test_real_xpt_and_zip_decode_equally(self):
        p=self.archive('safe/LLCP2015.XPT')
        direct=research.read_data(FIXTURE); zipped=research.read_data(p)
        pd.testing.assert_frame_equal(direct,zipped)
        self.assertEqual(len(zipped),5)
        self.assertEqual(zipped.VALUE.iloc[0],12.5)
        self.assertTrue(pd.isna(zipped.VALUE.iloc[2]))
        self.assertEqual(zipped.LABEL.iloc[4],'epsilon')
        self.assertTrue(zipped.attrs['input_provenance']['crc_checked'])
        self.assertEqual(len(zipped.attrs['input_provenance']['member_sha256']),64)
        self.assertFalse((self.root/'safe').exists())
        sample,info=data_io.inspect_xpt(p,sample_rows=2)
        self.assertEqual(len(sample),2);self.assertEqual(info['xpt_reported_rows'],5)
        self.assertFalse(info['raw_domain_audit_complete'])
    def test_unsafe_ambiguous_and_symlink_refused(self):
        for name in ['../escape.XPT','/escape.XPT','dir\\escape.XPT','C:/escape.XPT']:
            with self.subTest(name=name),self.assertRaises(ValueError):research.read_data(self.archive(name))
        p=self.archive()
        with zipfile.ZipFile(p,'a') as z:z.writestr('second.xpt',FIXTURE.read_bytes())
        with self.assertRaises(ValueError):research.read_data(p)
        with zipfile.ZipFile(p,'w') as z:
            entry=zipfile.ZipInfo('link.xpt');entry.create_system=3;entry.external_attr=(stat.S_IFLNK|0o777)<<16
            z.writestr(entry,'/tmp/elsewhere')
        with self.assertRaises(ValueError):research.read_data(p)
        with zipfile.ZipFile(p,'w') as z:z.writestr('readme.txt','No dataset')
        with self.assertRaises(ValueError):research.read_data(p)
    def test_bounds_and_corruption(self):
        p=self.archive()
        with patch.object(data_io,'MAX_XPT_BYTES',100),self.assertRaises(ValueError):research.read_data(p)
        with patch.object(data_io,'MAX_RATIO',1),self.assertRaises(ValueError):research.read_data(p)
        with patch.object(data_io,'MAX_MEMBERS',0),self.assertRaises(ValueError):research.read_data(p)
        p=self.root/'badcrc.zip'
        with zipfile.ZipFile(p,'w',compression=zipfile.ZIP_STORED) as z:z.writestr('data.xpt',FIXTURE.read_bytes())
        raw=bytearray(p.read_bytes())
        name_len,extra_len=struct.unpack_from('<HH',raw,26)
        raw[30+name_len+extra_len+10]^=1;p.write_bytes(raw)
        with self.assertRaises(zipfile.BadZipFile):research.read_data(p)
    def test_temporary_handle_closed_even_on_parser_failure(self):
        p=self.archive(payload=b'not an XPT file')
        handles=[];original=data_io.tempfile.TemporaryFile
        def tracked(*args,**kwargs):
            h=original(*args,**kwargs);handles.append(h);return h
        with patch.object(data_io.tempfile,'TemporaryFile',tracked):
            with self.assertRaises(ValueError):research.read_data(p)
        self.assertTrue(handles and all(h.closed for h in handles))
    def test_unreviewed_schema_fails_before_data_io(self):
        schema=ROOT/'schema.reviewed.json'
        with patch.object(research,'read_data',side_effect=AssertionError('must not read data')):
            with self.assertRaisesRegex(ValueError,'codebook'):research.load('/does/not/exist.zip',schema)
        s=json.loads(schema.read_text());s['codebook_reviewed']=True
        path=self.root/'flipped.json';path.write_text(json.dumps(s))
        with self.assertRaisesRegex(ValueError,'unverified_items'):research.load('/does/not/exist.zip',path)
    def test_inspect_writes_metadata_without_scoring(self):
        p=self.archive();schema=self.root/'schema.json'
        schema.write_text(json.dumps({'features':{'VALUE':{}},'target':'ID','codebook_reviewed':False}))
        out=self.root/'preflight.json'
        research.inspect(Namespace(data=p,schema=schema,output=out))
        info=json.loads(out.read_text())
        self.assertTrue(info['final_test_locked']);self.assertEqual(info['missing_required_columns'],[])
        with self.assertRaises(FileExistsError):research.inspect(Namespace(data=p,schema=schema,output=out))
        audit=self.root/'raw_codes'
        research.audit_codes(Namespace(data=p,schema=schema,output=audit))
        counts=pd.read_csv(audit/'raw_code_counts.csv')
        self.assertEqual(counts.groupby('variable')['count'].sum().to_dict(),{'VALUE':5,'ID':5})
        self.assertFalse(json.loads((audit/'raw_code_audit.json').read_text())['source_verification_complete'])
        with self.assertRaises(FileExistsError):research.audit_codes(Namespace(data=p,schema=schema,output=audit))
    def test_day_recode_activity_recode_and_bmi_groups(self):
        # Synthetic coding test only: this does NOT validate the real codebook.
        s={'features':{'_BMI5':{'scale':.01}},'roles':{'bmi':'_BMI5','physical_days':'PHYSHLTH'}}
        frame=pd.DataFrame({'_BMI5':[1850,2500,3000,np.nan], 'PHYSHLTH':[0,1,30,np.nan]})
        out=research.Features(s,'B3').transform(frame)
        # Configured adult BMI boundaries are left-inclusive: BMI 25 is overweight, BMI 30 obese.
        self.assertEqual(out.eng_bmi_group.iloc[:3].tolist(),[1,2,3])
        self.assertEqual(out.eng_log_physical_days.iloc[0],0)
        self.assertTrue(pd.isna(out.eng_bmi_group.iloc[3]))
    def test_final_cli_locked_by_default(self):
        with self.assertRaises(PermissionError):research.final(Namespace(output='/not/a/run',data='unused'))

    def test_raw_code_validation_precedes_recode(self):
        frame=pd.DataFrame({'x':np.arange(100),'days':[88,1,77,99]*25,
                            'activity':[1,2,7,9]*25,'target':[1,3]*50})
        path=self.root/'synthetic.csv';frame.to_csv(path,index=False)
        common={'type':'continuous','missing_codes':[], 'leakage_review':'safe',
                'rationale':'Synthetic only','codebook_reference':'SYNTHETIC ONLY'}
        s={'task':'binary','codebook_reviewed':True,'codebook_source':'SYNTHETIC ONLY',
           'target':'target','label_map':{'1':1,'3':0},'features':{
             'x':dict(common,valid_range=[0,100]),
             'days':dict(common,missing_codes=[77,99],raw_valid_values=list(range(1,31))+[88],valid_range=[0,30],recode={'88':0}),
             'activity':dict(common,type='categorical',missing_codes=[7,9],raw_valid_values=[1,2],valid_values=[0,1],recode={'2':0})}}
        sp=self.root/'synthetic.json';sp.write_text(json.dumps(s))
        X,*_=research.load(path,sp)
        self.assertEqual(X.days.iloc[0],0);self.assertEqual(X.activity.iloc[1],0)
        self.assertTrue(X.days.iloc[2:].iloc[::4].isna().all())
        frame.loc[0,'days']=0;frame.to_csv(path,index=False)
        with self.assertRaisesRegex(ValueError,'raw codes'):research.load(path,sp)

if __name__=='__main__':unittest.main()
