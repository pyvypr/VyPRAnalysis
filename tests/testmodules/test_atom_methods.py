from . import parent_setup

class test_atom_methods(parent_setup):

    def test_init(self):
        self.assertIsInstance(va.Atom(1), va.Atom)
        self.assertIsInstance(va.Atom(2), va.Atom)
        self.assertIsInstance(va.Atom(3), va.Atom)
        with self.assertRaises(ValueError): va.Atom(4)
        self.assertIsInstance(va.Atom(index_in_atoms=0, property_hash="9946612dc54b28688107995173d4463933ff1e5d"), va.Atom)
        self.assertEqual(va.Atom(index_in_atoms=0, property_hash="9946612dc54b28688107995173d4463933ff1e5d").id, 1)
        with self.assertRaises(ValueError): va.Atom(index_in_atoms=0)
    def test_get_structure(self):
        self.assertIsInstance(va.Atom(1).get_structure(), VyPR.monitor_synthesis.formula_tree.StateValueEqualTo)
