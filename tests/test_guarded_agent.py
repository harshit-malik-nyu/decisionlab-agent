import json
import unittest
from decisionlab.runner import run_model
from decisionlab.verify import verify

class GuardedAgentTests(unittest.TestCase):
    def test_invalid_data_stops_inference(self):
        calls=[]
        def model(messages):
            calls.append(1)
            if len(calls)>1:raise AssertionError('Invalid data should stop model calls')
            return json.dumps({'tool':'compare','args':{}})
        for case in ('missing','duplicates','schema_drift'):
            calls.clear();r=run_model(case,model)
            self.assertEqual(r['decision_origin'],'runtime_data_quality_gate')
            self.assertEqual(r['decision']['decision'],'hold')
            self.assertEqual(len(calls),1)
            self.assertTrue(verify(r)['valid'])
    def test_valid_data_not_automatically_approved(self):
        def model(messages):
            if len(messages)==2:return json.dumps({'tool':'compare','args':{}})
            return json.dumps({'tool':'finish','args':{'decision':'hold','evidence_ids':['e1']}})
        r=run_model('clean',model)
        self.assertEqual(r['safety_actions'],[])
        self.assertEqual(r['decision']['decision'],'hold')
