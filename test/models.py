import unittest
from datetime import date, datetime

from breeding_db.models import Model
from breeding_db.data_structures import *


class ModelTest(unittest.TestCase):

    def setUp(self):
        self.model = Model("test/helper/database_settings.json")

    def tearDown(self):
        self.model._delete_all("Farrowings")
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

    def test_dict_to_estrus(self):

        estrus_dict = {
            "id": "123456", 
            "birthday": "1999-05-12", 
            "farm": "test farm", 
            "estrus_datetime": "2000-05-12 12:00:00", 
            "parity": "2", 
            "pregnant": "Unknown"
        }
        estrus = self.model.dict_to_estrus(estrus_dict)
        self.assertEqual("123456", estrus.get_sow().get_id())
        self.assertEqual(date(1999, 5, 12), estrus.get_sow().get_birthday())
        self.assertEqual("test farm", estrus.get_sow().get_farm())
        self.assertEqual(datetime(2000, 5, 12, 12, 0, 0), estrus.get_estrus_datetime())
        self.assertEqual(2, estrus.get_parity())
        self.assertEqual(PregnantStatus.UNKNOWN, estrus.get_pregnant())
        estrus_dict = {
            "birthday": "1999-05-12", 
            "farm": "test farm", 
            "estrus_datetime": "2000-05-12 12:00:00", 
            "parity": "2", 
            "pregnant": "Unknown"
        }
        self.assertIsNone(self.model.dict_to_estrus(estrus_dict))
        estrus_dict = {
            "id": "123456", 
            "birthday": "1999-05-12", 
            "farm": "test farm", 
            "parity": "2", 
            "pregnant": "Unknown"
        }
        self.assertIsNone(self.model.dict_to_estrus(estrus_dict))
        with self.assertRaises(TypeError):
            self.model.dict_to_estrus(123)

    def test_find_estrus(self):

        sow = Pig()
        sow.set_id("123456")
        sow.set_birthday("1999-05-12")
        sow.set_farm("test farm")
        estrus = Estrus()
        estrus.set_sow(sow)
        estrus.set_estrus_datetime("2000-05-12 12:00:00")
        estrus.set_pregnant(PregnantStatus("No"))
        estrus.set_parity(1)
        self.model.insert_pig(sow)
        self.model.insert_estrus(estrus)
        sow.set_id("123455")
        self.model.insert_pig(sow)
        self.model.insert_estrus(estrus)
        estrus.set_estrus_datetime("2000-11-12 12:00:00")
        self.model.insert_estrus(estrus)
        
        results = self.model.find_estrus(equal={"id": "123455"})
        self.assertEqual(2, len(results))

        results = self.model.find_estrus(smaller={"birthday": "2000-05-12"})
        self.assertEqual(3, len(results))

    def test_update_estrus(self):

        sow = Pig()
        sow.set_id("123456")
        sow.set_birthday("1999-05-12")
        sow.set_farm("test farm")
        estrus = Estrus()
        estrus.set_sow(sow)
        estrus.set_estrus_datetime("2000-05-12 12:00:00")
        estrus.set_pregnant(PregnantStatus("No"))
        estrus.set_parity(1)
        self.model.insert_pig(sow)
        self.model.insert_estrus(estrus)

        estrus.set_parity(2)
        self.model.update_estrus(estrus)
        found = self.model.find_estrus(equal={
            "id": estrus.get_sow().get_id(), "birthday": estrus.get_sow().get_birthday(), 
            "farm": estrus.get_sow().get_farm(), "estrus_datetime": estrus.get_estrus_datetime()
        })
        self.assertEqual(2, found[0].get_parity())
        estrus.set_estrus_datetime("2000-05-13 12:00:00")
        self.model.update_estrus(estrus)
        found = self.model.find_estrus(equal={
            "id": estrus.get_sow().get_id(), "birthday": estrus.get_sow().get_birthday(), 
            "farm": estrus.get_sow().get_farm(), "estrus_datetime": estrus.get_estrus_datetime()
        })
        self.assertEqual(len(found), 0)
        with self.assertRaises(ValueError):
            self.model.update_estrus(Estrus())

    def test_dict_to_mating(self):

        mating_dict = {
            "sow_id": "123455", 
            "sow_birthday": "2020-05-12", 
            "sow_farm": "test farm", 
            "estrus_datetime": "2021-05-12 12:00:00", 
            "mating_datetime": "2021-05-12 12:00:00", 
            "boar_id": "123456", 
            "boar_birthday": "2020-05-13", 
            "boar_farm": "test farm 2"
        }
        mating = self.model.dict_to_mating(mating_dict)
        self.assertEqual("123455", mating.get_estrus().get_sow().get_id())
        self.assertEqual(date(2020, 5, 12), mating.get_estrus().get_sow().get_birthday())
        self.assertEqual("test farm", mating.get_estrus().get_sow().get_farm())
        self.assertEqual(datetime(2021, 5, 12, 12), mating.get_estrus().get_estrus_datetime())
        self.assertEqual("123456", mating.get_boar().get_id())
        self.assertEqual(date(2020, 5, 13), mating.get_boar().get_birthday())
        self.assertEqual("test farm 2", mating.get_boar().get_farm())
        self.assertEqual(datetime(2021, 5, 12, 12), mating.get_mating_datetime())

        mating_dict.pop("mating_datetime")
        self.assertIsNone(self.model.dict_to_mating(mating_dict))

    def test_find_matings(self):

        sow = Pig(id="123456", birthday="2020-05-12", farm="test farm")
        estrus = Estrus(sow=sow, estrus_datetime="2021-05-12 12:00:00")
        boar = Pig(id="123455", birthday="2020-05-12", farm="test farm")
        mating = Mating(estrus=estrus, mating_datetime="2021-05-12 12:00:00", boar=boar)
        self.model.insert_pig(sow)
        self.model.insert_pig(boar)
        self.model.insert_estrus(estrus)
        self.model.insert_mating(mating)
        found = self.model.find_matings(equal={"mating_datetime": "2021-05-12 12:00:00"})
        self.assertEqual(1, len(found))

        mating = Mating(estrus=estrus, mating_datetime="2021-05-13 12:00:00", boar=boar)
        self.model.insert_mating(mating)
        found = self.model.find_matings(equal={"estrus_datetime": "2021-05-12 12:00:00"})
        self.assertEqual(2, len(found))

        with self.assertRaises(ValueError):
            self.model.find_matings()

    def test_update_mating(self):

        sow = Pig(id="123456", birthday="2020-05-12", farm="test farm")
        estrus = Estrus(sow=sow, estrus_datetime="2021-05-12 12:00:00")
        boar = Pig(id="123455", birthday="2020-05-12", farm="test farm")
        mating = Mating(estrus=estrus, mating_datetime="2021-05-12 12:00:00", boar=boar)
        self.model.insert_pig(sow)
        self.model.insert_pig(boar)
        self.model.insert_estrus(estrus)
        self.model.insert_mating(mating)
        mating.set_mating_datetime("2021-05-13 12:00:00")
        self.model.insert_mating(mating)
        boar = Pig(id="111111", birthday="2019-05-12", farm="test farm")
        self.model.insert_pig(boar)
        mating.set_boar(boar)
        self.model.update_mating(mating)
        found = self.model.find_matings(equal={"mating_datetime": "2021-05-13 12:00:00"})
        self.assertEqual("111111", found[0].get_boar().get_id())
        found = self.model.find_matings(equal={"mating_datetime": "2021-05-12 12:00:00"})
        self.assertEqual("123455", found[0].get_boar().get_id())

    def test_dict_to_farrowing(self):

        farrowing_dict = {
            "id": "123456", 
            "birthday": "1999-05-12", 
            "farm": "test farm", 
            "estrus_datetime": "2000-05-12 12:00:00", 
            "farrowing_date": "2000-09-03", 
            "crushed": 1, 
            "black": 1, 
            "weak": 1, 
            "malformation": 1, 
            "dead": 1, 
            "total_weight": 100, 
            "n_of_male": 1, 
            "n_of_female": 1, 
            "note": "HI"
        }

        farrowing = self.model.dict_to_farrowing(farrowing_dict)
        self.assertEqual("123456", farrowing.get_estrus().get_sow().get_id())
        self.assertEqual("test farm", farrowing.get_estrus().get_sow().get_farm())
        self.assertEqual(date(1999, 5, 12), farrowing.get_estrus().get_sow().get_birthday())
        self.assertEqual(datetime(2000, 5, 12, 12), farrowing.get_estrus().get_estrus_datetime())
        self.assertEqual(date(2000, 9, 3), farrowing.get_farrowing_date())
        self.assertEqual(1, farrowing.get_crushed())
        self.assertEqual(1, farrowing.get_black())
        self.assertEqual(1, farrowing.get_weak())
        self.assertEqual(1, farrowing.get_malformation())
        self.assertEqual(1, farrowing.get_dead())
        self.assertEqual(100, farrowing.get_total_weight())
        self.assertEqual(1, farrowing.get_n_of_male())
        self.assertEqual(1, farrowing.get_n_of_female())
        self.assertEqual("HI", farrowing.get_note())

        farrowing_dict.pop("estrus_datetime")
        self.assertIsNone(self.model.dict_to_farrowing(farrowing_dict))

        self.assertRaises(TypeError, self.model.dict_to_farrowing, "Hi")

    def test_get_farrowing_attributes(self):
        
        sow = Pig(id="123456", birthday="1999-05-12", farm="test farm")
        estrus = Estrus(sow, "2000-05-12 12:00:00")
        farrowing = Farrowing(
            estrus=estrus, 
            farrowing_date="2000-09-03", 
            crushed=1, 
            black=1, 
            weak=1, 
            malformation=1, 
            dead=1, 
            total_weight=100, 
            n_of_male=1, 
            n_of_female=1, 
            note="Hi"
        )
        farrowing_dict = self.model._Model__get_farrowing_attributes(farrowing)
        self.assertEqual(farrowing_dict, {
            "id": "123456", 
            "birthday": date(1999, 5, 12), 
            "farm": "test farm", 
            "estrus_datetime": datetime(2000, 5, 12, 12), 
            "farrowing_date": date(2000, 9, 3), 
            "crushed": 1, 
            "black": 1, 
            "weak": 1, 
            "malformation": 1, 
            "dead": 1, 
            "total_weight": 100, 
            "n_of_male": 1, 
            "n_of_female": 1, 
            "note": "Hi"
        })

    def test_insert_farrowing(self):

        sow = Pig(id="123456", farm="test farm", birthday="1999-05-12")
        self.model.insert_pig(sow)
        estrus = Estrus(sow=sow, estrus_datetime="2000-05-12 12:00:00")
        self.model.insert_estrus(estrus)
        farrowing = Farrowing(
            estrus=estrus, 
            farrowing_date="2000-09-03", 
            crushed=1, 
            black=1, 
            weak=1, 
            malformation=1, 
            dead=1, 
            total_weight=100, 
            n_of_male=1, 
            n_of_female=1, 
            note="Hi"            
        )
        self.model.insert_farrowing(farrowing)

    def test_find_farrowing(self):

        sow = Pig(id="123456", farm="test farm", birthday="1999-05-12")
        self.model.insert_pig(sow)
        estrus = Estrus(sow=sow, estrus_datetime="2000-05-12 12:00:00")
        self.model.insert_estrus(estrus)
        farrowing = Farrowing(
            estrus=estrus, 
            farrowing_date="2000-09-03", 
            crushed=1, 
            black=1, 
            weak=1, 
            malformation=1, 
            dead=1, 
            total_weight=100, 
            n_of_male=1, 
            n_of_female=1, 
            note="Hi"            
        )
        self.model.insert_farrowing(farrowing)
        estrus = Estrus(sow=sow, estrus_datetime="2001-05-12 12:00:00")
        self.model.insert_estrus(estrus)
        farrowing = Farrowing(
            estrus=estrus, 
            farrowing_date="2001-09-03", 
            crushed=1, 
            black=1, 
            weak=1, 
            malformation=1, 
            dead=1, 
            total_weight=100, 
            n_of_male=1, 
            n_of_female=2, 
            note="Hi"            
        )
        self.model.insert_farrowing(farrowing)
        found = self.model.find_farrowings(equal={"n_of_female": 2})
        self.assertEqual(found[0], farrowing)
        found = self.model.find_farrowings(equal={"farm": "test farm"})
        self.assertEqual(len(found), 2)

    def test_update_farrowing(self):

        
        sow = Pig(id="123456", farm="test farm", birthday="1999-05-12")
        self.model.insert_pig(sow)
        estrus = Estrus(sow=sow, estrus_datetime="2000-05-12 12:00:00")
        self.model.insert_estrus(estrus)
        farrowing = Farrowing(
            estrus=estrus, 
            farrowing_date="2000-09-03", 
            crushed=1, 
            black=1, 
            weak=1, 
            malformation=1, 
            dead=1, 
            total_weight=100, 
            n_of_male=1, 
            n_of_female=1, 
            note="Hi"            
        )
        self.model.insert_farrowing(farrowing)
        farrowing = Farrowing(
            estrus=estrus, 
            farrowing_date="2000-09-03", 
            crushed=1, 
            black=1, 
            weak=1, 
            malformation=1, 
            dead=1, 
            total_weight=200, 
            n_of_male=1, 
            n_of_female=1, 
            note="Hi"            
        )
        self.model.update_farrowing(farrowing)
        found = self.model.find_farrowings(equal={"farm": "test farm"})
        self.assertEqual(200, found[0].get_total_weight())
        self.assertRaises(TypeError, self.model.update_farrowing, "123456")


if __name__ == '__main__':
    unittest.main()