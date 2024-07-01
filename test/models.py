import unittest

from breeding_db.models import Model
from breeding_db.data_structures import *


class ModelTest(unittest.TestCase):

    def setUp(self):
        self.model = Model("test/helper/database_settings.json")

    def tearDown(self):
        self.model._delete_all("Matings")
        self.model._delete_all("Estrus")
        self.model._delete_all("Pigs")
        self.model = None

    def test_connection(self):
        self.model._Model__query("SHOW TABLES;")

    def test_get_pig_attributes(self):

        pig = Pig()
        pig.set_id("123456")
        pig.set_birthday("1999-05-12")
        pig.set_farm("test_farm")
        pig.set_breed("L")
        pig.set_reg_id("111111")
        pig.set_gender("1")
        pig.set_chinese_name("你好")
        dam = Pig()
        dam.set_id("000000")
        dam.set_birthday("1998-05-12")
        dam.set_farm("test_farm")
        sire = Pig()
        sire.set_id("999999")
        sire.set_birthday("1998-05-12")
        sire.set_farm("test_farm")
        pig.set_dam(dam)
        pig.set_sire(sire)
        attributes = self.model._Model__get_pig_attributes(pig)
        self.assertEqual("123456", attributes["id"])
        self.assertEqual("1999-05-12", attributes["birthday"])
        self.assertEqual("test_farm", attributes["farm"])
        self.assertEqual("L", attributes["breed"])
        self.assertEqual("111111", attributes["reg_id"])
        self.assertEqual("M", attributes["gender"])
        self.assertEqual("你好", attributes["chinese_name"])
        self.assertEqual("000000", attributes["dam_id"])
        self.assertEqual("1998-05-12", attributes["dam_birthday"])
        self.assertEqual("test_farm", attributes["dam_farm"])
        self.assertEqual("999999", attributes["sire_id"])
        self.assertEqual("1998-05-12", attributes["sire_birthday"])
        self.assertEqual("test_farm", attributes["sire_farm"])

    def test_insert_pig(self):

        pig = Pig()
        pig.set_id("123456")
        pig.set_birthday("2022-12-17")
        with self.assertRaises(ValueError):
            self.model.insert_pig(pig)

        pig.set_farm("test_farm")
        pig.set_reg_id("111111")
        self.model.insert_pig(pig)

    def test_dict_to_pig(self):

        pig = Pig()
        pig.set_id("123456")
        pig.set_birthday("1999-05-12")
        pig.set_farm("test_farm")
        pig.set_breed("L")
        pig.set_reg_id("111111")
        pig.set_gender("1")
        pig.set_chinese_name("你好")
        dam = Pig()
        dam.set_id("000000")
        dam.set_birthday("1998-05-12")
        dam.set_farm("test_farm")
        sire = Pig()
        sire.set_id("999999")
        sire.set_birthday("1998-05-12")
        sire.set_farm("test_farm")
        pig.set_dam(dam)
        pig.set_sire(sire)
        attributes = self.model._Model__get_pig_attributes(pig)
        return_pig = self.model.dict_to_pig(attributes)
        self.assertEqual(pig, return_pig)

        self.assertIsNone(self.model.dict_to_pig({"id": "111111"}))
        with self.assertRaises(KeyError):
            self.model.dict_to_pig({"sire_id": "123456"})
        with self.assertRaises(KeyError):
            self.model.dict_to_pig({"dam_id": "123456"})

    def test_find_pig(self):

        pig = Pig()
        with self.assertRaises(ValueError):
            pig.set_id("123456")
            self.model.find_pig(pig)

        pig.set_birthday("2022-12-17")
        pig.set_farm("test_farm")
        pig.set_reg_id("111111")
        self.model.insert_pig(pig)
        returned_pig = self.model.find_pig(pig)
        self.assertEqual(pig, returned_pig)

    def test_update_pig(self):

        pig = Pig()
        pig.set_id("123456")
        pig.set_birthday("2022-05-12")
        pig.set_farm("test farm")
        self.model.insert_pig(pig)
        pig.set_gender("F")
        self.model.update_pig(pig)
        returned_pig = self.model.find_pig(pig)
        self.assertEqual(pig, returned_pig)

        with self.assertRaises(ValueError):
            self.model.update_pig(Pig())

    def test_insert_estrus(self):

        pig = Pig()
        pig.set_id("123456")
        pig.set_birthday("2022-05-12")
        pig.set_farm("test farm")
        estrus = Estrus()
        estrus.set_sow(pig)

        with self.assertRaises(ValueError):
            self.model.insert_estrus(estrus)

        estrus.set_estrus_datetime("2023-05-12 12:00:00")
        estrus.set_parity(1)

        with self.assertRaises(KeyError):
            self.model.insert_estrus(estrus)

        self.model.insert_pig(pig)
        self.model.insert_estrus(estrus)

    def test_insert_mating(self):

        sow = Pig()
        sow.set_id("123456")
        sow.set_birthday("1999-05-12")
        sow.set_farm("test farm")
        estrus = Estrus()
        estrus.set_sow(sow)
        estrus.set_estrus_datetime("2000-05-12 12:00:00")
        mating = Mating()
        mating.set_estrus(estrus)

        with self.assertRaises(ValueError):
            self.model.insert_mating(mating)

        boar = Pig()
        boar.set_id("123336")
        boar.set_birthday("1999-05-12")
        boar.set_farm("test farm")
        mating.set_boar(boar)
        mating.set_mating_datetime("2000-05-13 12:00:00")

        with self.assertRaises(KeyError):
            self.model.insert_mating(mating)

        self.model.insert_pig(sow)
        self.model.insert_pig(boar)
        self.model.insert_estrus(estrus)
        self.model.insert_mating(mating)


if __name__ == '__main__':
    unittest.main()