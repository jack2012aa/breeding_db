import unittest
import datetime

from data_structures.pig import Pig

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
        self.assertRaises(ValueError, self.pig.set_id, id = '')
    
    def test_set_id_failure_2(self):
        self.assertRaises(TypeError, self.pig.set_id, None)

    def test_set_id_failure_3(self):
        self.assertRaises(ValueError, self.pig.set_id, 'asduflsdfjskabdfijaslfefiudsbufbliadbf')

    def test_set_breed(self):
        breed = 'L'
        self.pig.set_breed(breed)
        result = self.pig.get_breed()
        self.assertEqual(breed, result)

    def test_set_breed_failure(self):
        breed = "Landrace"
        self.assertRaises(ValueError, self.pig.set_breed, breed)

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
        self.assertRaises(ValueError, self.pig.set_birthday, birthday)

    def test_set_birthday_failure_2(self):
        birthday = 12343
        self.assertRaises(TypeError, self.pig.set_birthday, birthday) 
    
    def test_set_birthday_failure_3(self):
        birthday = None
        self.assertRaises(TypeError, self.pig.set_birthday, birthday)

    def test_set_dam_1(self):
        dam = Pig()
        dam.set_id("dsfisdif")
        dam.set_birthday("2021-02-03")
        dam.set_farm("test_farm")
        self.pig.set_dam(dam)
        self.assertEqual(dam, self.pig.get_dam())

    def test_set_dam_failure_1(self):
        dam = Pig()
        dam.set_id("dsfisdif")
        dam.set_birthday("2021-02-03")
        self.assertRaises(ValueError, self.pig.set_dam, dam)

    def test_set_dam_failure_2(self):
        dam = None
        self.assertRaises(TypeError, self.pig.set_dam, dam)

    def test_set_sire_1(self):
        sire = Pig()
        sire.set_id("dsfisdif")
        sire.set_birthday("2021-02-03")
        sire.set_farm("test_farm")
        self.pig.set_sire(sire)
        self.assertEqual(sire, self.pig.get_sire())

    def test_set_sire_failure_2(self):
        sire = Pig()
        sire.set_id("dsfisdif")
        sire.set_birthday("2021-02-03")
        self.assertRaises(ValueError, self.pig.set_sire, sire)

    def test_set_sire_failure_2(self):
        sire = None
        self.assertRaises(TypeError, self.pig.set_sire, sire)

    def test_set_naif_id_1(self):
        id = '123456'
        self.pig.set_naif_id(id)
        self.assertEqual(str(id), self.pig.get_naif_id())

    def test_set_naif_id_failure_1(self):
        id = '324dsf'
        self.assertRaises(ValueError, self.pig.set_naif_id, id)

    def test_set_naif_id_failure_2(self):
        id = 14324.123
        self.assertRaises(TypeError, self.pig.set_naif_id, id)

    def test_set_naif_id_failure_3(self):
        id = '1234567'
        self.assertRaises(ValueError, self.pig.set_naif_id, id)

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

    def test_equality(self):
        pig1 = Pig()
        pig1.set_id("123456")
        pig1.set_birthday("2023-02-02")
        pig2 = Pig()
        pig2.set_id("123456")
        pig2.set_birthday("2023-02-02")
        self.assertEqual(True, pig1 == pig2)

if __name__ == '__main__':
    unittest.main()
