import unittest
from unittest.mock import patch
from decisionlab.engine import Investigation
from decisionlab.stress import build,check,fixture,make_dataset

class GeneratedStressTests(unittest.TestCase):
    def test_generated_variations(self):
        report=build()
        self.assertEqual(report['total'],600)
        self.assertEqual(report['passed'],600,[r for r in report['results'] if not r['passed']])
    def test_generator_changes_business_inputs(self):
        self.assertNotEqual(len(fixture(1000)),len(fixture(1001)))
        self.assertNotEqual({r[4] for r in fixture(1000)},{r[4] for r in fixture(1001)})
    def test_oracle_detects_wrong_economics(self):
        with patch.object(Investigation,'_scenario',return_value={'net_scenario':-999}):
            self.assertFalse(check(1001)['passed'])
    def test_half_cent_rounds_up(self):
        with patch('decisionlab.engine.dataset',side_effect=lambda *_:make_dataset(fixture(1001))):lab=Investigation()
        try:
            lab.step('compare')
            r=lab.step('scenario',{'segment':'small','lift':.01,'cost':100})['result']
            self.assertEqual(r['incremental_contribution_scenario'],1057.73)
            self.assertEqual(r['net_scenario'],957.73)
        finally:lab.close()
