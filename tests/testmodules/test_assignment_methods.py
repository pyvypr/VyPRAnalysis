from . import parent_setup
import VyPRAnalysis as va

class test_assignment_methods(parent_setup):
    def test_init(self):
        with self.assertRaises(ValueError): va.Assignment(1)
