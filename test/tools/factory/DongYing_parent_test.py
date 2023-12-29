import unittest

from models.pig_model import PigModel
from data_structures.pig import Pig
from tools.pig_factory import DongYingFactory, ParentError


class FactoryTest(unittest.TestCase):

    def setUp(self):
        self.factory = DongYingFactory()
        self.model = PigModel()

    def tearDown(self):
        self.factory = None
        self.model.delete_all()
        self.model = None

    def test_set_parent(self):

        # Insert some pigs
        pig = Pig()
        pig.set_id("123456")
        pig.set_birthday("2022-12-29")
        pig.set_farm("Dong-Ying")
        pig.set_gender("M")
        pig.set_breed("Y")
        self.model.insert(pig)
        pig = None
        pig = Pig()
        pig.set_id("123456")
        pig.set_birthday("2022-12-31")
        pig.set_farm("Dong-Ying")
        pig.set_gender("M")
        pig.set_breed("Y")
        self.model.insert(pig)
        pig = None
        pig = Pig()
        pig.set_id("123457")
        pig.set_birthday("2022-12-20")
        pig.set_farm("farm2")
        pig.set_gender("M")
        pig.set_breed("Y")
        self.model.insert(pig)
        pig = None
        pig = Pig()
        pig.set_id("123457")
        pig.set_birthday("2022-12-29")
        pig.set_farm("Dong-Ying")
        pig.set_gender("M")
        pig.set_breed("Y")
        self.model.insert(pig)
        self.factory.set_id("123333")
        self.factory.set_birthday("2022-12-30")
        self.factory.set_farm()
        self.factory.set_gender("M")
        self.factory.set_parent(False, "Y123456", True, True)
        # Test basic function.
        self.assertEqual(str(self.factory.pig.get_sire().get_birthday()), "2022-12-29")
        self.factory.set_birthday("2023-01-01")
        self.factory.set_parent(False, "Y123456", True, True)
        # Test nearest.
        self.assertEqual(str(self.factory.pig.get_sire().get_birthday()), "2022-12-31")
        self.factory.set_birthday("2022-12-21")
        self.factory.set_parent(False, "Y123457", False, True)
        # Test in_farm
        self.assertEqual(str(self.factory.pig.get_sire().get_birthday()), "2022-12-20")
        # Test multiple choice.
        print("Choose 2022-12-31.")
        self.factory.set_birthday("2023-12-10")
        self.factory.set_parent(False, "Y123456", True, False)
        self.assertEqual(str(self.factory.pig.get_sire().get_birthday()), "2022-12-31")
        print("Choose non of above.")
        self.assertRaises(ParentError, self.factory.set_parent, False, "Y123456", True, False)

if __name__ == '__main__':
    unittest.main()
