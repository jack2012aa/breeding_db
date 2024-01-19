import unittest

from data_structures.pig import Pig
from data_structures.estrus import Estrus
from models.pig_model import PigModel
from models.estrus_model import EstrusModel
from factory.dong_ying_factory import DongYingFarrowingFactory

class FactoryTestCase(unittest.TestCase):

    def setUp(self):

        self.factory = DongYingFarrowingFactory()

        # Insert some pigs
        pig = Pig()
        pig.set_id("123456")
        pig.set_birthday("2022-01-03")
        pig.set_farm("Dong-Ying")
        pig.set_gender("F")
        PigModel().insert(pig)
        pig.set_birthday("2000-01-03")
        PigModel().insert(pig)
        pig.set_birthday("2023-01-03")
        PigModel().insert(pig)
        pig.set_birthday("2023-01-05")
        pig.set_gender("M")
        PigModel().insert(pig)

        # Insert some estrus
        estrus = Estrus()
        pig.set_birthday("2022-01-03")
        pig.set_gender("F")
        estrus.set_sow(pig)
        estrus.set_estrus_datetime("2023-02-27")
        EstrusModel().insert(estrus)
        estrus.set_estrus_datetime("2023-11-08")
        EstrusModel().insert(estrus)
        pig.set_farm("test")
        PigModel().insert(pig)
        estrus.set_sow(pig)
        estrus.set_estrus_datetime("2020-04-30")
        EstrusModel().insert(estrus)

    def tearDown(self):
        self.factory = None
        EstrusModel().delete_all("Pigs")
        EstrusModel().delete_all("Estrus")
        EstrusModel().delete_all("Farrowings")
        self.model = None

    def test_correctly_set_estrus(self):

        self.factory.set_estrus("123456", "2023-09-29")
        self.assertEqual(str(self.factory.farrowing.get_estrus().get_estrus_datetime()), "2023-02-27 00:00:00")
        self.factory.set_estrus("123456", "2024-04-08")
        self.assertEqual(str(self.factory.farrowing.get_estrus().get_estrus_datetime()), "2023-11-08 00:00:00")

    def test_set_estrus_error(self):

        self.assertRaises(TypeError, self.factory.set_estrus, 123456, "2023-09-29")
        self.assertRaises(TypeError, self.factory.set_estrus, "123456", 123)
        self.factory.set_estrus("123456", "2025-12-25")
        self.assertEqual(self.factory.Flags.ESTRUS_FLAG.value, self.factory.get_flag())
        self.factory = DongYingFarrowingFactory()
        self.factory.set_estrus("123456", "2022-09-08")
        self.assertEqual(self.factory.Flags.ESTRUS_FLAG.value, self.factory.get_flag())
        self.factory = DongYingFarrowingFactory()
        self.factory.set_estrus("123451", "2020-09-29")
        self.assertEqual(self.factory.Flags.ESTRUS_FLAG.value, self.factory.get_flag())

    def test_set_numeric(self):

        self.factory.set_crushing(1)
        self.assertEqual(1, self.factory.farrowing.get_crushing())
        print("Choose Yes.")
        self.factory.set_malformation(-3)
        self.assertEqual(3, self.factory.farrowing.get_malformation())
        print("Choose No.")
        self.factory.set_black(40)
        self.assertEqual(self.factory.Flags.BLACK_FLAG.value, self.factory.get_flag())


if __name__ == '__main__':
    unittest.main()