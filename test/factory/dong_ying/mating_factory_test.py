import unittest

from data_structures.pig import Pig
from models.pig_model import PigModel
from factory.dong_ying_factory import DongYingMatingFactory

class FactoryTestCase(unittest.TestCase):

    def setUp(self):

        self.factory = DongYingMatingFactory()
        self.model = PigModel()

        # Insert some pigs
        pig = Pig()
        pig.set_id("123456")
        pig.set_birthday("2022-01-03")
        pig.set_farm("Dong-Ying")
        pig.set_gender("M")
        self.model.insert(pig)
        pig.set_birthday("2000-01-03")
        self.model.insert(pig)
        pig.set_birthday("2023-01-03")
        self.model.insert(pig)
        pig.set_birthday("2023-01-05")
        pig.set_gender("F")
        self.model.insert(pig)

    def tearDown(self):
        self.factory = None
        self.model.delete_all("Pigs")
        self.model = None

    def test_correctly_set_mating_datetime(self):

        self.factory.set_mating_datetime("2022-07-09", "16:00:00")
        self.assertEqual(str(self.factory.mating.get_mating_datetime()), "2022-07-09 16:00:00")

    def test_set_wrong_format_datetime(self):

        self.assertRaises(TypeError, self.factory.set_mating_datetime, 20200709)
        self.factory.set_mating_datetime("2022-07-07", "16:00")
        self.assertEqual(self.factory.get_flag(), self.factory.Flags.MATING_DATE_FLAG.value)

    def test_correctly_set_boar(self):

        self.factory.set_boar("<123456>", "2023-01-01", nearest=True)
        self.assertEqual(str(self.factory.mating.get_boar().get_birthday()), "2022-01-03")
        print("Choose 0.")
        self.factory.set_boar("20Y123456", "2023-05-01")
        self.assertEqual(str(self.factory.mating.get_boar().get_birthday()), "2023-01-03")

    def test_set_wrong_boar(self):

        self.assertRaises(TypeError, self.factory.set_boar, 123456, "2023-01-03")
        self.assertRaises(TypeError, self.factory.set_boar, "123456", 123)
        self.factory.set_boar("111111", "2024-05-05")
        self.assertTrue(self.factory.check_flag(self.factory.Flags.BOAR_FLAG.value))


if __name__ == '__main__':
    unittest.main()