import random
import unittest
from datetime import date

from breeding_db.general import *


class MyTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_transform_date(self):

        # Declare variables.
        test_date: date
        test_str: str

        test_date = date(1999, 5, 12)
        self.assertEqual(transform_date(test_date), date(1999, 5, 12))

        test_str = "1999-05-12"
        self.assertEqual(transform_date(test_str), date(1999, 5, 12))

        test_str = "1999/5/12"
        self.assertRaises(ValueError, transform_date, test_str)

    def test_add_with_none(self):

        self.assertEqual(20, add_with_none(None, 10, 5, None, 2, 3))
        with self.assertRaises(TypeError):
            add_with_none("12")


if __name__ == '__main__':
    unittest.main()