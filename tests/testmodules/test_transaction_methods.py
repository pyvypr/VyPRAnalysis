from . import parent_setup
import VyPRAnalysis as va

class test_transaction_methods(parent_setup):

    def test_init(self):
        self.assertIsInstance(va.Transaction(1), va.Transaction)
        with self.assertRaises(ValueError): va.Transaction(7911)
        self.assertIsInstance(va.Transaction(7910, "2020-02-25T21:03:17.546866"), va.Transaction)
        self.assertIsInstance(va.Transaction(time_of_transaction="2020-02-25T21:03:17.546866"), va.Transaction)
        with self.assertRaises(ValueError): va.Transaction()
        self.assertEqual(len(va.transaction(time_lower_bound="2020-02-25T21:02:38.724606",
            time_upper_bound="2020-02-25T21:03:01.805627")), 15)
        self.assertEqual(va.transaction(time_lower_bound="2020-02-28T21:02:38.724606",
            time_upper_bound="2020-02-28T21:03:01.805627"), [])
        self.assertIsInstance(va.transaction(time_lower_bound="2020-02-25T21:02:38.724606",
            time_upper_bound="2020-02-25T21:03:01.805627")[0], va.Transaction)

    def test_get_calls(self):
        self.assertEqual(len(va.transaction(1).get_calls()), 2)
        self.assertIsInstance(va.transaction(1).get_calls()[1], va.FunctionCall)
