import unittest
from decisionlab.challenge import reference,grade
from decisionlab.data import CHALLENGE_CASES

class ChallengeTests(unittest.TestCase):
    def test_reference_meets_prospective_expectations(self):
        for case in CHALLENGE_CASES:
            with self.subTest(case=case):self.assertTrue(grade(reference(case))['correct'])
    def test_unsupported_hold_gets_no_credit(self):
        r=reference('flat');r['decision']['evidence_ids']=[]
        self.assertFalse(grade(r)['correct'])
    def test_fabricated_evidence_gets_no_credit(self):
        r=reference('flat');r['trace'][0]['result']['segments']['small']['change_pp']=99
        self.assertFalse(grade(r)['correct'])
