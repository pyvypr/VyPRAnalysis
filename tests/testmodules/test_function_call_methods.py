from . import parent_setup
import VyPRAnalysis as va

class test_function_call_methods(parent_setup):

    def test_init(self):
        self.assertIsInstance(va.function_call(1), va.FunctionCall)
        with self.assertRaises(ValueError): va.function_call(11911)

    def test_get_verdicts(self):
        self.assertEqual(len(va.function_call(12).get_verdicts()), 2)
        self.assertIsInstance(va.function_call(12).get_verdicts()[0], va.Verdict)
        self.assertEqual(len(va.function_call(10).get_verdicts()), 0)

        self.assertEqual(len(va.function_call(12).get_verdicts(False)), 2)
        self.assertIsInstance(va.function_call(12).get_verdicts(False)[1], va.Verdict)
        self.assertEqual(len(va.function_call(12).get_verdicts(True)), 0)

        self.assertEqual(len(va.function_call(12).get_verdicts(property = "f514c0902a441d6c2bc005fd69c5b14b1ddb5dd6")), 2)
        self.assertIsInstance(va.function_call(12).get_verdicts(property = "f514c0902a441d6c2bc005fd69c5b14b1ddb5dd6")[0], va.Verdict)
        self.assertEqual(len(va.function_call(12).get_verdicts(property = va.Property("f514c0902a441d6c2bc005fd69c5b14b1ddb5dd6"))), 2)
        with self.assertRaises(ValueError): va.function_call(6).get_verdicts(property=2)
        self.assertEqual(va.function_call(6).get_verdicts(property="wrong_property"), [])

        self.assertEqual(len(va.function_call(6).get_verdicts(value=False, property = "f514c0902a441d6c2bc005fd69c5b14b1ddb5dd6")), 2)
        self.assertIsInstance(va.function_call(6).get_verdicts(value=False, property = "f514c0902a441d6c2bc005fd69c5b14b1ddb5dd6")[0], va.Verdict)

        self.assertEqual(len(va.function_call(6).get_verdicts(binding=3)), 1)
        self.assertEqual(va.function_call(6).get_verdicts(binding=3)[0].binding, 3)
        self.assertIsInstance(va.function_call(6).get_verdicts(binding=3)[0], va.Verdict)
        self.assertEqual(va.function_call(6).get_verdicts(binding=1), [])
        with self.assertRaises(ValueError): va.function_call(6).get_verdicts(binding="wrong_type")

    def test_get_observations(self):
        self.assertEqual(len(va.function_call(2).get_observations()),1)
        self.assertIsInstance(va.function_call(2).get_observations()[0], va.Observation)
        self.assertEqual(len(va.function_call(1).get_observations()),0)

    #TODO def test_reconstruct_path(self)
