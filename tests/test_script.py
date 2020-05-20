import sys
import os
sys.path.append("../../")

import VyPRAnalysis as va
import VyPR
import unittest
from testmodules import (test_binding_methods, test_function_methods, test_property_methods,
test_verdict_methods, test_global_methods, test_testdata_methods, test_assignment_methods,
test_function_call_methods, test_instrumentation_point_methods, test_transaction_methods, test_atom_methods,
test_observation_methods)



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

if __name__ == "__main__":
    va.prepare("verdicts.db", 9001, True)
    #va.set_monitored_service_path(os.path.abspath(""))
    unittest.main(exit=False)
    va.teardown()
