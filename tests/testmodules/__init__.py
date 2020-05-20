import unittest
from . import *

class parent_setup(unittest.TestCase):
    def setUp(self):
        va.set_server("http://localhost:9001/")
