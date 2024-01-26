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
        pig.set_reg_id("654321")
        self.model.insert(pig)

    def tearDown(self):
        self.model.delete_all("Pigs")
        self.model = None

    def test_insertion(self):

        # Correct insertion
        pig = Pig()
        pig.set_id("123456")
        pig.set_birthday("2022-12-27")
        pig.set_farm("test_farm")
        pig.set_reg_id("654321")
        self.model.insert(pig)
        self.assertEqual(self.model.find_pig(pig), pig)

        # Duplicate primary key
        pig.set_id("123457")
        pig.set_birthday("2022-12-27")
        pig.set_farm("test_farm")
        self.assertRaises(ValueError, self.model.insert, pig)

        # Not unique
        pig = Pig()
        pig.set_id("112233")
        self.assertRaises(TypeError, self.model.insert, pig)

        # Type Error
        pig = None
        self.assertRaises(TypeError, self.model.insert, pig)

    def test_find_pig(self):

        # Exist
        pig = Pig()
        pig.set_id("123457")
        pig.set_birthday("2022-12-27")
        pig.set_farm("test_farm")        
        self.assertEqual(pig.get_id(),self.model.find_pig(pig).get_id())
        self.assertEqual(pig.get_birthday(),self.model.find_pig(pig).get_birthday())
        self.assertEqual(pig.get_farm(),self.model.find_pig(pig).get_farm())

        # Not exist
        pig.set_id("12457")
        pig.set_birthday("2022-12-27")
        pig.set_farm("test_farm")        
        self.assertEqual(None,self.model.find_pig(pig))

        # Not unique
        pig = Pig()
        pig.set_id("112233")
        self.assertRaises(ValueError, self.model.find_pig, pig)

        # TypeErrpr
        pig = None
        self.assertRaises(TypeError, self.model.find_pig, pig)

    def test_find_pigs(self):

        # Add data
        pig = Pig()
        pig.set_id("123456")
        pig.set_birthday("2022-12-28")
        pig.set_farm("test_farm")
        pig.set_reg_id("654421")
        self.model.insert(pig)
        pig = Pig()
        pig.set_id("1234356")
        pig.set_birthday("2022-12-27")
        pig.set_farm("test_farm")
        pig.set_reg_id("654421")
        self.model.insert(pig)

        # Equal
        self.assertEqual(
            len(self.model.find_multiple({
                "reg_id": "654421", 
                "farm": "test_farm"}
                )),
            2
        )

        # Smaller
        self.assertEqual(
            len(self.model.find_multiple(
                equal={"farm": "test_farm"}, 
                smaller={"birthday": "2022-12-28"})),
            2
        )

        # Smaller Equal
        self.assertEqual(
            len(self.model.find_multiple(
                smaller_equal={"birthday": "2022-12-28"}
            )),
            3
        )

        # Larger
        self.assertEqual(
            len(self.model.find_multiple(
                larger={"birthday": "2022-12-27"}
            )),
            1
        )

        # Larger Equal
        self.assertEqual(
            len(self.model.find_multiple(
                larger_equal={"birthday": "2022-12-27"}
            )),
            3
        )

        # Empty set
        self.assertEqual(
            len(self.model.find_multiple(
                equal={"id": "jasdii"}
            )),
            0
        )

        # Error
        self.assertRaises(TypeError, self.model.find_multiple, equal=None)
        self.assertRaises(TypeError, self.model.find_multiple, smaller=None)
        self.assertRaises(TypeError, self.model.find_multiple, larger=None)
        self.assertRaises(TypeError, self.model.find_multiple, smaller_equal=None)
        self.assertRaises(TypeError, self.model.find_multiple, larger_equal=None)
        self.assertRaises(ValueError, self.model.find_multiple, smaller={})

    def test_update(self):

        pig = Pig()
        pig.set_id("123457")
        pig.set_birthday("2022-12-27")
        pig.set_farm("test_farm")
        pig.set_chinese_name("65")
        self.model.update(pig)
        self.assertEqual(self.model.find_pig(pig).get_chinese_name(), "65")

        # Nothing happens
        pig.set_id("asdffg")
        self.model.update(pig)

        # Error
        pig = Pig()
        pig.set_id("233")
        self.assertRaises(ValueError, self.model.update, pig)
        self.assertRaises(TypeError, self.model.update, None)

if __name__ == '__main__':
    unittest.main()