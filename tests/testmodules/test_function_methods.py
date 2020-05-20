import unittest
import VyPRAnalysis as va
import VyPR
import os

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
