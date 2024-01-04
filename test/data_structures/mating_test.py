import unittest
from datetime import datetime

from data_structures.pig import Pig
from data_structures.estrus import Estrus
from data_structures.mating import Mating

class MatingTestCase(unittest.TestCase):

    def setUp(self):

        self.mating = Mating()
        self.sow = Pig()
        self.sow.set_id("123456")
        self.sow.set_birthday("2020-01-31")
        self.sow.set_farm("test")
        self.estrus = Estrus()
        self.estrus.set_sow(self.sow)
        self.estrus.set_estrus_datetime("2020-07-30")

    def tearDown(self):
        self.pig = None

    def test_correctly_set_estrus(self):
        
        self.mating.set_estrus(self.estrus)
        self.assertEqual(self.mating.get_estrus(), self.estrus)

    def test_set_not_unique_estrus(self):

        estrus = Estrus()
        estrus.set_sow(self.sow)
        self.assertRaises(ValueError, self.mating.set_estrus, estrus)

    def test_set_not_estrus(self):

        self.assertRaises(TypeError, self.mating.set_estrus, 123)

    def test_set_mating_datetime(self):

        # Correct
        self.mating.set_mating_datetime("2023-12-05 9:27:30")
        self.assertEqual(
            self.mating.get_mating_datetime(), 
            datetime.strptime("2023-12-05 9:27:30", "%Y-%m-%d %H:%M:%S")
        )
        self.mating.set_mating_datetime(datetime.strptime("2023-12-05 9:27:30", "%Y-%m-%d %H:%M:%S"))
        self.assertEqual(
            self.mating.get_mating_datetime(), 
            datetime.strptime("2023-12-05 9:27:30", "%Y-%m-%d %H:%M:%S")
        )
        self.mating.set_mating_datetime("2023-12-05")
        self.assertEqual(
            self.mating.get_mating_datetime(), 
            datetime.strptime("2023-12-05", "%Y-%m-%d")
        )

        # Wrong format
        self.assertRaises(ValueError, self.mating.set_mating_datetime, "2023/12/15")
        
        # TypeError
        self.assertRaises(TypeError, self.mating.set_mating_datetime, None)

    def test_correctly_set_boar(self):

        self.mating.set_boar(self.sow)
        self.assertEqual(self.sow, self.mating.get_boar())

    def test_set_not_unique_boar(self):

        boar = Pig()
        boar.set_id("12344")
        self.assertRaises(ValueError, self.mating.set_boar, boar)

    def test_set_not_boar(self):

        self.assertRaises(TypeError, self.mating.set_boar, "12344")

    def test_equality(self):

        mating = Mating()
        self.mating.set_estrus(self.estrus)
        mating.set_estrus(self.estrus)
        self.assertEqual(self.mating, mating)
        self.mating.set_boar(self.sow)
        mating.set_boar(self.sow)
        self.assertEqual(self.mating, mating)
        self.mating.set_mating_datetime("2023-02-06")
        mating.set_mating_datetime("2023-02-06")
        self.assertEqual(self.mating, mating)

    def test_inequality(self):

        mating = Mating()
        estrus = Estrus()
        estrus.set_sow(self.sow)
        estrus.set_estrus_datetime("2023-01-04 16:00:00")
        self.mating.set_estrus(self.estrus)
        mating.set_estrus(estrus)
        self.assertNotEqual(self.mating, mating)
        mating.set_estrus(self.estrus)
        self.mating.set_mating_datetime("2023-01-01 16:00:00")
        mating.set_mating_datetime("2023-01-01 19:00:00")
        self.assertNotEqual(self.mating, mating)
        mating.set_mating_datetime("2023-01-01 16:00:00")
        boar = Pig()
        boar.set_id("12345")
        boar.set_birthday("2019-01-01")
        boar.set_farm("test")
        self.mating.set_boar(boar)
        self.assertNotEqual(self.mating, mating)


if __name__ == '__main__':
    unittest.main()
