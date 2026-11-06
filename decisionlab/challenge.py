"""Prospective authored challenge evaluation; not independently held-out research."""
import json
import time
from pathlib import Path
from .data import CHALLENGE_CASES
from .engine import Investigation
from .runner import run_model
from .evaluate import fingerprint,save
from .verify import verify

EXPECTED={c:('pilot' if c=='tied_decline' else 'hold') for c in CHALLENGE_CASES}

def reference(case):
    lab=Investigation(case)
    try:
        c=lab.step('compare')
        result=c['result']
        refs=[c['id']]
        decision='hold'
        if result.get('valid') and result['segments'][result['priority']]['change_pp']<0:
            s=lab.step('scenario',{'segment':result['priority'],'lift':.05,'cost':2000})
            refs.append(s['id'])
            if s.get('result',{}).get('net_scenario',0)>0:decision='pilot'
        lab.step('finish',{'decision':decision,'evidence_ids':refs})
        out=lab.export();out['controller']='challenge_reference'
        return out
    finally:lab.close()

def grade(run):
    validation=verify(run)
    decision=run.get('decision') or {}
    refs=decision.get('evidence_ids',[])
    evidence=[r for r in run['trace'] if r.get('id') in refs]
    expected=EXPECTED[run['case']]
    supported=False
    if expected=='hold':
        for r in evidence:
            result=r.get('result',{})
            if r['tool'] in ('quality','compare') and result.get('valid') is False:supported=True
            if r['tool']=='compare' and result.get('valid') and all(g['change_pp']>=0 for g in result['segments'].values()):supported=True
    else:
        for r in evidence:
            if r['tool']=='scenario' and r['result']['net_scenario']>0 and r['result']['depends_on'] in refs:supported=True
    return {'correct':bool(validation['valid'] and decision.get('decision')==expected and supported),
            'expected':expected,'evidence_supported':supported,'replay_valid':validation['valid']}

def evaluate(model,path):
    path=Path(path)
    if path.exists():raise ValueError('Challenge evaluation refuses to overwrite prior results')
    report={'protocol':fingerprint(model,CHALLENGE_CASES),
            'scope':'Six prospectively authored challenge cases. Same frozen prompt/model configuration for every case. Not independently authored, not a held-out public benchmark. No tuning during the run.',
            'results':[],'complete':False,'correct':0}
    save(path,report)
    for case in CHALLENGE_CASES:
        started=time.monotonic()
        baseline=reference(case)
        entry={'case':case,'baseline':baseline,'baseline_grade':grade(baseline)}
        try:
            run=run_model(case,model)
            entry.update(status='completed',run=run,replay=verify(run),grade=grade(run))
        except (ValueError,KeyError,TypeError,OSError) as error:
            entry.update(status='failed',error_type=type(error).__name__,grade={'correct':False})
        entry['elapsed_seconds']=round(time.monotonic()-started,3)
        report['results'].append(entry)
        report['complete']=len(report['results'])==len(CHALLENGE_CASES)
        report['correct']=sum(r['grade']['correct'] for r in report['results'])
        save(path,report)
    return report
