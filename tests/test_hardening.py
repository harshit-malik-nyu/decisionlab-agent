import unittest
from decisionlab.engine import Investigation
from decisionlab.runner import run_model,run_baseline
from decisionlab.benchmark import grade

class HardeningTests(unittest.TestCase):
    def setUp(self): self.lab=Investigation()
    def tearDown(self): self.lab.close()
    def test_invalid_panels(self):
        for sql in ["DELETE FROM observations WHERE account_id=1 AND period='after'","UPDATE observations SET segment='large' WHERE account_id=20 AND period='after'","UPDATE observations SET retained=2 WHERE account_id=1","UPDATE observations SET monthly_value=-1 WHERE account_id=1","DELETE FROM observations"]:
            with self.subTest(sql=sql):
                lab=Investigation()
                try:
                    lab.db.execute(sql)
                    self.assertFalse(lab._quality()['valid'])
                    self.assertFalse(lab._compare()['valid'])
                finally:lab.close()
    def test_unknown_arguments(self):
        self.assertIn('error',self.lab.step('quality',{'ignore_missing':True}))
    def test_return_isolated(self):
        r=self.lab.step('compare');r['result']['priority']='forged'
        self.assertEqual(self.lab.evidence['e1']['result']['priority'],'small')
    def test_export_isolated(self):
        self.lab.step('quality');self.lab.export()['trace'][0]['result']['valid']=False
        self.assertTrue(self.lab.evidence['e1']['result']['valid'])
    def test_multiple_scenarios(self):
        c=self.lab.step('compare')
        a=self.lab.step('scenario',{'segment':'small','lift':.05,'cost':2000})
        b=self.lab.step('scenario',{'segment':'large','lift':.05,'cost':2000})
        self.assertIn('error',self.lab.step('finish',{'decision':'pilot','evidence_ids':[c['id'],a['id'],b['id']]}))
    def test_exhaustion_is_failure(self):
        self.assertFalse(grade(run_model('missing',lambda _: 'invalid',max_steps=2),None)['correct'])
    def test_only_cited_scenario_counts(self):
        r=run_baseline();r['trace'].append({'id':'uncited','tool':'scenario','result':{'segment':'large'}})
        self.assertTrue(grade(r,'small')['correct'])
