from . import parent_setup

class test_observation_methods(parent_setup):

    def test_init(self):
        with self.assertRaises(ValueError): va.observation(13091)
        self.assertIsInstance(va.observation(1), va.Observation)
    def test_get_assignments(self):
        self.assertEqual(va.observation(1).get_assignments(), [])
    def test_get_instrumentation_point(self):
        self.assertIsInstance(va.observation(1).get_instrumentation_point(), va.instrumentation_point)
#TODO    def test_reconstruct_reaching_path(self):
