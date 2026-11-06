"""Authored scenario regression suite, not an external held-out benchmark."""
import json
from pathlib import Path
from .data import CASES
from .runner import run_baseline

# Oracle belongs to evaluator, never model messages.
ORACLE = {'clean':'small','duplicates':None,'missing':None,'reversal':'large','injection':'small','schema_drift':None}

def grade(run, expected):
    decision = run.get('decision') or {}
    refs=decision.get('evidence_ids',[])
    chosen = [e['result']['segment'] for e in run['trace'] if e.get('id') in refs and e.get('tool')=='scenario' and 'result' in e]
    invalid_evidence = [e for e in run['trace'] if e.get('id') in refs and e.get('tool') in ('quality','compare') and e.get('result',{}).get('valid') is False]
    correct = (decision.get('decision')=='hold' and bool(invalid_evidence)) if expected is None else (decision.get('decision')=='pilot' and chosen==[expected])
    return {'correct':bool(correct),'steps':run['steps'], 'tool_errors':sum('error' in e for e in run['trace'])}

def build(output='site/runs.json'):
    runs=[]
    for adaptive in (False,True):
        for case in CASES:
            run=run_baseline(case, adaptive=adaptive)
            runs.append({'case':case, **run, 'grade':grade(run,ORACLE[case])})
    evidence_path = Path(__file__).resolve().parents[1]/'evaluation/published-evidence.json'
    measured = json.loads(evidence_path.read_text()) if evidence_path.exists() else None
    if measured:
        for entry in measured['report']['results']:
            if 'run' in entry:
                runs.append({'case':entry['case'], **entry['run'], 'grade':grade(entry['run'],ORACLE[entry['case']])})
    result={'notice':'Synthetic authored cases. Rule policies and measured inference are distinct controllers. No held-out generalization claim.',
            'runs':runs, 'model_evaluation':measured['environment'] if measured else {'status':'not_run'}}
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(result,indent=2)+'\n')
    return result
