import unittest

from data_structures.pig import Pig
from models.pig import PigModel

class ReaderTest(unittest.TestCase):

    def setUp(self):
        # Insert some appropriate data.
        # ---------------------------- Not done ----------------------------------------
        self.model = PigModel()

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

if __name__ == '__main__':
    unittest.main()