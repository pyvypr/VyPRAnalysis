import unittest

import sys
sys.path.append("../")
import VyPRAnalysis as analysis

"""classes concerning assignments are commented out
because there are no recorded assignments in the database
TODO test for raising errors, testing global functions and 
functions that create files"""


class test_function_methods(unittest.TestCase):

    def test_init(self):
        self.assertTrue(isinstance(analysis.function(1),analysis.function))
        self.assertTrue(isinstance(analysis.function(fully_qualified_name='app.routes.paths_branching_test'),analysis.function))
        #self.assertRaises(ValueError,'no functions with given ID',analysis.function(7))

    def test_get_calls(self):
        self.assertEqual(len(analysis.function(1).get_calls()),4)
        self.assertEqual(analysis.function(1).get_calls(analysis.http_request(1))[0].id,1)

    def test_get_calls_with_verdict(self):
        self.assertEqual(len(analysis.function(1).get_calls_with_verdict(0)),2)

    def test_get_verdicts(self):
        self.assertEqual(len(analysis.function(1).get_verdicts()),4)
        self.assertEqual(len(analysis.function(1).get_verdicts(0)),2)



class test_property_methods(unittest.TestCase):
    def test_init(self):
        self.assertTrue(isinstance(analysis.property('734d1510681a11c32da16934e170c70804b5328b'),analysis.property))



class test_binding_methods(unittest.TestCase):
    def test_init(self):
        self.assertTrue(isinstance(analysis.binding(1),analysis.binding))



class test_function_call_methods(unittest.TestCase):

    def test_init(self):
        self.assertTrue(isinstance(analysis.function_call(1),analysis.function_call))

    def test_get_falsifying_observation(self):
        self.assertEqual(type(analysis.function_call(1).get_falsifying_observation()),type(analysis.observation(1)))

    def test_get_verdicts(self):
        self.assertEqual(analysis.function_call(2).get_verdicts()[0].id,2)
        self.assertEqual(analysis.function_call(2).get_verdicts(0)[0].id,2)

    def test_get_observations(self):
        self.assertEqual(analysis.function_call(3).get_observations()[0].id,3)


class test_verdict_methods(unittest.TestCase):

    def test_init(self):
        self.assertTrue(isinstance(analysis.verdict(1),analysis.verdict))

    def test_get_property_hash(self):
        self.assertEqual(analysis.verdict(1).get_property_hash(),'734d1510681a11c32da16934e170c70804b5328b')

    def test_get_collapsing_atom(self):
        self.assertEqual(analysis.verdict(1).get_collapsing_atom().id,1)



class test_http_request_methods(unittest.TestCase):

    def test_init(self):
        self.assertTrue(isinstance(analysis.http_request(1),analysis.http_request))
        self.assertTrue(isinstance(analysis.http_request(time_of_request='2019-08-15T15:49:28.610874'),analysis.http_request))

    def test_get_calls(self):
        self.assertEqual(analysis.http_request(1).get_calls()[0].id,1)




class test_atom_methods(unittest.TestCase):

    def test_init(self):
        self.assertTrue(isinstance(analysis.atom(1),analysis.atom))

    def test_get_structure(self):
        self.assertTrue(analysis.atom(1).get_structure(),'monitor_synthesis.formula_tree.TransitionDurationInInterval')



class test_atom_instrumentation_point_pair_methods(unittest.TestCase):
    def test_init(self):
        self.assertTrue(isinstance(analysis.atom_instrumentation_point_pair(1,1),analysis.atom_instrumentation_point_pair))


class test_binding_instrumentation_point_pair_methods(unittest.TestCase):
    def test_init(self):
        self.assertTrue(isinstance(analysis.binding_instrumentation_point_pair(1,1),analysis.binding_instrumentation_point_pair))


class test_instrumentation_point_methods(unittest.TestCase):

    def test_init(self):
        self.assertTrue(isinstance(analysis.instrumentation_point(1),analysis.instrumentation_point))

    def test_get_observations(self):
        self.assertEqual(len(analysis.instrumentation_point(1).get_observations()),4)


class test_observation_methods(unittest.TestCase):

    def test_init(self):
        self.assertTrue(isinstance(analysis.observation(1),analysis.observation))

    """def test_get_assignments(self):
        self.assertEqual()

    def test_get_assignments_as_dictionary(self):
        self.assertEqual()"""

    def test_verdict_severity(self):
        self.assertAlmostEqual(analysis.observation(1).verdict_severity(),-0.102061)
        self.assertEqual(analysis.observation(3).verdict_severity(),9e-06)

    def test_get_instrumentation_point(self):
        self.assertEqual(analysis.observation(1).get_instrumentation_point().id,1)




"""class test_observation_assignment_pair_methods(unittest.TestCase):
    def test_init(self):
        self.assertTrue(isinstance(analysis.observation_assignment_pair(1),analysis.observation_assignment_pair))

class test_assignment_methods(unittest.TestCase):
    def test_init(self):
        self.assertTrue(isinstance(analysis.assignment(1),analysis.assignment))"""


class test_path_condition_structure_methods:
    def test_init(self):
        self.assertTrue(isinstance(analysis.path_condition_structure(4),analysis.path_condition_structure))

class test_path_condition_methods:
    def test_init(self):
        self.assertTrue(isinstance(analysis.path_condition(30),analysis.path_condition))

class test_search_tree_methods:
    def test_init(self):
        self.assertTrue(isinstance(analysis.search_tree(1),analysis.search_tree))

class test_search_tree_vertex_methods:
    def test_init(self):
        self.assertTrue(isinstance(analysis.search_tree_vertex(1),analysis.search_tree_vertex))

class test_intersection_methods:
    def test_init(self):
        self.assertTrue(isinstance(analysis.intersection(1),analysis.intersection))






if __name__ == '__main__':
    analysis.set_server("http://127.0.0.1:9001/")
    unittest.main()
