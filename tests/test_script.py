import sys
import os
# to find VyPRAnalysis
sys.path.append("../../")
# to find VyPR
sys.path.append("VyPRServer")

import VyPRAnalysis as va
import VyPR
import unittest
from time import sleep


""" NOTES
- do we need to test repr methods?
- don't forget to test the path reconstruction functions, global functions
"""

class test_server_setup(unittest.TestCase):
    def setUp(self):
        va.prepare("verdicts.db", logging=True)

    def test_connection(self):
        va.set_server("http://localhost:9002/")

    def tearDown(self):
        try:
            va.teardown()
        except:
            pass

class test_function_methods(unittest.TestCase):

    def setUp(self):
        va.set_server("http://localhost:9001/")
        va.set_monitored_service_path(os.path.abspath(""))

    def test_init(self):
        self.assertIsInstance(
            va.Function(1, 'server-app.routes.find_new_hashes'), va.Function)
        self.assertIsInstance(va.function(1),va.Function)
        self.assertIsInstance(
            va.function(fully_qualified_name='server-app.routes.find_new_hashes')[0], va.Function)
        self.assertEqual(va.function(1).fully_qualified_name, 'server-app.routes.find_new_hashes')

        self.assertIsInstance(
            va.Function(2, 'server-app.routes.check_hashes'), va.Function)
        self.assertIsInstance(va.function(2),va.Function)
        self.assertIsInstance(
            va.function(fully_qualified_name='server-app.routes.check_hashes')[0], va.Function)
        self.assertEqual(va.function(2).fully_qualified_name, 'server-app.routes.check_hashes')

        self.assertIsInstance(
            va.Function(3, 'server-app.metadata_handler.MetadataHandler:__init__'), va.Function)
        self.assertIsInstance(va.function(3),va.Function)
        self.assertIsInstance(
            va.function(fully_qualified_name='server-app.metadata_handler.MetadataHandler:__init__')[0],
            va.Function)
        self.assertEqual(va.function(3).fully_qualified_name, 'server-app.metadata_handler.MetadataHandler:__init__')

        with self.assertRaises(ValueError): va.function(4)
        self.assertEqual(len(va.function(fully_qualified_name='wrong_name')), 0)

    def test_get_calls(self):

        self.assertEqual(len(va.function(1).get_calls()),4000)
        self.assertIsInstance(va.function(1).get_calls()[0], va.FunctionCall)

        self.assertEqual(len(va.function(2).get_calls()),4000)
        self.assertIsInstance(va.function(2).get_calls()[0], va.FunctionCall)

        self.assertEqual(len(va.function(3).get_calls()),3910)
        self.assertIsInstance(va.function(3).get_calls()[0], va.FunctionCall)

        self.assertEqual(len(va.Function(4, "fake_name").get_calls()), 0)

    def test_get_scfg(self):
        self.assertIsInstance(va.function(3).get_scfg(), VyPR.SCFG.construction.CFG)

    def test_get_bindings(self):
        self.assertEqual(len(va.function(1).get_bindings()), 0)
        self.assertEqual(len(va.function(2).get_bindings()), 1)
        self.assertIsInstance(va.function(2).get_bindings()[0], va.Binding)
        self.assertEqual(len(va.function(3).get_bindings()), 2)
        self.assertIsInstance(va.function(3).get_bindings()[0], va.Binding)
        self.assertIsInstance(va.function(3).get_bindings()[1], va.Binding)

    def test_get_properties(self):
        self.assertEqual(len(va.function(1).get_properties()), 1)
        self.assertIsInstance(va.function(1).get_properties()[0], va.Property)
        self.assertEqual(len(va.function(2).get_properties()), 1)
        self.assertIsInstance(va.function(2).get_properties()[0], va.Property)
        self.assertEqual(len(va.function(3).get_properties()), 1)
        self.assertIsInstance(va.function(3).get_properties()[0], va.Property)

        self.assertEqual(len(va.Function(4, "fake_name").get_properties()), 0)


class test_property_methods(unittest.TestCase):

    def setUp(self):
        va.set_server("http://localhost:9001/")

    def test_init(self):
        self.assertIsInstance(va.Property(hash="9946612dc54b28688107995173d4463933ff1e5d"), va.Property)
        self.assertIsInstance(va.property(hash="9946612dc54b28688107995173d4463933ff1e5d"), va.Property)
        self.assertIsInstance(va.Property(hash="437efac7d4163aeccc48140fadf6b071dc26e31d"), va.Property)
        self.assertIsInstance(va.property(hash="437efac7d4163aeccc48140fadf6b071dc26e31d"), va.Property)
        self.assertIsInstance(va.Property(hash="f514c0902a441d6c2bc005fd69c5b14b1ddb5dd6"), va.Property)
        self.assertIsInstance(va.property(hash="f514c0902a441d6c2bc005fd69c5b14b1ddb5dd6"), va.Property)

        with self.assertRaises(ValueError): va.property(hash='wrong_property_hash')

class test_binding_methods(unittest.TestCase):
    def setUp(self):
        va.set_server("http://localhost:9001/")

    def test_init(self):

        self.assertIsInstance(va.Binding(1,0,2,[251],"437efac7d4163aeccc48140fadf6b071dc26e31d"), va.Binding)

        self.assertIsInstance(va.binding(1), va.Binding)
        self.assertIsInstance(va.binding(2), va.Binding)
        self.assertIsInstance(va.binding(3), va.Binding)

        with self.assertRaises(ValueError): va.binding(4)

        self.assertEqual(len(va.binding(function=1)), 0)
        self.assertEqual(len(va.binding(function=2)), 1)
        self.assertIsInstance(va.binding(function=2)[0], va.Binding)
        self.assertEqual(len(va.binding(function=3)), 2)
        self.assertIsInstance(va.binding(function=3)[0], va.Binding)
        self.assertIsInstance(va.binding(function=3)[1], va.Binding)

        with self.assertRaises(Exception): va.binding(property_hash="437efac7d4163aeccc48140fadf6b071dc26e31d")

        self.assertEqual(len(va.binding(function=3, binding_statement_lines=42)), 2)
        self.assertIsInstance(va.binding(function=3, binding_statement_lines=42)[0], va.Binding)
        self.assertEqual(len(va.binding(function=3, binding_statement_lines=[104,42])), 1)
        self.assertIsInstance(va.binding(function=3, binding_statement_lines=[104,42])[0], va.Binding)

        with self.assertRaises(Exception): va.binding(binding_statement_lines=42)

    def test_get_verdicts(self):
        self.assertEqual(len(va.binding(1).get_verdicts()), 4000)
        self.assertIsInstance(va.binding(1).get_verdicts()[0], va.Verdict)
        self.assertEqual(len(va.binding(2).get_verdicts()), 604)
        self.assertIsInstance(va.binding(2).get_verdicts()[600], va.Verdict)
        self.assertEqual(len(va.binding(3).get_verdicts()), 3941)
        self.assertIsInstance(va.binding(3).get_verdicts()[100], va.Verdict)
        self.assertEqual(
            len(va.Binding(4,0,2,[3],"fake_hash").get_verdicts()), 0)

class test_function_call_methods(unittest.TestCase):
    def setUp(self):
        va.set_server("http://localhost:9001/")

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

""" TODO get this data into the database
class test_testdata_methods(unittest.TestCase):
    def test_init(self):
        self.assertIsInstance(va.TestData(), va.TestData)
        self.assertIsInstance(va.test_data(), va.TestData)
    def test_get_calls(self):
        self.assertEqual(len(va.TestData.get_function_calls()), 0)
"""

class test_verdict_methods(unittest.TestCase):
    def setUp(self):
        va.set_server("http://localhost:9001/")

    def test_init(self):
        self.assertIsInstance(va.Verdict(1), va.Verdict)
        with self.assertRaises(ValueError): va.Verdict(9000)
        self.assertIsInstance(va.verdict(1), va.Verdict)
        with self.assertRaises(ValueError): va.verdict(9000)
        with self.assertRaises(Exception): va.verdict(verdict = 0)

    def test_get_observations(self):
        self.assertEqual(len(va.verdict(1).get_observations()),1)
        self.assertIsInstance(va.verdict(1).get_observations()[0], va.Observation)

def test_transaction_methods(self):
    def setUp(self):
        va.set_server("http://localhost:9001/")

    def test_init(self):
        self.assertIsInstance(va.Transaction(1), va.Transaction)
        with self.assertRaises(ValueError): va.Transaction(7911)
        self.assertIsInstance(va.Transaction(7910, "2020-02-25T21:03:17.546866"), va.Transaction)
        self.assertIsInstance(va.Transaction(time_of_transaction="2020-02-25T21:03:17.546866"), va.Transaction)
        with self.assertRaises(ValueError): va.Transaction()
        self.assertEqual(len(va.transaction(time_lower_bound="2020-02-25T21:02:38.724606",
            time_upper_bound="2020-02-25T21:03:01.805627")), 14)
        self.assertEqual(va.transaction(time_lower_bound="2020-02-28T21:02:38.724606",
            time_upper_bound="2020-02-28T21:03:01.805627"), [])
        self.assertIsInstance(va.transaction(time_lower_bound="2020-02-25T21:02:38.724606",
            time_upper_bound="2020-02-25T21:03:01.805627")[0], va.Transaction)

    def test_get_calls(self):
        self.assertEqual(va.transaction(1).get_calls(), 2)
        self.assertIsInstance(va.transaction(1).get_calls()[1], va.FunctionCall)

class test_atom_methods(unittest.TestCase):
    def setUp(self):
        va.set_server("http://localhost:9001/")
    def test_init(self):
        self.assertIsInstance(va.Atom(1), va.Atom)
        self.assertIsInstance(va.Atom(2), va.Atom)
        self.assertIsInstance(va.Atom(3), va.Atom)
        with self.assertRaises(ValueError): va.Atom(4)
        self.assertIsInstance(va.Atom(index_in_atoms=0, property_hash="9946612dc54b28688107995173d4463933ff1e5d"), va.Atom)
        self.assertEqual(va.Atom(index_in_atoms=0, property_hash="9946612dc54b28688107995173d4463933ff1e5d").id, 1)
        with self.assertRaises(ValueError): va.Atom(index_in_atoms=0)
    def test_get_structure(self):
        self.assertIsInstance(va.Atom(1).get_structure(), VyPR.monitor_synthesis.formula_tree.StateValueEqualTo)

class test_instrumentation_point_methods(unittest.TestCase):
    def setUp(self):
        va.set_server("http://localhost:9001/")
    def test_init(self):
        self.assertIsInstance(va.instrumentation_point(1), va.instrumentation_point)
        with self.assertRaises(ValueError): va.instrumentation_point(10)
    def test_get_observations(self):
        self.assertEqual(len(va.instrumentation_point(1).get_observations()), 4000)
        self.assertIsInstance(va.instrumentation_point(1).get_observations()[0], va.Observation)
        self.assertEqual(va.instrumentation_point(6, "", 0).get_observations(), [])

class test_observation_methods(unittest.TestCase):
    def setUp(self):
        va.set_server("http://localhost:9001/")
    def test_init(self):
        with self.assertRaises(ValueError): va.observation(13091)
        self.assertIsInstance(va.observation(1), va.Observation)
    def test_get_assignments(self):
        self.assertEqual(va.observation(1).get_assignments(), [])
    def test_get_instrumentation_point(self):
        self.assertIsInstance(va.observation(1).get_instrumentation_point(), va.instrumentation_point)
#TODO    def test_reconstruct_reaching_path(self):


class test_assignment_methods(unittest.TestCase):
    def setUp(self):
        va.set_server("http://localhost:9001/")
    def test_init(self):
        with self.assertRaises(ValueError): va.Assignment(1)

class test_global_methods(unittest.TestCase):
    def setUp(self):
        va.set_server("http://localhost:9001/")
    def test_list_function(self):
        self.assertEqual(len(va.list_functions()), 3)
        for i in range(2):
            self.assertIsInstance(va.list_functions()[i], va.Function)
    #def test_list_test_data(self):

if __name__ == "__main__":
    va.prepare("verdicts.db", 9001, True)
    #va.set_monitored_service_path(os.path.abspath(""))
    unittest.main(exit=False)
    va.teardown()
