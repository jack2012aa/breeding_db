import unittest

from data_structures.pig import Pig
from models.pig_model import PigModel

class ModelTest(unittest.TestCase):

    def setUp(self):
        # Insert some data.
        self.model = PigModel()
        pig = Pig()
        pig.set_id("123457")
        pig.set_birthday("2022-12-27")
        pig.set_farm("test_farm")
        pig.set_naif_id("654321")
        self.model.insert(pig)

    def tearDown(self):
        self.model.delete_all()
        self.model = None

    def test_insertion_1(self):
        pig = Pig()
        pig.set_id("123456")
        pig.set_birthday("2022-12-27")
        pig.set_farm("test_farm")
        pig.set_naif_id("654321")
        self.model.insert(pig)
        self.model.find_all()

    def test_insertion_failure_1(self):
        pig = Pig()
        pig.set_id("123457")
        pig.set_birthday("2022-12-27")
        pig.set_farm("test_farm")
        self.assertRaises(ValueError, self.model.insert, pig)

    def test_insertion_failure_2(self):
        pig = Pig()
        pig.set_id("123457")
        pig.set_birthday("2022-12-27")
        self.assertRaises(TypeError, self.model.insert, pig)

    def test_find_1(self):
        pig = Pig()
        pig.set_id("123457")
        pig.set_birthday("2022-12-27")
        pig.set_farm("test_farm")        
        self.assertEqual(pig.get_id(),self.model.find_pig(pig).get_id())
        self.assertEqual(pig.get_birthday(),self.model.find_pig(pig).get_birthday())
        self.assertEqual(pig.get_farm(),self.model.find_pig(pig).get_farm())

    def test_find_2(self):
        pig = Pig()
        pig.set_id("12457")
        pig.set_birthday("2022-12-27")
        pig.set_farm("test_farm")        
        self.assertEqual(None,self.model.find_pig(pig))

    def test_find_pigs(self):
        pig = Pig()
        pig.set_id("123456")
        pig.set_birthday("2022-12-28")
        pig.set_farm("test_farm")
        pig.set_naif_id("654421")
        self.model.insert(pig)
        pig = Pig()
        pig.set_id("1234356")
        pig.set_birthday("2022-12-27")
        pig.set_farm("test_farm")
        pig.set_naif_id("654421")
        self.model.insert(pig)
        self.assertEqual(len(self.model.find_pigs({"naif_id": "654421", "farm": "test_farm"})),2)
        self.assertEqual(len(self.model.find_pigs(equal={"farm": "test_farm"}, smaller={"birthday": "2022-12-28"})),2)

if __name__ == '__main__':
    unittest.main()