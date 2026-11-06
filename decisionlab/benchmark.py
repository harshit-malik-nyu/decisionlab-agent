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
    evaluations=[]
    evidence_root=Path(__file__).resolve().parents[1]/'evaluation'
    for filename in ('qwen2.5-1.5b-evidence.json','qwen2.5-3b-evidence.json','qwen2.5-3b-guarded-evidence.json'):
        path=evidence_root/filename
        if not path.exists():
            raise ValueError('Missing published evaluation: '+filename)
        measured=json.loads(path.read_text())
        validate_evaluation(measured)
        group=filename.removesuffix('-evidence.json')
        evaluations.append({'id':group,'environment':measured['environment'],'protocol':measured['report']['protocol']})
        for entry in measured['report']['results']:
            run=entry['run']
            runs.append({**run,'evaluation_id':group,'elapsed_seconds':entry['elapsed_seconds'],
                         'grade':grade(run,ORACLE[entry['case']])})
    result={'notice':'Synthetic authored cases. Historical development runs, not a controlled ablation or held-out benchmark.',
            'runs':runs,'evaluations':evaluations}
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(result,indent=2)+'\n')
    return result


def validate_evaluation(evidence):
    """Fail publication on missing cases, stale scores or unreplayable evidence."""
    from .verify import verify
    report=evidence['report']
    entries=report['results']
    cases=[e['case'] for e in entries]
    if report.get('complete') is not True or len(cases)!=len(CASES) or set(cases)!=set(CASES):
        raise ValueError('Evaluation must contain each required case exactly once')
    correct=0
    for entry in entries:
        run=entry['run']
        if entry.get('status')!='completed' or run['case']!=entry['case']:
            raise ValueError('Case identity or completion mismatch')
        if not verify(run)['valid']:
            raise ValueError('Trace failed re-execution')
        actual=grade(run,ORACLE[entry['case']])
        if actual!=entry['grade']:
            raise ValueError('Stored grade differs from recomputed grade')
        correct+=actual['correct']
    if report['correct']!=correct:
        raise ValueError('Aggregate score mismatch')
