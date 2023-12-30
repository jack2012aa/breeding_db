import unittest
from datetime import datetime

from data_structures.estrus import Estrus, Pregnant_status
from data_structures.pig import Pig


class EstrusTestCase(unittest.TestCase):

    def setUp(self):
        self.estrus = Estrus()

    def tearDown(self):
        self.pig = None

    def test_set_sow(self):

        # Correct
        pig = Pig()
        pig.set_id("123456")
        pig.set_birthday("2019-12-23")
        pig.set_farm("test_farm")
        self.estrus.set_sow(pig)
        self.assertEqual(pig, self.estrus.get_sow())

        # Not unique
        pig = Pig()
        pig.set_id("123456")
        self.assertRaises(ValueError, self.estrus.set_sow, pig)

        # TypeError
        self.assertRaises(TypeError, self.estrus.set_sow, None)

    def test_set_estrus_datetime(self):

        # Correct
        self.estrus.set_estrus_datetime("2023-12-05 9:27:30")
        self.assertEqual(
            self.estrus.get_estrus_datetime(), 
            datetime.strptime("2023-12-05 9:27:30", "%Y-%m-%d %H:%M:%S")
        )
        self.estrus.set_estrus_datetime(datetime.strptime("2023-12-05 9:27:30", "%Y-%m-%d %H:%M:%S"))
        self.assertEqual(
            self.estrus.get_estrus_datetime(), 
            datetime.strptime("2023-12-05 9:27:30", "%Y-%m-%d %H:%M:%S")
        )
        self.estrus.set_estrus_datetime("2023-12-05")
        self.assertEqual(
            self.estrus.get_estrus_datetime(), 
            datetime.strptime("2023-12-05", "%Y-%m-%d")
        )

        # Wrong format
        self.assertRaises(ValueError, self.estrus.set_estrus_datetime, "2023/12/15")
        
        # TypeError
        self.assertRaises(TypeError, self.estrus.set_estrus_datetime, None)

    def test_pregnant(self):

        # Correct
        self.estrus.set_pregnant(Pregnant_status.UNKNOWN)
        self.assertEqual(self.estrus.get_pregnant(), Pregnant_status.UNKNOWN)

        # TypeError
        self.assertRaises(TypeError, self.estrus.set_pregnant, Pig())

    def test_parity(self):

        # Correct
        self.estrus.set_parity(0)
        self.assertEqual(0, self.estrus.get_parity())

        # Out of range
        self.assertRaises(ValueError, self.estrus.set_parity, -1)
        self.assertRaises(ValueError, self.estrus.set_parity, 11)

        # TypeError
        self.assertRaises(TypeError, self.estrus.set_parity, Pig())

if __name__ == '__main__':
    unittest.main()