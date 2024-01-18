import unittest

from data_structures.pig import Pig
from data_structures.estrus import Estrus
from data_structures.estrus import PregnantStatus
from models.pig_model import PigModel
from models.estrus_model import EstrusModel

class ModelTest(unittest.TestCase):

    def setUp(self):
        # Insert some data.
        self.model = EstrusModel()
        estrus = Estrus()
        sow = Pig()
        sow.set_id("112211")
        sow.set_birthday("2021-05-12")
        sow.set_farm("test")
        PigModel().insert(sow)
        estrus.set_sow(sow)
        estrus.set_estrus_datetime("2022-06-03 15:00:00")
        estrus.set_parity(3)
        estrus.set_pregnant(PregnantStatus.YES)
        self.model.insert(estrus)

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
        self.assertEqual(2, self.model.query("SELECT COUNT(*) FROM Estrus;")[0]["COUNT(*)"])

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

    def test_find_multiple(self):

        self.assertEqual(
            PregnantStatus.YES,
            self.model.find_multiple(equal={"id":"112211"})[0].get_pregnant()
        )


    def test_correctly_update_pregnant(self):

        estrus = Estrus()
        sow = Pig()
        sow.set_id("112211")
        sow.set_birthday("2021-05-12")
        sow.set_farm("test")
        estrus.set_sow(sow)
        estrus.set_estrus_datetime("2022-06-03 15:00:00")
        estrus.set_pregnant(PregnantStatus.ABORTION)
        self.model.update_pregnant(estrus, PregnantStatus.ABORTION)
        last = self.model.find_multiple(equal={"id":"112211"})[0]
        self.assertEqual(last.get_pregnant(), PregnantStatus.ABORTION)

    def test_update_error(self):

        estrus = Estrus()
        sow = Pig()
        sow.set_id("112231")
        sow.set_birthday("2021-05-12")
        sow.set_farm("test")
        estrus.set_sow(sow)
        self.assertRaises(ValueError, self.model.update_pregnant, estrus, PregnantStatus.ABORTION)


if __name__ == '__main__':
    unittest.main()