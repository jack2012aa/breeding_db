import unittest

from factory.dong_ying_factory import DongYingEstrusFactory
from models.pig_model import PigModel
from data_structures.pig import Pig
from data_structures.estrus import PregnantStatus

class FactoryTestCase(unittest.TestCase):

    def setUp(self):

        self.factory = DongYingEstrusFactory()
        self.model = PigModel()

        # Insert some pigs
        pig = Pig()
        pig.set_id("123456")
        pig.set_birthday("2022-01-03")
        pig.set_farm("Dong-Ying")
        pig.set_gender("F")
        self.model.insert(pig)
        pig.set_birthday("2000-01-03")
        self.model.insert(pig)
        pig.set_birthday("2023-01-03")
        self.model.insert(pig)

    def tearDown(self):
        self.factory = None
        self.model.delete_all("Pigs")
        self.model = None

    def test_set_sow_type_error(self):

        self.assertRaises(TypeError, self.factory.set_sow, None, "1234")
        self.assertRaises(TypeError, self.factory.set_sow, "None", 1234)

    def test_correctly_set_sow(self):

        pig = Pig()
        pig.set_id("22L123456")
        pig.set_birthday("2022-01-03")
        pig.set_farm("Dong-Ying")
        pig.set_gender("F")
        # Change the id into different Dong-Ying's styles
        self.factory.set_sow(pig.get_id(), "2023-01-03")
        self.assertEqual(self.factory.estrus.get_sow().get_id(), "123456")
        self.assertEqual(self.factory.estrus.get_sow().get_birthday(), pig.get_birthday())
        pig.set_id("<123456>")
        self.factory.set_sow(pig.get_id(), "2023-01-03")
        self.assertEqual(self.factory.estrus.get_sow().get_id(), "123456")
        self.assertEqual(self.factory.estrus.get_sow().get_birthday(), pig.get_birthday())

    def test_set_sow_date_format_error(self):

        self.factory.set_sow("123456", "2023/01/03")
        self.assertEqual(self.factory.get_flag(), self.factory.SOW_FLAG | self.factory.ESTRUS_DATE_FLAG)

    def test_set_sow_id_not_found(self):

        self.factory.set_sow("123444", "2021-01-01") 
        self.assertEqual(self.factory.get_flag(), self.factory.SOW_FLAG)

    def test_set_date_type_error(self):

        self.assertRaises(TypeError, self.factory.set_estrus_datetime, 123, "213")
        self.assertRaises(TypeError, self.factory.set_estrus_datetime, "123", 123)

    def test_correctly_set_date(self):

        self.factory.set_estrus_datetime("2021-02-23", "16:00")
        self.assertEqual(str(self.factory.estrus.get_estrus_datetime()), "2021-02-23 16:00:00")

    def test_set_date_format_error(self):

        self.factory.set_estrus_datetime("2021-02-23", "16:00:00")
        self.assertEqual(self.factory.get_flag(), self.factory.ESTRUS_DATE_FLAG)
        self.factory._turn_off_flag(self.factory.ESTRUS_DATE_FLAG)
        self.factory.set_estrus_datetime("2021/02/23", "16:00")
        self.assertEqual(self.factory.get_flag(), self.factory.ESTRUS_DATE_FLAG)

    def test_set_pregnant_status_type_error(self):

        self.assertRaises(TypeError, self.factory.set_pregnant, 12)

    def test_correctly_set_pregnant_status(self):

        self.factory.set_pregnant(PregnantStatus.NO)
        self.assertEqual(PregnantStatus.NO, self.factory.estrus.get_pregnant())

    def test_set_parity_type_error(self):

        self.assertRaises(TypeError, self.factory.set_parity, "12")

    def test_correctly_set_parity(self):

        self.factory.set_parity(3)
        self.assertEqual(3, self.factory.estrus.get_parity())

    def test_set_parity_out_of_range(self):

        self.factory.set_parity(-1)
        self.assertEqual(self.factory.get_flag(), self.factory.PARITY_FLAG)
        self.factory._turn_off_flag(self.factory.PARITY_FLAG)
        self.factory.set_parity(20)
        self.assertEqual(self.factory.get_flag(), self.factory.PARITY_FLAG)


if __name__ == '__main__':
    unittest.main()