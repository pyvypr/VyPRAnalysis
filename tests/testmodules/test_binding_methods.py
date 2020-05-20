from . import parent_setup
import VyPRAnalysis as va

class test_binding_methods(parent_setup):

    def test_init(self):

        self.assertIsInstance(va.Binding(1,0,2,[251],"437efac7d4163aeccc48140fadf6b071dc26e31d"), va.Binding)

        self.assertIsInstance(va.binding(1), va.Binding)
        self.assertIsInstance(va.binding(2), va.Binding)
        self.assertIsInstance(va.binding(3), va.Binding)

        with self.assertRaises(ValueError): va.binding(4)

        self.assertEqual(len(va.binding(function=1)), 0)
        self.assertEqual(len(va.binding(function=2)), 1)
        self.assertIsInstance(va.binding(function=2)[0], va.Binding)
        self.assertEqual(len(va.binding(function=3)), 2)
        self.assertIsInstance(va.binding(function=3)[0], va.Binding)
        self.assertIsInstance(va.binding(function=3)[1], va.Binding)

        with self.assertRaises(Exception): va.binding(property_hash="437efac7d4163aeccc48140fadf6b071dc26e31d")

        self.assertEqual(len(va.binding(function=3, binding_statement_lines=42)), 2)
        self.assertIsInstance(va.binding(function=3, binding_statement_lines=42)[0], va.Binding)
        self.assertEqual(len(va.binding(function=3, binding_statement_lines=[104,42])), 1)
        self.assertIsInstance(va.binding(function=3, binding_statement_lines=[104,42])[0], va.Binding)

        with self.assertRaises(Exception): va.binding(binding_statement_lines=42)

    def test_get_verdicts(self):
        self.assertEqual(len(va.binding(1).get_verdicts()), 4000)
        self.assertIsInstance(va.binding(1).get_verdicts()[0], va.Verdict)
        self.assertEqual(len(va.binding(2).get_verdicts()), 604)
        self.assertIsInstance(va.binding(2).get_verdicts()[600], va.Verdict)
        self.assertEqual(len(va.binding(3).get_verdicts()), 3941)
        self.assertIsInstance(va.binding(3).get_verdicts()[100], va.Verdict)
        self.assertEqual(
            len(va.Binding(4,0,2,[3],"fake_hash").get_verdicts()), 0)
