import unittest

from models.pig_model import PigModel
from data_structures.pig import Pig
from factory import ParentError
from factory.dong_ying_factory import DongYingPigFactory

class FactoryTestCase(unittest.TestCase):

    def setUp(self):
        self.factory = DongYingPigFactory()
        self.model = PigModel()

    def tearDown(self):
        self.factory = None
        self.model.delete_all("Pigs")
        self.model = None

    def test_flag(self):

        self.factory._turn_on_flag(self.factory.Flags.BIRTHDAY_FLAG.value)
        self.factory._turn_on_flag(self.factory.Flags.SIRE_FLAG.value)
        self.assertEqual(self.factory.Flags.SIRE_FLAG.value | self.factory.Flags.BIRTHDAY_FLAG.value,self.factory.get_flag())
        self.factory._turn_off_flag(self.factory.Flags.SIRE_FLAG.value)
        self.assertEqual(self.factory.Flags.BIRTHDAY_FLAG.value,self.factory.get_flag())

    def test_abb(self):
        breed = 'landrace'
        self.assertEqual('L',self.factory.get_breed_abbrevation(breed))

    def test_breed_dict(self):
        breed = '藍瑞斯'
        self.assertEqual('L', self.factory.translate_breed_to_english(breed))

    def test_standardize_id(self):

        self.assertEqual('123414',self.factory.standardize_id("1234-14"))
        self.assertEqual('123404',self.factory.standardize_id("1234-4"))
        self.assertEqual('123404',self.factory.standardize_id("1234-4-12"))
        self.assertEqual('123404',self.factory.standardize_id("20Y1234-4"))
        self.assertEqual('197006',self.factory.standardize_id("1970-6楚桃"))
        self.assertEqual('001970',self.factory.standardize_id("1970"))
        self.assertEqual("012304", self.factory.standardize_id("123-4"))

    def test_reg_id(self):

        self.factory.set_reg_id("123456")
        self.assertEqual("123456",self.factory.pig.get_reg_id())
        self.factory.set_reg_id("1234567")
        self.assertEqual(self.factory.get_flag(), self.factory.Flags.REG_FLAG.value)
        self.factory = DongYingPigFactory()
        print("Choose Yes.")
        self.factory.set_reg_id("e234567")
        self.assertEqual('234567',self.factory.pig.get_reg_id())
        print("Choose No.")
        self.factory.set_reg_id("e234567")
        self.assertEqual(self.factory.get_flag(), self.factory.Flags.REG_FLAG.value)
        self.assertRaises(TypeError, self.factory.set_reg_id, 123456)

    def test_set_breed(self):

        breed = 'y'
        self.factory.set_breed(breed)
        self.assertEqual('Y', self.factory.pig.get_breed())
        breed = 'York'
        self.factory.set_breed(breed)
        self.assertEqual('Y', self.factory.pig.get_breed())
        breed = '約克夏'
        self.factory.set_breed(breed)
        self.assertEqual('Y', self.factory.pig.get_breed())
        breed = 'Y'
        self.factory.set_breed(breed)
        self.assertEqual('Y', self.factory.pig.get_breed())
        self.assertRaises(ValueError, self.factory.set_breed, "NO")
        self.assertRaises(TypeError, self.factory.set_breed, 123)

    def test_set_id_1(self):
        id = '1234-4'
        self.factory.set_id(id)
        self.assertEqual('123404',self.factory.pig.get_id())
    
    def test_set_id_2(self):
        id = '1234-4-12'
        self.factory.set_id(id)
        self.assertEqual('123404',self.factory.pig.get_id())

    def test_set_id_3(self):
        id = '20Y1234-4'
        self.factory.set_id(id)
        self.assertEqual('123404',self.factory.pig.get_id())

    def test_set_id_4(self):
        id = '1970-6楚桃'
        self.factory.set_id(id)
        self.assertEqual('197006',self.factory.pig.get_id())

    def test_set_id_5(self):
        id = '1970'
        self.factory.set_id(id)
        self.assertEqual('001970',self.factory.pig.get_id())

    def test_set_id_6(self):
        id = '1970-12'
        self.factory.set_id(id)
        self.assertEqual('197012',self.factory.pig.get_id())

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
        self.factory.set_parent(False, "Y123456", True, False)
        self.assertEqual(self.factory.Flags.SIRE_FLAG.value, self.factory.get_flag())


if __name__ == '__main__':
    unittest.main()
'''
    while True:
        f = DongYingFactory()
        f.set_id(input())
        print(f.pig.get_id())'''