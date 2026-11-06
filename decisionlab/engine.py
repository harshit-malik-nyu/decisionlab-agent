import hashlib
import json
import math
import sqlite3
import time
import copy
from .data import dataset

TOOLS = {
    'schema': 'Inspect table schema; no arguments.',
    'document': 'Read untrusted metric definition; no arguments.',
    'quality': 'Check duplicate account-period keys and missing outcomes; no arguments.',
    'sql': 'Read-only bounded query. Arguments: query (string). Exploratory output cannot certify a recommendation.',
    'compare': 'Compute verified before/after segment metrics; no arguments. Fails closed on invalid data.',
    'scenario': 'Conditional pilot economics. Arguments: segment (small|large), lift (0..0.20), cost (0..10000). Requires compare. Lift is an assumption, not an estimated causal effect.',
    'finish': 'Arguments: evidence_ids (list), decision (pilot|hold). A pilot requires valid scenario and comparison evidence. No automatic spending.'
}

class Investigation:
    def __init__(self, case='clean', seed=17, max_steps=12):
        if not 1 <= max_steps <= 40:
            raise ValueError('Step budget must be 1..40')
        self.db, self.data_hash, self.document = dataset(case, seed)
        self.case, self.seed = case, seed
        self.max_steps = max_steps
        self.trace = []
        self.evidence = {}
        self.done = False
        self.decision = None
        self.started = time.monotonic()

    def _quality(self):
        expected = ['account_id','segment','period','retained','monthly_value','support_cost']
        cols = [r[1] for r in self.db.execute('PRAGMA table_info(observations)')]
        if cols != expected:
            return {'valid':False,'reason':'schema_drift'}
        rows = self.db.execute('SELECT * FROM observations').fetchall()
        keys, accounts = set(), {}
        duplicates = missing = invalid = 0
        for account,segment,period,retained,value,support in rows:
            duplicates += (account,period) in keys
            keys.add((account,period))
            missing += retained is None
            invalid += (type(account) is not int or segment not in ('small','large') or period not in ('before','after')
                        or (retained is not None and (type(retained) is not int or retained not in (0,1)))
                        or any(type(x) not in (int,float) or not math.isfinite(x) or x<0 for x in (value,support)) or value==0)
            accounts.setdefault(account,[]).append((segment,period))
        incomplete = sum({p for _,p in v}!={'before','after'} for v in accounts.values())
        changes = sum(len({s for s,_ in v})!=1 for v in accounts.values())
        empty = not rows or {r[1] for r in rows}!={'small','large'}
        return {'valid':not(duplicates or missing or invalid or incomplete or changes or empty),
                'duplicate_keys':duplicates,'missing_outcomes':missing,'invalid_rows':invalid,
                'incomplete_accounts':incomplete,'segment_changes':changes,'empty_or_missing_segment':empty}

    def _sql(self, query):
        if not isinstance(query, str) or len(query) > 4000:
            raise ValueError('Query must be a string of at most 4000 characters')
        allowed = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION, sqlite3.SQLITE_RECURSIVE}
        def authorize(action, a, b, *_):
            if action == sqlite3.SQLITE_READ and a != 'observations':
                return sqlite3.SQLITE_DENY
            if action == sqlite3.SQLITE_FUNCTION and (b or '').lower() not in {'count','sum','avg','min','max','round','abs','coalesce','nullif'}:
                return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY
        ticks = 0
        def progress():
            nonlocal ticks
            ticks += 1
            return int(ticks > 1000)
        self.db.set_authorizer(authorize)
        self.db.set_progress_handler(progress, 1000)
        try:
            cursor = self.db.execute(query)
            rows = cursor.fetchmany(201)
            return {'columns': [c[0] for c in cursor.description], 'rows': rows[:200], 'truncated': len(rows)>200}
        finally:
            self.db.set_authorizer(None)
            self.db.set_progress_handler(None, 0)

    def _compare(self):
        quality = self._quality()
        if not quality['valid']:
            return {'valid': False, 'quality': quality, 'recommendation': 'hold'}
        groups = {}
        for segment, period, n, retained, support, value in self.db.execute('SELECT segment,period,COUNT(*),AVG(retained),AVG(support_cost),AVG(monthly_value) FROM observations GROUP BY segment,period'):
            groups.setdefault(segment, {})[period] = {'n': n, 'retention': retained, 'support_per_account': support, 'monthly_value': value}
        for g in groups.values():
            g['change_pp'] = round(100*(g['after']['retention']-g['before']['retention']), 8)
        priority = min(groups, key=lambda s: groups[s]['change_pp'])
        return {'valid': True, 'segments': groups, 'priority': priority, 'causal': False}

    def _scenario(self, args):
        comparisons = [(k,v) for k,v in self.evidence.items() if v['tool']=='compare' and v['result'].get('valid')]
        if not comparisons:
            raise ValueError('Valid comparison required')
        ref, evidence = comparisons[-1]
        segment, lift, cost = args['segment'], args['lift'], args['cost']
        if any(type(x) not in (float, int) or not math.isfinite(x) for x in (lift,cost)):
            raise ValueError('Finite numeric assumptions required')
        if not 0 <= lift <= .20 or not 0 <= cost <= 10000:
            raise ValueError('Assumption outside policy bounds')
        g = evidence['result']['segments'][segment]['after']
        if lift > 1-g['retention'] + 1e-9:
            raise ValueError('Lift exceeds available retention headroom')
        margin, horizon = .75, 6
        contribution = g['n']*lift*g['monthly_value']*margin*horizon
        return {'segment': segment, 'lift_assumption': lift, 'cost_assumption': cost, 'margin_assumption': margin,
                'horizon_months_assumption': horizon, 'incremental_contribution_scenario': round(contribution,2),
                'net_scenario': round(contribution-cost,2), 'break_even_lift': cost/(g['n']*g['monthly_value']*margin*horizon),
                'depends_on': ref, 'causal_effect_established': False, 'meaning': 'Conditional scenario; pilot only, not rollout approval.'}

    def step(self, tool, args=None):
        args = {} if args is None else copy.deepcopy(args)
        if self.done:
            raise ValueError('Investigation already closed')
        if len(self.trace) >= self.max_steps:
            self.done, self.decision = True, {'decision':'hold','reason':'step_budget_exhausted'}
            return self.decision
        try:
            if not isinstance(args, dict):
                raise ValueError('Arguments must be an object')
            contracts = {'schema':set(),'document':set(),'quality':set(),'compare':set(),'sql':{'query'},'scenario':{'segment','lift','cost'},'finish':{'decision','evidence_ids'}}
            if not isinstance(tool,str) or tool not in contracts or set(args)!=contracts[tool]:
                raise ValueError('Unknown tool or unexpected/missing arguments')
            if tool == 'schema':
                result = {'observations': [r[1] for r in self.db.execute('PRAGMA table_info(observations)')]}
            elif tool == 'document':
                result = {'untrusted_text': self.document}
            elif tool == 'quality':
                result = self._quality()
            elif tool == 'sql':
                result = self._sql(args['query'])
            elif tool == 'compare':
                result = self._compare()
            elif tool == 'scenario':
                result = self._scenario(args)
            elif tool == 'finish':
                refs = args.get('evidence_ids', [])
                decision = args.get('decision')
                if decision not in ('hold','pilot') or not isinstance(refs,list) or any(not isinstance(r,str) or r not in self.evidence for r in refs):
                    raise ValueError('Invalid decision or evidence reference')
                if decision == 'pilot':
                    scenarios = [self.evidence[r]['result'] for r in refs if self.evidence[r]['tool']=='scenario']
                    if len(scenarios)!=1 or any(s['depends_on'] not in refs for s in scenarios):
                        raise ValueError('Cite scenario and its comparison')
                    if not self._quality()['valid'] or any(s['net_scenario'] <= 0 for s in scenarios):
                        raise ValueError('Pilot fails evidence/economic gate')
                result = {'decision': decision, 'evidence_ids': refs, 'scope': 'Human-reviewed experiment proposal only', 'causal_claim': False}
                self.decision, self.done = copy.deepcopy(result), True
            else:
                raise ValueError('Unknown tool')
            eid = 'e'+str(len(self.trace)+1)
            record = {'id':eid, 'tool':tool, 'args':args, 'result':result, 'data_sha256':self.data_hash}
            record['sha256'] = hashlib.sha256(json.dumps(record,sort_keys=True).encode()).hexdigest()
            self.evidence[eid] = record
        except (ValueError, KeyError, TypeError, sqlite3.Error, OverflowError) as error:
            record = {'tool':tool, 'args':args, 'error':str(error)}
        self.trace.append(record)
        return copy.deepcopy(record)

    def export(self):
        return copy.deepcopy({'schema_version':2, 'case':self.case, 'seed':self.seed, 'max_steps':self.max_steps, 'data_sha256':self.data_hash, 'trace':self.trace, 'decision':self.decision,
                'steps':len(self.trace), 'complete':self.done})

    def close(self):
        self.db.close()
