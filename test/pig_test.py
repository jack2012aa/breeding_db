import unittest
from data_structures.pig import Pig, PigSettingException
import datetime

class PigTestCase(unittest.TestCase):

    def setUp(self):
        self.pig = Pig()

    def tearDown(self):
        self.pig = None

    def test_set_id(self):

        expect = "123456"
        self.pig.set_id(expect)
        result = self.pig.get_id()
        self.assertEqual(expect,result)

    def test_set_id_failure_1(self):
        self.assertRaises(PigSettingException, self.pig.set_id, id = '')
    
    def test_set_id_failure_2(self):
        self.assertRaises(PigSettingException, self.pig.set_id, None)

    def test_set_id_failure_3(self):
        self.assertRaises(PigSettingException, self.pig.set_id, 'asduflsdfjskabdfijaslfefiudsbufbliadbf')

    def test_set_breed(self):
        breed = 'L'
        self.pig.set_breed(breed)
        result = self.pig.get_breed()
        self.assertEqual(breed, result)

    def test_set_breed_failure(self):
        breed = "Landrace"
        self.assertRaises(PigSettingException, self.pig.set_breed, breed)

    def test_set_birthday(self):
        birthday_str = '2021-02-03'
        self.pig.set_birthday(birthday_str)
        birthday = datetime.date(2021, 2, 3)
        self.assertEqual(birthday, self.pig.get_birthday())

    def test_set_birthday_2(self):
        birthday = datetime.date(2021, 2, 3)
        self.pig.set_birthday(birthday)
        self.assertEqual(birthday, self.pig.get_birthday())

    def test_set_birthday_failure_1(self):
        birthday = '202123'
        self.assertRaises(PigSettingException, self.pig.set_birthday, birthday)

    def test_set_birthday_failure_2(self):
        birthday = 12343
        self.assertRaises(PigSettingException, self.pig.set_birthday, birthday) 
    
    def test_set_birthday_failure_1(self):
        birthday = None
        self.assertRaises(PigSettingException, self.pig.set_birthday, birthday)

    def test_set_dam_1(self):
        dam = {'id':'dsfisdif','birthday':datetime.date(2021,2,3)}
        self.pig.set_dam(dam['id'], dam['birthday'])
        self.assertEqual(dam, self.pig.get_dam())

    def test_set_dam_2(self):
        dam = {'id':'dsfisdif','birthday':datetime.date(2021,2,3)}
        self.pig.set_dam(dam['id'], '2021/02/03')
        self.assertEqual(dam, self.pig.get_dam())

    def test_set_boar_1(self):
        boar = {'id':'dsfisdif','birthday':datetime.date(2021,2,3)}
        self.pig.set_sire(boar['id'], boar['birthday'])
        self.assertEqual(boar, self.pig.get_boar())

    def test_set_boar_2(self):
        boar = {'id':'dsfisdif','birthday':datetime.date(2021,2,3)}
        self.pig.set_sire(boar['id'], '2021/02/03')
        self.assertEqual(boar, self.pig.get_boar())

    def test_set_naif_id(self):
        id = '1238342'
        self.pig.set_naif_id(id)
        self.assertEqual(str(id), self.pig.get_naif_id())

    def test_set_naif_id(self):
        id = 123424
        self.pig.set_naif_id(id)
        self.assertEqual(str(id), self.pig.get_naif_id())

    def test_set_naif_id_failure_1(self):
        id = '324dsf'
        self.assertRaises(PigSettingException, self.pig.set_naif_id, id)

    def test_set_naif_id_failure_2(self):
        id = 14324.123
        self.assertRaises(PigSettingException, self.pig.set_naif_id, id)

    def test_gender_1(self):
        gender = '公'
        self.pig.set_gender(gender)
        self.assertEqual('M',self.pig.get_gender())

    def test_gender_2(self):
        gender = 'M'
        self.pig.set_gender(gender)
        self.assertEqual('M',self.pig.get_gender())
        
    def test_gender_3(self):
        gender = '1'
        self.pig.set_gender(gender)
        self.assertEqual('M',self.pig.get_gender())

    def test_gender_4(self):
        gender = '母'
        self.pig.set_gender(gender)
        self.assertEqual('F',self.pig.get_gender())

    def test_gender_5(self):
        gender = 'F'
        self.pig.set_gender(gender)
        self.assertEqual('F',self.pig.get_gender())
        
    def test_gender_6(self):
        gender = '2'
        self.pig.set_gender(gender)
        self.assertEqual('F',self.pig.get_gender())


if __name__ == '__main__':
    unittest.main()
