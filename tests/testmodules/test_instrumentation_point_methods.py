from . import parent_setup
import VyPRAnalysis as va

class test_instrumentation_point_methods(parent_setup):

    def test_init(self):
        self.assertIsInstance(va.instrumentation_point(1), va.instrumentation_point)
        with self.assertRaises(ValueError): va.instrumentation_point(10)
    def test_get_observations(self):
        self.assertEqual(len(va.instrumentation_point(1).get_observations()), 4000)
        self.assertIsInstance(va.instrumentation_point(1).get_observations()[0], va.Observation)
        self.assertEqual(va.instrumentation_point(6, "", 0).get_observations(), [])
