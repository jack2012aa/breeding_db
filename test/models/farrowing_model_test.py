import unittest

from data_structures.pig import Pig
from data_structures.estrus import Estrus
from data_structures.farrowing import Farrowing
from models.pig_model import PigModel
from models.estrus_model import EstrusModel
from models.farrowing_model import FarrowingModel

class ModelTest(unittest.TestCase):

    def setUp(self):
        # Insert some data.
        self.model = FarrowingModel()
        estrus = Estrus()
        sow = Pig()
        sow.set_id("112211")
        sow.set_birthday("2021-05-12")
        sow.set_farm("test")
        sow.set_gender("F")
        PigModel().insert(sow)
        estrus.set_sow(sow)
        estrus.set_estrus_datetime("2022-06-03 15:00:00")
        estrus.set_parity(3)
        EstrusModel().insert(estrus)

    def tearDown(self):
        self.model.delete_all("Pigs")
        self.model.delete_all("Estrus")
        self.model.delete_all("Farrowings")
        self.model = None

    def test_correctly_insert(self):

        estrus = Estrus()
        sow = Pig()
        sow.set_id("112211")
        sow.set_birthday("2021-05-12")
        sow.set_farm("test")
        sow.set_gender("F")
        estrus.set_sow(sow)
        estrus.set_estrus_datetime("2022-06-03 15:00:00")
        estrus.set_parity(3)
        farrowing = Farrowing()
        farrowing.set_estrus(estrus)
        farrowing.set_black(2)
        farrowing.set_farrowing_date("2023-01-04")
        farrowing.set_malformation(1)
        farrowing.set_n_of_male(5)
        farrowing.set_n_of_female(6)
        self.model.insert(farrowing)
        input("Stop")
        self.assertEqual(1, self.model.query("SELECT COUNT(*) FROM Farrowings;")[0]["COUNT(*)"])


if __name__ == '__main__':
    unittest.main()