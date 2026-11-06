import copy
import json
from pathlib import Path
import unittest
from decisionlab.benchmark import validate_evaluation

class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((Path(__file__).resolve().parents[1]/'evaluation/qwen2.5-3b-guarded-evidence.json').read_text())
    def test_real_report_replays(self):
        validate_evaluation(self.data)
    def test_missing_case_rejected(self):
        self.data['report']['results'].pop()
        with self.assertRaises(ValueError):validate_evaluation(self.data)
    def test_duplicate_case_rejected(self):
        r=self.data['report']['results'];r[-1]=copy.deepcopy(r[0])
        with self.assertRaises(ValueError):validate_evaluation(self.data)
    def test_inflated_score_rejected(self):
        self.data['report']['correct']=99
        with self.assertRaises(ValueError):validate_evaluation(self.data)
    def test_forged_result_rejected(self):
        self.data['report']['results'][0]['run']['trace'][0]['result']['valid']=False
        with self.assertRaises(ValueError):validate_evaluation(self.data)
    def test_stale_grade_rejected(self):
        self.data['report']['results'][0]['grade']['correct']=False
        with self.assertRaises(ValueError):validate_evaluation(self.data)
    def test_case_swap_rejected(self):
        self.data['report']['results'][0]['run']['case']='missing'
        with self.assertRaises(ValueError):validate_evaluation(self.data)
