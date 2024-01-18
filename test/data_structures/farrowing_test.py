import unittest
from datetime import date

from data_structures.pig import Pig
from data_structures.estrus import Estrus
from data_structures.farrowing import Farrowing

class FarrowingTestCase(unittest.TestCase):

    def setUp(self):
        self.farrowing = Farrowing()

    def tearDown(self):
        self.farrowing = None

    def test_set_estrus(self):
        
        sow = Pig()
        sow.set_id("112233")
        sow.set_birthday("2020-05-12")
        sow.set_farm("test")
        estrus = Estrus()
        estrus.set_sow(sow)
        self.assertRaises(ValueError, self.farrowing.set_estrus, estrus)
        self.assertRaises(TypeError, self.farrowing.set_estrus, 1234)
        estrus.set_estrus_datetime("2022-04-10 16:00:00")
        self.farrowing.set_estrus(estrus)
        self.assertEqual(self.farrowing.get_estrus(), estrus)

    def test_set_farrowing_date(self):

        self.farrowing.set_farrowing_date("2022-10-10")
        self.assertEqual(str(self.farrowing.get_farrowing_date()), "2022-10-10")
        self.farrowing.set_farrowing_date(date.fromisoformat("2022-10-11"))
        self.assertEqual(str(self.farrowing.get_farrowing_date()), "2022-10-11")
        self.assertRaises(TypeError, self.farrowing.set_farrowing_date, 123)
        self.assertRaises(ValueError, self.farrowing.set_farrowing_date, "123")

    def test_set_numeric(self):

        self.farrowing.set_crushing(1)
        self.assertEqual(1, self.farrowing.get_crushing())
        self.farrowing.set_black(1)
        self.assertEqual(1, self.farrowing.get_black())
        self.farrowing.set_weak(1)
        self.assertEqual(1, self.farrowing.get_weak())
        self.farrowing.set_malformation(1)
        self.assertEqual(1, self.farrowing.get_malformation())
        self.farrowing.set_dead(1)
        self.assertEqual(1, self.farrowing.get_dead())
        self.assertEqual(5, self.farrowing.get_born_dead())
        self.farrowing.set_n_of_male(3)
        self.assertEqual(3, self.farrowing.get_n_of_male())
        self.farrowing.set_n_of_female(3)
        self.assertEqual(3, self.farrowing.get_n_of_female())
        self.assertEqual(6, self.farrowing.get_born_alive())
        self.assertEqual(11, self.farrowing.get_total_born())
        self.farrowing.set_total_weight(90)
        self.assertEqual(90, self.farrowing.get_total_weight())
        self.farrowing.set_note("234324")
        self.assertEqual("234324", self.farrowing.get_note())



if __name__ == '__main__':
    unittest.main()
