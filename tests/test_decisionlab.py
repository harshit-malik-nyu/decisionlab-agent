import hashlib
import json
import unittest
from decisionlab.engine import Investigation
from decisionlab.runner import run_baseline, run_model
from decisionlab.benchmark import grade, ORACLE

class DecisionLabTests(unittest.TestCase):
    def setUp(self):
        self.lab=Investigation()
    def tearDown(self):
        self.lab.close()
    def test_read_only(self):
        for query in ['DELETE FROM observations','DROP TABLE observations',"ATTACH DATABASE ':memory:' AS evil",'PRAGMA writable_schema=ON',"SELECT load_extension('evil')",'SELECT * FROM sqlite_master']:
            with self.subTest(query=query):
                self.assertIn('error',self.lab.step('sql',{'query':query}))
        self.assertTrue(self.lab._quality()['valid'])
    def test_large_result_truncated(self):
        r=self.lab.step('sql',{'query':'SELECT * FROM observations'})['result']
        self.assertTrue(r['truncated']); self.assertEqual(len(r['rows']),200)
    def test_expensive_query_interrupted(self):
        self.assertIn('error',self.lab.step('sql',{'query':'SELECT COUNT(*) FROM observations a, observations b, observations c, observations d'}))
    def test_missing_gate(self):
        for case in ('missing','duplicates','schema_drift'):
            r=run_baseline(case)
            self.assertEqual(r['decision']['decision'],'hold')
    def test_reference_forgery(self):
        self.assertIn('error',self.lab.step('finish',{'decision':'pilot','evidence_ids':['e999']}))
    def test_no_evidence_pilot(self):
        self.assertIn('error',self.lab.step('finish',{'decision':'pilot','evidence_ids':[]}))
    def test_lineage_required(self):
        self.lab.step('compare')
        s=self.lab.step('scenario',{'segment':'small','lift':.05,'cost':2000})
        self.assertIn('error',self.lab.step('finish',{'decision':'pilot','evidence_ids':[s['id']]}))
    def test_economics(self):
        self.lab.step('compare')
        s=self.lab.step('scenario',{'segment':'small','lift':.05,'cost':2000})['result']
        self.assertEqual(s['incremental_contribution_scenario'],3600)
        self.assertEqual(s['net_scenario'],1600)
        self.assertAlmostEqual(s['break_even_lift'],2000/72000)
    def test_bounds(self):
        self.lab.step('compare')
        for lift in (float('nan'),float('inf'),-.01,.21,True):
            self.assertIn('error',self.lab.step('scenario',{'segment':'small','lift':lift,'cost':2000}))
    def test_revision_changes_priority(self):
        a=run_baseline('clean'); b=run_baseline('reversal')
        self.assertNotEqual(a['data_sha256'],b['data_sha256'])
        def segment(r): return next(x['result']['segment'] for x in r['trace'] if x['tool']=='scenario')
        self.assertEqual(segment(a),'small'); self.assertEqual(segment(b),'large')
    def test_hash_integrity(self):
        for e in run_baseline()['trace']:
            copy=dict(e); digest=copy.pop('sha256')
            self.assertEqual(hashlib.sha256(json.dumps(copy,sort_keys=True).encode()).hexdigest(),digest)
    def test_reproducibility(self):
        self.assertEqual(run_baseline(),run_baseline())
    def test_injection_is_data(self):
        run=run_baseline('injection')
        self.assertTrue(grade(run,'small')['correct'])
        self.assertTrue(all(e['tool']!='sql' for e in run['trace']))
    def test_model_adapts_to_observation(self):
        def model(messages):
            if len(messages)==2: return json.dumps({'tool':'quality','args':{}})
            observation=json.loads(messages[-1]['content'])['tool_observation']
            self.assertFalse(observation['result']['valid'])
            return json.dumps({'tool':'finish','args':{'decision':'hold','evidence_ids':[observation['id']]}})
        self.assertEqual(run_model('missing',model)['decision']['decision'],'hold')
    def test_bad_model_bounded(self):
        result=run_model('clean',lambda _: 'not json',max_steps=3)
        self.assertEqual(result['steps'],3)
        self.assertEqual(result['decision']['reason'],'step_budget_exhausted')
    def test_oracles(self):
        for case,expected in ORACLE.items():
            self.assertTrue(grade(run_baseline(case),expected)['correct'])
        self.assertFalse(grade(run_baseline('reversal',adaptive=False),'large')['correct'])
    def test_closed(self):
        self.lab.step('finish',{'decision':'hold','evidence_ids':[]})
        with self.assertRaises(ValueError): self.lab.step('schema')

if __name__=='__main__': unittest.main()
