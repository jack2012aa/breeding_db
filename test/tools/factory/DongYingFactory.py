import unittest
import datetime

from data_structures.pig import Pig
from tools.pig_factory import DongYingFactory

class FactoryTestCase(unittest.TestCase):

    def setUp(self):
        self.factory = DongYingFactory()

    def tearDown(self):
        self.factory = None

    def test_flag(self):

        self.factory._turn_on_flag(self.factory.BIRTHDAY_FLAG)
        self.factory._turn_on_flag(self.factory.SIRE_FLAG)
        self.assertEqual(self.factory.SIRE_FLAG | self.factory.BIRTHDAY_FLAG,self.factory.get_flag())
        self.factory._turn_off_flag(self.factory.SIRE_FLAG)
        self.assertEqual(self.factory.BIRTHDAY_FLAG,self.factory.get_flag())

    def test_abb(self):
        breed = 'landrace'
        self.assertEqual('L',self.factory.get_breed_abbrevation(breed))

    def test_breed_dict(self):
        breed = '藍瑞斯'
        self.assertEqual('L', self.factory.translate_breed_to_english(breed))

    def test_remove_dash(self):

        self.assertEqual('123414',self.factory.remove_dash_from_id("1234-14"))
        self.assertEqual('123404',self.factory.remove_dash_from_id("1234-4"))
        self.assertEqual('123404',self.factory.remove_dash_from_id("1234-4-12"))
        self.assertEqual('123404',self.factory.remove_dash_from_id("20Y1234-4"))
        self.assertEqual('197006',self.factory.remove_dash_from_id("1970-6楚桃"))
        self.assertEqual('1970',self.factory.remove_dash_from_id("1970"))

    def test_naif_id(self):

        self.factory.set_naif_id("123456")
        self.assertEqual("123456",self.factory.pig.get_naif_id())
        self.factory.set_naif_id("1234567")
        self.assertEqual(self.factory.get_flag(), self.factory.NAIF_FLAG)
        self.factory = DongYingFactory()
        print("Choose Yes.")
        self.factory.set_naif_id("e234567")
        self.assertEqual('234567',self.factory.pig.get_naif_id())
        print("Choose No.")
        self.factory.set_naif_id("e234567")
        self.assertEqual(self.factory.get_flag(), self.factory.NAIF_FLAG)
        self.assertRaises(TypeError, self.factory.set_naif_id, 123456)

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
        self.assertRaises(ValueError, self.factory.get_flag, "NO")
        self.assertRaises(TypeError, self.factory.set_breed, None)

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
        self.assertEqual('1970',self.factory.pig.get_id())

    def test_set_id_6(self):
        id = '1970-12'
        self.factory.set_id(id)
        self.assertEqual('197012',self.factory.pig.get_id())

if __name__ == '__main__':
    unittest.main()
'''
    while True:
        f = DongYingFactory()
        f.set_id(input())
        print(f.pig.get_id())'''