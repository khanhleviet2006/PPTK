"""Audit-only subprocess regression tests; no ML imports/fitting or CV."""
import json,os,subprocess,sys,tempfile,unittest,contextlib,io
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from notebook_runtime import new_artifact,run_logged
ROOT=Path(__file__).resolve().parents[1]

class AuditRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.p=Path(self.tmp.name)
        self.capture=contextlib.redirect_stdout(io.StringIO());self.capture.__enter__()
    def tearDown(self):
        self.capture.__exit__(None,None,None);self.tmp.cleanup()
    def command(self,out,schema=None):
        if schema is None:
            schema=self.p/'schema.json';schema.write_text(json.dumps({'features':{'VALUE':{}},'target':'ID','codebook_reviewed':False}))
        return [sys.executable,str(ROOT/'src/audit_cli.py'),'inspect','--data',str(ROOT/'tests/fixtures/synthetic.xpt'),'--schema',str(schema),'--output',str(out)]
    def test_repeated_preflight_uses_unique_reports_preserves_previous(self):
        a=new_artifact(self.p,'preflight');b=new_artifact(self.p,'preflight');self.assertNotEqual(a,b)
        run_logged(self.command(a),self.p,'inspect');before=a.read_bytes()
        run_logged(self.command(b),self.p,'inspect');self.assertEqual(a.read_bytes(),before)
        self.assertEqual(json.loads(b.read_text())['xpt_reported_rows'],5)
    def test_original_exception_and_log_are_visible(self):
        s=self.p/'bad.json';s.write_text('{not JSON')
        with self.assertRaisesRegex(RuntimeError,'JSONDecodeError'):
            run_logged(self.command(self.p/'out.json',s),self.p,'inspect')
        logs=list(self.p.glob('inspect_*.log'));self.assertEqual(len(logs),1)
        self.assertIn('JSONDecodeError',logs[0].read_text())
    def test_existing_output_refusal_visible_and_no_overwrite(self):
        out=self.p/'existing.json';out.write_text('preserve')
        with self.assertRaisesRegex(RuntimeError,'FileExistsError'):run_logged(self.command(out),self.p,'inspect')
        self.assertEqual(out.read_text(),'preserve')
    def test_audit_cli_does_not_require_ml_imports(self):
        # A subprocess import guard proves inspect is isolated from ML packages.
        (self.p/'sitecustomize.py').write_text('''import sys
class Guard:
 def find_spec(self,fullname,path=None,target=None):
  if fullname.split('.')[0] in {'sklearn','scipy','joblib','catboost','lightgbm','xgboost'}:
   raise ImportError('Forbidden ML import: '+fullname)
sys.meta_path.insert(0,Guard())
''')
        settings=os.environ.copy();settings['PYTHONPATH']=str(self.p)
        out=self.p/'isolated.json'
        result=subprocess.run(self.command(out),env=settings,text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertTrue(out.is_file())

if __name__=='__main__':unittest.main()
