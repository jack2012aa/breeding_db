import unittest

from breeding_db.data_structures import Pig
from breeding_db.data_structures import Estrus
from breeding_db.data_structures import PregnantStatus
from models.pig_model import PigModel
from models.estrus_model import EstrusModel

class ModelTest(unittest.TestCase):

    def setUp(self):
        # Insert some data.
        self.model = EstrusModel()


    def tearDown(self):
        self.model.delete_all("Pigs")
        self.model.delete_all("Estrus")
        self.model = None

    def test_correctly_insert(self):

        estrus = Estrus()
        pig_model = PigModel()
        pig = Pig()
        pig.set_id("123456")
        pig.set_farm("test")
        pig.set_birthday("2021-02-02")
        pig_model.insert(pig)
        estrus.set_sow(pig)
        estrus.set_estrus_datetime("2023-01-01 16:00:00")
        estrus.set_parity(3)
        estrus.set_pregnant(PregnantStatus.NO)
        self.model.insert(estrus)
        self.assertEqual(1, self.model.query("SELECT COUNT(*) FROM Estrus;")[0]["COUNT(*)"])

    def test_insertion_error(self):

        pig = Pig()    
        pig.set_id("123456")
        pig.set_farm("test")
        pig.set_birthday("2021-02-02")
        estrus = Estrus()
        estrus.set_sow(pig)
        self.assertRaises(ValueError, self.model.insert, estrus)
        estrus.set_estrus_datetime("2023-01-01 16:00:00")
        estrus.set_parity(3)
        estrus.set_pregnant(PregnantStatus.NO)
        self.assertRaises(KeyError, self.model.insert, estrus)


if __name__ == '__main__':
    unittest.main()