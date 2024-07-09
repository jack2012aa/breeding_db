import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from breeding_db.models import Model
from breeding_db.data_structures import *
from breeding_db.reader import ExcelReader
from breeding_db.general import delete_contents


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.reader = ExcelReader("test/helper/database_settings.json")
        self.model = Model("test/helper/database_settings.json")

    def tearDown(self):
        self.reader = None
        self.model._delete_all("Pigs")
        self.model._delete_all("Estrus")
        self.model._delete_all("Matings")
        self.model = None
        delete_contents("test/helper/garbage")

    def test_remove_nonnumeric(self):

        s = "Y123456"
        self.assertEqual("123456", self.reader._ExcelReader__remove_nonnumeric(s))

    def test_remove_dash_from_id(self):

        s = 123
        with self.assertRaises(TypeError):
            self.reader._ExcelReader__remove_dash_from_id(s)

        s = "1234-3"
        self.assertEqual("123403", self.reader._ExcelReader__remove_dash_from_id(s))
        s = "1234-12"
        self.assertEqual("123412", self.reader._ExcelReader__remove_dash_from_id(s))
        s = "1234-3-2"
        self.assertEqual("123403", self.reader._ExcelReader__remove_dash_from_id(s))
        s = "20Y123413"
        self.assertEqual("123413", self.reader._ExcelReader__remove_dash_from_id(s))
        s = "123456cao"
        self.assertEqual("123456", self.reader._ExcelReader__remove_dash_from_id(s))
        s = "123456.0"
        self.assertEqual("123456", self.reader._ExcelReader__remove_dash_from_id(s))

    @patch("breeding_db.reader.ask")
    def test_read_and_insert_pigs(self, mock_ask):

        mock_ask.return_value = True
        self.reader.read_and_insert_pigs(
            farm="test farm", 
            input_path="test/helper/pig_data/pig_ancestors.xlsx", 
            output_path="test/helper/garbage", 
            allow_none=True
        )
        self.assertEqual(100, len(self.model.find_pigs(equal={"farm":"test farm"})))
        output_dataframe = pd.read_csv("test/helper/garbage/output.csv")
        self.assertEqual(0, output_dataframe.size)
        self.reader.read_and_insert_pigs(
            farm="test farm", 
            input_path="test/helper/pig_data/pigs.xlsx", 
            output_path="test/helper/garbage", 
            output_filename="output2.csv"
        )

        # Test repeat id pig.
        pig = Pig()
        pig.set_birthday("2026-09-22")
        pig.set_id("289213")
        pig.set_farm("test farm")
        pig = self.model.find_pig(pig)
        self.assertEqual(pig.get_reg_id(), None)

        output_dataframe = pd.read_csv("test/helper/garbage/output2.csv")
        self.assertEqual(14, output_dataframe.shape[0])
        # 109 rows in pigs.xlsx and 13 errors.
        self.assertEqual(100 + 109 - 13, len(self.model.find_pigs(equal={"farm":"test farm"})))

    def test_seperate_year_breed_id(self):

        id = "19Y1234-06"
        year, breed, id = self.reader._ExcelReader__seperate_year_breed_id(id)
        self.assertEqual("2019", year)
        self.assertEqual("Y",breed)
        self.assertEqual(id, "123406")

        id = "F<204>"
        year, breed, id = self.reader._ExcelReader__seperate_year_breed_id(id)
        self.assertEqual(id, "204")

        with self.assertRaises(TypeError):
            year, breed, id = self.reader._ExcelReader__seperate_year_breed_id(1234)
        
        with self.assertRaises(ValueError):
            id = "20Y202034Y39"
            year, breed, id = self.reader._ExcelReader__seperate_year_breed_id(id)

    @patch("breeding_db.reader.ask")
    def test_read_and_insert_estrus(self, mock_ask):

        mock_ask.return_value = True
        self.reader.read_and_insert_pigs(
            farm="test farm", 
            input_path="test/helper/estrus_data/estrus_data.xlsx", 
            output_path="test/helper/garbage", 
            output_filename="output1.csv", 
            allow_none=True
        )
        self.reader.read_and_insert_estrus(
            farm="test farm", 
            input_path="test/helper/estrus_data/estrus_data.xlsx", 
            output_path="test/helper/garbage",
            output_filename="output2.csv"
        )
        found = self.model.find_estrus(equal={"farm": "test farm"})
        self.assertEqual(52, len(found))
        error = pd.read_csv("test/helper/garbage/output2.csv")
        self.assertEqual(6, error.shape[0])

    @patch("breeding_db.reader.ask")
    def test_read_and_insert_matings(self, mock_ask):

        mock_ask.return_value = True
        self.reader.read_and_insert_pigs(
            farm="test farm", 
            input_path="test/helper/mating_data/mating_data.xlsx", 
            output_path="test/helper/garbage", 
            output_filename="output1.csv", 
            allow_none=True
        )
        self.reader.read_and_insert_estrus(
            farm="test farm", 
            input_path="test/helper/mating_data/mating_data.xlsx", 
            output_path="test/helper/garbage", 
            output_filename="output2.csv"
        )
        self.reader.read_and_insert_matings(
            farm="test farm", 
            input_path="test/helper/mating_data/mating_data.xlsx", 
            output_path="test/helper/garbage", 
            output_filename="output3.csv"
        )

        # Test pregnant status
        found = self.model.find_estrus(equal={
            "id": "171403", 
            "birthday": "2018-01-17", 
            "farm": "test farm", 
            "estrus_datetime": "2019-01-20 12:00:00"
        })
        self.assertEqual(PregnantStatus.NO, found[0].get_pregnant())
        found = self.model.find_estrus(equal={
            "id": "158005", 
            "birthday": "2020-04-27", 
            "farm": "test farm", 
            "estrus_datetime": "2020-11-01 12:00:00"
        })
        self.assertEqual(PregnantStatus.ABORTION, found[0].get_pregnant())
        found = self.model.find_matings(equal={"sow_farm": "test farm"})
        self.assertEqual(52, len(found))
        dataframe = pd.read_csv("test/helper/garbage/output3.csv")
        self.assertEqual(5, dataframe.shape[0])

    @patch("breeding_db.reader.ask")
    def test_read_and_insert_matings(self, mock_ask):

        mock_ask.return_value = True
        self.reader.read_and_insert_pigs(
            farm="test farm", 
            input_path="test/helper/farrowing_data/farrowing_data.xlsx", 
            output_filename="output1.csv", 
            output_path="test/helper/garbage", 
            allow_none=True
        )
        self.reader.read_and_insert_estrus(
            farm="test farm", 
            input_path="test/helper/farrowing_data/farrowing_data.xlsx", 
            output_filename="output2.csv", 
            output_path="test/helper/garbage"
        )
        self.reader.read_and_insert_farrowings(
            farm="test farm", 
            input_path="test/helper/farrowing_data/farrowing_data.xlsx", 
            output_filename="output3.csv", 
            output_path="test/helper/garbage"
        )
        
        found = self.model.find_farrowings(equal={"farm": "test farm"})
        self.assertEqual(49, len(found))
        dataframe = pd.read_csv("test/helper/garbage/output3.csv")
        self.assertEqual(13, dataframe.shape[0])


if __name__ == '__main__':
    unittest.main()