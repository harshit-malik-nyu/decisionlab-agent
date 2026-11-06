"""Re-execute recorded tool calls; rehashed fabricated results still fail."""
import argparse
import json
from pathlib import Path
from .engine import Investigation

def verify(run):
    if run.get('schema_version') != 2:
        return {'valid':False,'errors':['Unsupported trace version; regenerate with the current engine.']}
    lab=Investigation(run['case'],run['seed'],run['max_steps'])
    errors=[]
    try:
        if run['data_sha256']!=lab.data_hash: errors.append('Dataset fingerprint mismatch')
        for i,record in enumerate(run['trace']):
            if lab.done:
                errors.append('Trace continues after closure');break
            actual=lab.step(record['tool'],record['args'])
            if actual!=record:errors.append('Re-execution mismatch at step '+str(i+1))
        if not lab.done and len(lab.trace)>=lab.max_steps:lab.step('schema')
        if lab.decision!=run['decision']:errors.append('Final decision mismatch')
        if len(run['trace'])!=run['steps']:errors.append('Step count mismatch')
        if lab.done!=run['complete']:errors.append('Completion mismatch')
        return {'valid':not errors,'errors':errors}
    finally:lab.close()

def main():
    p=argparse.ArgumentParser();p.add_argument('trace');a=p.parse_args()
    try:result=verify(json.loads(Path(a.trace).read_text()))
    except (ValueError,KeyError,TypeError,OSError) as error:result={'valid':False,'errors':[str(error)]}
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['valid'] else 1)
if __name__=='__main__':main()
