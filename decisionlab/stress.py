"""Generated engine stress checks; no model inference or held-out AI claim."""
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
import random
import sqlite3
from pathlib import Path
from unittest.mock import patch
from .engine import Investigation

COLUMNS=['account_id','segment','period','retained','monthly_value','support_cost']
MUTATIONS=('duplicate','missing_outcome','incomplete_panel','segment_change','negative_value')

def fixture(seed):
    rng=random.Random(seed)
    rows=[]
    for segment in ('small','large'):
        n=rng.randint(8,100)
        value=rng.randint(10,2000)
        before=rng.randint(1,n-1)
        after=rng.randint(1,n-1)
        for i in range(n):
            account=len(rows)//2
            for period,retained_count in (('before',before),('after',after)):
                rows.append([account,segment,period,int(i<retained_count),value,rng.randint(0,500)])
    rng.shuffle(rows)
    return rows

def make_dataset(rows):
    db=sqlite3.connect(':memory:')
    db.execute('CREATE TABLE observations ('+','.join(COLUMNS)+')')
    db.executemany('INSERT INTO observations VALUES (?,?,?,?,?,?)',rows)
    db.commit()
    digest=hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()
    return db,digest,'Synthetic generated stress fixture. No causal claims.'

def check(seed,mutation=None):
    rows=fixture(seed)
    if mutation=='duplicate':rows.append(rows[0][:])
    elif mutation=='missing_outcome':rows[0][3]=None
    elif mutation=='incomplete_panel':rows.pop()
    elif mutation=='segment_change':rows[0][1]='large' if rows[0][1]=='small' else 'small'
    elif mutation=='negative_value':rows[0][4]=-1
    with patch('decisionlab.engine.dataset',side_effect=lambda *_:make_dataset(rows)):
        lab=Investigation()
    errors=[]
    try:
        comparison=lab.step('compare')['result']
        if mutation:
            if comparison.get('valid') is not False:errors.append('Invalid data accepted')
        else:
            if not comparison.get('valid'):errors.append('Valid data rejected')
            else:
                # Independent Python arithmetic; no SQL or engine helpers in oracle.
                for segment in ('small','large'):
                    before=[r for r in rows if r[1]==segment and r[2]=='before']
                    after=[r for r in rows if r[1]==segment and r[2]=='after']
                    expected=round(100*(sum(r[3] for r in after)/len(after)-sum(r[3] for r in before)/len(before)),8)
                    if comparison['segments'][segment]['change_pp']!=expected:errors.append('Retention delta mismatch')
                    lift=.01;cost=100
                    scenario=lab.step('scenario',{'segment':segment,'lift':lift,'cost':cost})
                    expected_net=float((Decimal(sum(r[4] for r in after))*Decimal('0.01')*Decimal('0.75')*6-Decimal(cost)).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP))
                    if scenario.get('result',{}).get('net_scenario')!=expected_net:errors.append('Economics mismatch')
        return {'seed':seed,'mutation':mutation or 'none','data_sha256':lab.data_hash,'passed':not errors,'errors':errors}
    finally:lab.close()

def build(count=100):
    results=[check(seed,mutation) for seed in range(1000,1000+count) for mutation in (None,*MUTATIONS)]
    return {'scope':'Generated deterministic engine stress checks, not LLM evaluation or independently authored held-out tasks.',
            'generator':'Python random.Random; seeds 1000 onward; varied cohort sizes, retention rates, values, support costs and row order',
            'passed':sum(r['passed'] for r in results),'total':len(results),'results':results}

if __name__=='__main__':
    report=build()
    path=Path('evaluation/engine-stress.json');path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='results'}))
    raise SystemExit(0 if report['passed']==report['total'] else 1)
