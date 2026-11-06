import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from decisionlab.runner import run_baseline,run_model
from decisionlab.verify import verify
from decisionlab.evaluate import evaluate

class ReplayEvaluationTests(unittest.TestCase):
    def test_replay_all_cases(self):
        for case in ('clean','duplicates','missing','reversal','injection','schema_drift'):
            self.assertTrue(verify(run_baseline(case))['valid'])
    def test_rehashed_fabrication(self):
        run=run_baseline();e=next(e for e in run['trace'] if e['tool']=='scenario')
        e['result']['net_scenario']=1000000;e.pop('sha256')
        e['sha256']=hashlib.sha256(json.dumps(e,sort_keys=True).encode()).hexdigest()
        self.assertFalse(verify(run)['valid'])
    def test_decision_tampering(self):
        r=run_baseline('missing');r['decision']['decision']='pilot'
        self.assertFalse(verify(r)['valid'])
    def test_budget_exhaustion_replays(self):
        self.assertTrue(verify(run_model('clean',lambda _: 'bad json',max_steps=2))['valid'])
    def test_checkpoint_survives_interrupt(self):
        class Model:
            model='test-double-not-inference'
            calls=0
            def __call__(self,messages):
                self.calls+=1
                if self.calls==1:raise OSError('unavailable')
                raise KeyboardInterrupt()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'report.json'
            with self.assertRaises(KeyboardInterrupt):evaluate(Model(),p,['clean','missing'])
            saved=json.loads(p.read_text());self.assertEqual(len(saved['results']),1)
            self.assertEqual(saved['results'][0]['status'],'failed')
            self.assertFalse(saved['complete'])
    def test_resume_and_protocol_guard(self):
        class Model:
            model='test-double-not-inference'
            calls=0
            def __call__(self,messages):self.calls+=1;raise OSError()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'report.json';m=Model()
            evaluate(m,p,['clean']);evaluate(m,p,['clean'])
            self.assertEqual(m.calls,1)
            m.model='changed'
            with self.assertRaises(ValueError):evaluate(m,p,['clean'])
