from . import parent_setup
import VyPRAnalysis as va

class test_global_methods(parent_setup):

    def test_list_function(self):
        self.assertEqual(len(va.list_functions()), 3)
        for i in range(2):
            self.assertIsInstance(va.list_functions()[i], va.Function)
    #def test_list_test_data(self):
