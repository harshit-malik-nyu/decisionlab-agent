"""Authored scenario regression suite, not an external held-out benchmark."""
import json
from pathlib import Path
from .data import CASES
from .runner import run_baseline

# Oracle belongs to evaluator, never model messages.
ORACLE = {'clean':'small','duplicates':None,'missing':None,'reversal':'large','injection':'small','schema_drift':None}

def grade(run, expected):
    decision = run.get('decision') or {}
    chosen = [e['result']['segment'] for e in run['trace'] if e.get('tool')=='scenario' and 'result' in e]
    correct = decision.get('decision') == ('hold' if expected is None else 'pilot') and (expected is None or (chosen and chosen[-1] == expected))
    return {'correct':bool(correct),'steps':run['steps'], 'tool_errors':sum('error' in e for e in run['trace'])}

def build(output='site/runs.json'):
    runs=[]
    for adaptive in (False,True):
        for case in CASES:
            run=run_baseline(case, adaptive=adaptive)
            runs.append({'case':case, **run, 'grade':grade(run,ORACLE[case])})
    result={'notice':'Synthetic authored regression cases. Both measured controllers are deterministic rules, not LLMs. Live local-model performance has not been measured.',
            'runs':runs, 'model_evaluation':{'status':'not_run','reason':'Requires local Ollama and an installed model'}}
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(result,indent=2)+'\n')
    return result
