"""Visible subprocess logs and unique artifact names for repeatable Colab audits."""
from pathlib import Path
from datetime import datetime, timezone
import subprocess
import uuid


def new_artifact(root,prefix,suffix='.json'):
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    return root/f'{prefix}_{datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")}_{uuid.uuid4().hex[:12]}{suffix}'


def run_logged(command,root,label):
    """Stream merged stdout/stderr, preserve status, and include root error on failure."""
    log=new_artifact(root,label,'.log');tail=[]
    print('Diagnostic log:',log,flush=True)
    with log.open('x',encoding='utf8') as f:
        with subprocess.Popen([str(x) for x in command],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                              text=True,encoding='utf8',errors='replace',bufsize=1) as process:
            for line in process.stdout:
                print(line,end='',flush=True);f.write(line);f.flush()
                tail.append(line);tail=tail[-50:]
            code=process.wait()
    if code:
        signal_note=f'Process terminated by signal {-code}; inspect runtime memory/termination evidence.' if code<0 else ''
        raise RuntimeError(f'{label} failed (exit {code}). {signal_note}\nFull log: {log}\nLast output:\n'+''.join(tail))
    return log
