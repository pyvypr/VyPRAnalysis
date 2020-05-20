from . import parent_setup

class test_property_methods(parent_setup):

    def test_init(self):
        self.assertIsInstance(va.Property(hash="9946612dc54b28688107995173d4463933ff1e5d"), va.Property)
        self.assertIsInstance(va.property(hash="9946612dc54b28688107995173d4463933ff1e5d"), va.Property)
        self.assertIsInstance(va.Property(hash="437efac7d4163aeccc48140fadf6b071dc26e31d"), va.Property)
        self.assertIsInstance(va.property(hash="437efac7d4163aeccc48140fadf6b071dc26e31d"), va.Property)
        self.assertIsInstance(va.Property(hash="f514c0902a441d6c2bc005fd69c5b14b1ddb5dd6"), va.Property)
        self.assertIsInstance(va.property(hash="f514c0902a441d6c2bc005fd69c5b14b1ddb5dd6"), va.Property)

        with self.assertRaises(ValueError): va.property(hash='wrong_property_hash')
