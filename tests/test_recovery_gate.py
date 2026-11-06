import unittest
from decisionlab.engine import Investigation

class RecoveryGateTests(unittest.TestCase):
    def attempt(self,sql=None,segment='small',cost=100):
        lab=Investigation()
        try:
            if sql:lab.db.execute(sql)
            c=lab.step('compare')
            s=lab.step('scenario',{'segment':segment,'lift':.05,'cost':cost})
            self.assertIn('result',s,'Exploratory economics remain permitted')
            return lab.step('finish',{'decision':'pilot','evidence_ids':[c['id'],s['id']]})
        finally:lab.close()
    def test_improvement_is_not_recovery_evidence(self):
        self.assertIn('error',self.attempt("UPDATE observations SET retained=0 WHERE period='before'"))
    def test_stable_cohort_rejected(self):
        self.assertIn('error',self.attempt(segment='large'))
    def test_declining_cohort_accepted(self):
        self.assertEqual(self.attempt()['result']['decision'],'pilot')
    def test_decline_does_not_override_negative_economics(self):
        self.assertIn('error',self.attempt(cost=10000))
