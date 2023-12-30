import unittest
import datetime

from data_structures.pig import Pig

class PigTestCase(unittest.TestCase):

    def setUp(self):
        self.pig = Pig()

    def tearDown(self):
        self.pig = None

    def test_set_id(self):

        self.pig.set_id("123456")
        self.assertEqual(self.pig.get_id(),"123456")

        # Length Error
        self.assertRaises(ValueError, self.pig.set_id, id = '')
        self.assertRaises(ValueError, self.pig.set_id, 'asduflsdfjskabdfijaslfefiudsbufbliadbf')

        # TypeError
        self.assertRaises(TypeError, self.pig.set_id, None)

    def test_set_breed(self):

        self.pig.set_breed("L")
        self.assertEqual("L", self.pig.get_breed())
        self.pig.set_breed("藍瑞斯")
        self.assertEqual("L", self.pig.get_breed())
        breed = "Landrace"
        self.assertRaises(ValueError, self.pig.set_breed, breed)
        self.assertRaises(TypeError, self.pig.set_breed, None)

    def test_set_birthday(self):

        self.pig.set_birthday("2021-02-03")
        self.assertEqual(datetime.date(2021, 2, 3), self.pig.get_birthday())
        birthday = datetime.date(2021, 2, 3)
        self.pig.set_birthday(birthday)
        self.assertEqual(birthday, self.pig.get_birthday())

        # Error
        self.assertRaises(ValueError, self.pig.set_birthday, "2021.12.03")
        self.assertRaises(TypeError, self.pig.set_birthday, 123456) 
        self.assertRaises(TypeError, self.pig.set_birthday, None)

    def test_set_dam(self):

        dam = Pig()
        dam.set_id("dsfisdif")
        dam.set_birthday("2021-02-03")
        dam.set_farm("test_farm")
        self.pig.set_dam(dam)
        self.assertEqual(dam, self.pig.get_dam())
        dam = Pig()
        dam.set_id("dsfisdif")
        dam.set_birthday("2021-02-03")
        self.assertRaises(ValueError, self.pig.set_dam, dam)
        self.assertRaises(TypeError, self.pig.set_dam, None)

    def test_set_sire(self):

        sire = Pig()
        sire.set_id("dsfisdif")
        sire.set_birthday("2021-02-03")
        sire.set_farm("test_farm")
        self.pig.set_sire(sire)
        self.assertEqual(sire, self.pig.get_sire())
        sire = Pig()
        sire.set_id("dsfisdif")
        sire.set_birthday("2021-02-03")
        self.assertRaises(ValueError, self.pig.set_sire, sire)
        sire = None
        self.assertRaises(TypeError, self.pig.set_sire, sire)

    def test_set_naif_id(self):

        self.pig.set_naif_id("123456")
        self.assertEqual("123456", self.pig.get_naif_id())

        self.assertRaises(ValueError, self.pig.set_naif_id, "324dsf")
        self.assertRaises(TypeError, self.pig.set_naif_id, 12345)
        self.assertRaises(ValueError, self.pig.set_naif_id, "1234567")

    def test_gender(self):

        self.pig.set_gender("公")
        self.assertEqual("M",self.pig.get_gender())
        self.pig.set_gender("M")
        self.assertEqual("M",self.pig.get_gender())
        self.pig.set_gender("1")
        self.assertEqual("M",self.pig.get_gender())
        self.assertRaises(KeyError, self.pig.set_gender, None)

    def test_set_chinese_name(self):

        self.pig.set_chinese_name("你好")
        self.assertEqual("你好", self.pig.get_chinese_name())
        self.assertRaises(TypeError, self.pig.set_chinese_name, None)
        self.assertRaises(ValueError, self.pig.set_chinese_name, "你好恭喜發財")

    def set_farm(self):

        self.pig.set_farm("Dong-Ying")
        self.assertEqual("Dong-Ying", self.pig.get_farm())
        self.assertRaises(TypeError, self.pig.set_farm, None)

    def test_equality(self):

        pig1 = Pig()
        pig1.set_id("123456")
        pig1.set_birthday("2023-02-02")
        pig2 = Pig()
        pig2.set_id("123456")
        pig2.set_birthday("2023-02-02")
        self.assertEqual(True, pig1 == pig2)
        pig2.set_farm("Dong-Ying")
        self.assertEqual(False, pig1 == pig2)
        self.assertRaises(TypeError, pig1.__eq__, None)

if __name__ == '__main__':
    unittest.main()
