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

    def test_flag_2(self):
        self.factory._turn_on_flag(self.factory.BIRTHDAY_FLAG)
        self.factory._turn_on_flag(self.factory.SIRE_FLAG)
        self.factory._turn_off_flag(self.factory.ID_FLAG)
        self.assertEqual(self.factory.SIRE_FLAG | self.factory.BIRTHDAY_FLAG,self.factory.get_flag())
        self.factory._turn_off_flag(self.factory.SIRE_FLAG)
        self.assertEqual(self.factory.BIRTHDAY_FLAG,self.factory.get_flag())

    def test_abb(self):
        breed = 'landrace'
        self.assertEqual('L',self.factory.get_breed_abbrevation(breed))

    def test_breed_dict(self):
        breed = '藍瑞斯'
        self.assertEqual('L', self.factory.translate_breed_to_english(breed))

    def test_remove_dash_1(self):
        id = '1234-4'
        self.assertEqual('123404',self.factory.remove_dash_from_id(id))
    
    def test_remove_dash_2(self):
        id = '1234-4-12'
        self.assertEqual('123404',self.factory.remove_dash_from_id(id))

    def test_remove_dash_3(self):
        id = '20Y1234-4'
        self.assertEqual('123404',self.factory.remove_dash_from_id(id))

    def test_remove_dash_4(self):
        id = '1970-6楚桃'
        self.assertEqual('197006',self.factory.remove_dash_from_id(id))

    def test_remove_dash_5(self):
        id = '1970'
        self.assertEqual('1970',self.factory.remove_dash_from_id(id))

    def test_remove_dash_6(self):
        id = '1970-12'
        self.assertEqual('197012',self.factory.remove_dash_from_id(id))

    def test_set_parent_1(self):
        # --------------------------- Not Done ------------------------------
        parent = Pig()
        parent.set_id("123456")
        parent.set_birthday("2020-02-03")
        parent.set_farm("test_farm")

        self.factory.set_birthday('2021-02-03')
        self.factory.set_parent("dam", parent.get_id())
        self.assertEqual('123456',self.factory.pig.get_dam()['id'])
        self.assertEqual(datetime.date(2020,2,3),self.factory.pig.get_dam()['birthday'])

    def test_set_parent_2(self):
        parent = 'sire'
        parent_id = '2Y123456'
        self.factory.set_birthday('2019-02-03')
        self.factory.set_parent(parent, parent_id)
        self.assertEqual(self.factory.get_flag(), self.factory.SIRE_FLAG)

    def test_naif_id_1(self):
        id = 123456
        self.factory.set_naif_id(id)
        self.assertEqual(str(id),self.factory.pig.get_naif_id())

    def test_naif_id_2(self):
        id = '123456'
        self.factory.set_naif_id(id)
        self.assertEqual(str(id),self.factory.pig.get_naif_id())

    def test_naif_id_3(self):
        id = "1234567"
        self.factory.set_naif_id(id)
        self.assertEqual(self.factory.get_flag(), self.factory.NAIF_FLAG)

    def test_naif_id_4(self):
        id = 'e234567'
        self.factory.set_naif_id(id)
        self.assertEqual('234567',self.factory.pig.get_naif_id())

    def test_set_breed_1(self):
        breed = 'y'
        self.factory.set_breed(breed)
        self.assertEqual('Y', self.factory.pig.get_breed())

    def test_set_breed_2(self):
        breed = 'York'
        self.factory.set_breed(breed)
        self.assertEqual('Y', self.factory.pig.get_breed())

    def test_set_breed_3(self):
        breed = '約克夏'
        self.factory.set_breed(breed)
        self.assertEqual('Y', self.factory.pig.get_breed())

    def test_set_breed_4(self):
        breed = 'Y'
        self.factory.set_breed(breed)
        self.assertEqual('Y', self.factory.pig.get_breed())

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