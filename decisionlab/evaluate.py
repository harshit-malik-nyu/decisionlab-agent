"""Checkpointed authored-case evaluation, never a held-out benchmark claim."""
import argparse
import hashlib
import json
import os
import platform
import time
from pathlib import Path
from .data import CASES
from .benchmark import ORACLE,grade
from .runner import LocalModel,run_model,SYSTEM,QUESTION
from .verify import verify

def fingerprint(model,cases):
    root=Path(__file__).parent
    return {'model_tag':model.model,'cases':list(cases),'seed':17,'max_steps':12,
            'python':platform.python_version(),
            'prompt_sha256':hashlib.sha256((SYSTEM+QUESTION).encode()).hexdigest(),
            'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.glob('*.py'))}}

def save(path,report):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_name(path.name+'.tmp')
    with temporary.open('w') as f:
        json.dump(report,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(temporary,path)

def evaluate(model,path,cases=CASES):
    cases=tuple(cases)
    if not cases or len(set(cases))!=len(cases) or any(c not in CASES for c in cases):
        raise ValueError('Choose unique known cases')
    protocol=fingerprint(model,cases)
    path=Path(path)
    if path.exists():
        report=json.loads(path.read_text())
        if report['protocol']!=protocol:raise ValueError('Checkpoint protocol changed; use a new output file')
        completed=[r['case'] for r in report['results']]
        if completed!=list(cases[:len(completed)]):raise ValueError('Invalid checkpoint case order')
        for entry in report['results']:
            if entry['status']=='completed' and not verify(entry['run'])['valid']:
                raise ValueError('Checkpoint replay validation failed')
    else:
        report={'protocol':protocol,'scope':'Authored development cases; not generalization evidence. Model tag is not an immutable model digest.',
                'results':[],'complete':False}
        save(path,report)
    for case in cases[len(report['results']):]:
        started=time.monotonic()
        try:
            run=run_model(case,model)
            validation=verify(run)
            entry={'case':case,'status':'completed','run':run,'replay':validation,'grade':grade(run,ORACLE[case])}
            if not validation['valid']:entry['grade']['correct']=False
        except (OSError,ValueError,KeyError,TypeError) as error:
            entry={'case':case,'status':'failed','error_type':type(error).__name__,'grade':{'correct':False}}
        entry['elapsed_seconds']=round(time.monotonic()-started,3)
        report['results'].append(entry)
        report['complete']=len(report['results'])==len(cases)
        report['correct']=sum(e['grade']['correct'] for e in report['results'])
        save(path,report)
    return report

def main():
    p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--output',required=True)
    p.add_argument('--cases',nargs='+',choices=CASES,default=list(CASES));a=p.parse_args()
    result=evaluate(LocalModel(a.model),a.output,a.cases)
    print(json.dumps({'correct':result['correct'],'total':len(result['results']),'complete':result['complete']}))
if __name__=='__main__':main()
