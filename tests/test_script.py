import sys
import os
sys.path.append("../../")

import VyPRAnalysis as va
import VyPR
import unittest
from testmodules.test_binding_methods import *
from testmodules.test_function_methods import *
from testmodules.test_property_methods import *
from testmodules.test_verdict_methods import *
from testmodules.test_global_methods import *
from testmodules.test_testdata_methods import *
from testmodules.test_assignment_methods import *
from testmodules.test_function_call_methods import *
from testmodules.test_instrumentation_point_methods import *
from testmodules.test_transaction_methods import *
from testmodules.test_atom_methods import *
from testmodules.test_observation_methods import *



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
