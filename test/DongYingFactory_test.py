import unittest
from factory.pig_factory import DongYingFactory, PigFactory, FactoryException

class FactoryTestCase(unittest.TestCase):

    def setUp(self):
        self.factory = DongYingFactory()

    def tearDown(self):
        self.factory = None

    def test_flag(self):
        self.factory.turn_on_breed_review_flag()
        self.assertEqual(1,self.factory.get_flag())

    def test_flag_2(self):
        self.factory.turn_on_breed_review_flag()
        self.factory.turn_on_id_review_flag()
        self.assertEqual(3,self.factory.get_flag())

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

if __name__ == '__main__':
    unittest.main()
'''
    while True:
        f = DongYingFactory()
        f.set_id(input())
        print(f.pig.get_id())'''