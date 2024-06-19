import unittest

from breeding_db.data_structures import Pig
from breeding_db.data_structures import Estrus
from breeding_db.data_structures import Mating
from models.pig_model import PigModel
from models.estrus_model import EstrusModel
from models.mating_model import MatingModel

class ModelTest(unittest.TestCase):

    def setUp(self):

        # Insert some data.
        self.model = MatingModel()
        pig_model = PigModel()
        pig = Pig()
        pig.set_id("111111")
        pig.set_birthday("2019-10-23")
        pig.set_farm("test")
        pig.set_gender("M")
        pig_model.insert(pig)
        pig.set_id("222222")
        pig.set_gender("F")
        pig_model.insert(pig)
        estrus_model = EstrusModel()
        self.estrus = Estrus()
        self.estrus.set_sow(pig)
        self.estrus.set_estrus_datetime("2023-04-13 05:00:00")
        estrus_model.insert(self.estrus)

    def tearDown(self):
        self.model.delete_all("Pigs")
        self.model.delete_all("Estrus")
        self.model.delete_all("Matings")
        self.model = None

    def test_correctly_insert(self):

        mating = Mating()
        mating.set_estrus(self.estrus)
        mating.set_mating_datetime("2023-04-13 06:00:00")
        boar = Pig()
        boar.set_id("111111")
        boar.set_birthday("2019-10-23")
        boar.set_farm("test")
        mating.set_boar(boar)
        self.model.insert(mating)
        self.assertEqual(1, self.model.query("SELECT COUNT(*) FROM Matings;")[0]["COUNT(*)"])

    def test_insertion_error(self):

        mating = Mating()
        mating.set_estrus(self.estrus)
        self.assertRaises(ValueError, self.model.insert, mating)
        mating.set_mating_datetime("2023-01-01 16:00:00")
        pig = Pig()
        pig.set_id("333333")
        pig.set_birthday("2020-09-08")
        pig.set_farm("test")
        mating.set_boar(pig)
        self.assertRaises(KeyError, self.model.insert, pig)


if __name__ == '__main__':
    unittest.main()