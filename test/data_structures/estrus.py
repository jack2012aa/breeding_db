import unittest
from datetime import datetime

from data_structures.estrus import Estrus, PregnantStatus
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
        self.estrus.set_pregnant(PregnantStatus.UNKNOWN)
        self.assertEqual(self.estrus.get_pregnant(), PregnantStatus.UNKNOWN)

        # TypeError
        self.assertRaises(TypeError, self.estrus.set_pregnant, Pig())

    def test_parity(self):

        # Correct
        self.estrus.set_parity(0)
        self.assertEqual(0, self.estrus.get_parity())

        # Out of range
        self.assertRaises(ValueError, self.estrus.set_parity, -1)
        self.assertRaises(ValueError, self.estrus.set_parity, 13)

        # TypeError
        self.assertRaises(TypeError, self.estrus.set_parity, Pig())

    def test_equal(self):

        pig = Pig()
        pig.set_birthday("2022-02-01")
        pig.set_id("123456")
        pig.set_farm("test")

        other = Estrus()
        other.set_sow(pig)
        self.estrus.set_sow(pig)
        other.set_estrus_datetime("2025-03-12 16:00:00")
        self.estrus.set_estrus_datetime("2025-03-12 16:00:00")
        self.assertEqual(self.estrus, other)
        other.set_parity(2)
        self.estrus.set_parity(2)
        other.set_pregnant(PregnantStatus.YES)
        self.estrus.set_pregnant(PregnantStatus.YES)
        self.assertEqual(self.estrus, other)

    def test_inequality(self):

        pig = Pig()
        other = Estrus()
        pig.set_id("123456")
        pig.set_birthday("2021-02-02")
        pig.set_farm("test")
        self.estrus.set_sow(pig)
        self.assertFalse(other == self.estrus)
        other.set_sow(pig)
        self.estrus.set_estrus_datetime("2022-02-02 16:00:00")
        other.set_estrus_datetime("2022-02-01 16:00:00")
        self.assertFalse(other == self.estrus)
        other.set_estrus_datetime("2022-02-02 16:00:00")
        self.estrus.set_parity(3)
        other.set_parity(2)
        self.assertFalse(other == self.estrus)
        self.estrus.set_parity(2)
        self.estrus.set_pregnant(PregnantStatus.ABORTION)
        other.set_pregnant(PregnantStatus.YES)
        self.assertFalse(other == self.estrus)

    def test_is_unique(self):

        self.assertFalse(self.estrus.is_unique())
        pig = Pig()
        pig.set_id("123456")
        pig.set_birthday("2021-02-02")
        pig.set_farm("test")
        self.estrus.set_sow(pig)
        self.assertFalse(self.estrus.is_unique())
        self.estrus.set_estrus_datetime("2023-02-02")
        self.assert_(self.estrus.is_unique())


if __name__ == '__main__':
    unittest.main()