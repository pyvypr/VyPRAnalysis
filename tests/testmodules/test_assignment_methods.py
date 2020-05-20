from . import parent_setup

class test_assignment_methods(parent_setup):
    def setUp(self):
        va.set_server("http://localhost:9001/")
    def test_init(self):
        with self.assertRaises(ValueError): va.Assignment(1)
