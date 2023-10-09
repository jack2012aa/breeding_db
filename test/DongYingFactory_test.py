import unittest, datetime
from tools.pig_factory import DongYingFactory, PigFactory, FactoryException

class FactoryTestCase(unittest.TestCase):

    def setUp(self):
        self.factory = DongYingFactory()

    def tearDown(self):
        self.factory = None

    def test_flag(self):
        self.factory.turn_on_flag(self.factory.BIRTHDAY_FLAG)
        self.factory.turn_on_flag(self.factory.BOAR_FLAG)
        self.assertEqual(self.factory.BOAR_FLAG | self.factory.BIRTHDAY_FLAG,self.factory.get_flag())

    def test_flag_2(self):
        self.factory.turn_on_flag(self.factory.BIRTHDAY_FLAG)
        self.factory.turn_on_flag(self.factory.BOAR_FLAG)
        self.factory.turn_off_flag(self.factory.ID_FLAG)
        self.assertEqual(self.factory.BOAR_FLAG | self.factory.BIRTHDAY_FLAG,self.factory.get_flag())
        self.factory.turn_off_flag(self.factory.BOAR_FLAG)
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

    def test_set_parent_1(self):
        parent = 'dam'
        parent_id = '2Y123456'
        self.factory.set_birthday('2021-02-03')
        self.factory.set_parent(parent, parent_id)
        self.assertEqual('123456',self.factory.pig.get_dam()['id'])
        self.assertEqual(datetime.date(2020,2,3),self.factory.pig.get_dam()['birthday'])

    def test_set_parent_2(self):
        parent = 'boar'
        parent_id = '2Y123456'
        self.factory.set_birthday('2019-02-03')
        self.assertRaises(FactoryException, self.factory.set_parent, parent,parent_id)


if __name__ == '__main__':
    unittest.main()
'''
    while True:
        f = DongYingFactory()
        f.set_id(input())
        print(f.pig.get_id())'''