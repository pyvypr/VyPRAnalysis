from . import parent_setup
import VyPRAnalysis as va

class test_verdict_methods(parent_setup):

    def test_init(self):
        self.assertIsInstance(va.Verdict(1), va.Verdict)
        with self.assertRaises(ValueError): va.Verdict(9000)
        self.assertIsInstance(va.verdict(1), va.Verdict)
        with self.assertRaises(ValueError): va.verdict(9000)
        with self.assertRaises(Exception): va.verdict(verdict = 0)

    def test_get_observations(self):
        self.assertEqual(len(va.verdict(1).get_observations()),1)
        self.assertIsInstance(va.verdict(1).get_observations()[0], va.Observation)
