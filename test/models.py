import unittest
from datetime import date, datetime

from breeding_db.models import Model
from breeding_db.data_structures import *


class ModelTest(unittest.TestCase):

    def setUp(self):
        self.model = Model("test/helper/database_settings.json")

    def tearDown(self):
        self.model._delete_all("Individuals")
        self.model._delete_all("Weanings")
        self.model._delete_all("Farrowings")
        self.model._delete_all("Matings")
        self.model._delete_all("Estrus")
        self.model._delete_all("Pigs")
        self.model = None

    def test_generate_query_string(self):

        equal = {"id": "123456"}
        larger = {"birthday": "1999-05-12"}
        smaller = {"farrowing_date": "2002-09-03"}
        smaller_equal = {"estrus_datetime": "2002-09-03 12:00:00"}
        larger_equal = {"total_weight": 100}
        
        got = self.model._Model__generate_qeury_string("Test", equal, larger, smaller, larger_equal, smaller_equal, "birthday DESC")
        sql_query = "SELECT * FROM Test WHERE id='123456' AND "
        sql_query += "birthday>'1999-05-12' AND farrowing_date<'2002-09-03' "
        sql_query += "AND total_weight>='100' AND estrus_datetime<="
        sql_query += "'2002-09-03 12:00:00' ORDER BY birthday DESC;"
        self.assertEqual(got, sql_query)

    def test_generate_insert_string(self):

        attributes = {
            "id": "123456", 
            "farm": "test farm", 
            "birthday": date(1999, 5, 12)
        }
        got = self.model._Model__generate_insert_string(attributes, "Pigs")
        self.assertEqual(got, "INSERT INTO Pigs (id, farm, birthday) VALUES ('123456', 'test farm', '1999-05-12');")

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
        pig.set_litter(10)
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
        self.assertEqual(10, attributes["litter"])

    def test_insert_pig(self):

        pig = Pig()
        pig.set_id("123456")
        pig.set_birthday("2022-12-17")
        with self.assertRaises(ValueError):
            self.model.insert_pig(pig)

        pig.set_farm("test_farm")
        pig.set_reg_id("111111")
        pig.set_litter(12)
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
        pig.set_litter(10)
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
        pig.set_litter(10)
        self.model.insert_pig(pig)
        pig.set_gender("F")
        pig.set_litter(9)
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
            "n_of_male": 1, 
            "n_of_female": 1, 
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
        self.assertEqual(1, farrowing.get_n_of_male())
        self.assertEqual(1, farrowing.get_n_of_female())

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
            n_of_male=1, 
            n_of_female=1, 
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
            "n_of_male": 1, 
            "n_of_female": 1, 
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
            n_of_male=1, 
            n_of_female=1, 
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
            n_of_male=1, 
            n_of_female=1, 
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
            n_of_male=1, 
            n_of_female=2, 
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
            n_of_male=1, 
            n_of_female=1, 
        )
        self.model.insert_farrowing(farrowing)
        farrowing = Farrowing(
            estrus=estrus, 
            farrowing_date="2000-09-03", 
            crushed=1, 
            black=1, 
            weak=1, 
            malformation=2, 
            dead=1, 
            n_of_male=1, 
            n_of_female=1, 
        )
        self.model.update_farrowing(farrowing)
        found = self.model.find_farrowings(equal={"farm": "test farm"})
        self.assertEqual(2, found[0].get_malformation())
        self.assertRaises(TypeError, self.model.update_farrowing, "123456")

    def test_dict_to_weaning(self):

        weaning_dict = {
            "id": "123456", 
            "birthday": "1999-05-12", 
            "farm": "test farm", 
            "estrus_datetime": "2000-05-12 12:00:00", 
            "farrowing_date": "2000-09-03", 
            "weaning_date": "2000-09-24", 
            "total_nursed_piglets": 10, 
            "total_weaning_piglets": 9, 
        }
        got = self.model.dict_to_weaning(weaning_dict)
        sow = Pig(
            id="123456", 
            birthday="1999-05-12", 
            farm="test farm"
        )
        estrus = Estrus(sow, "2000-05-12 12:00:00")
        farrowing = Farrowing(estrus, "2000-09-03")
        weaning = Weaning(
            farrowing=farrowing, 
            weaning_date="2000-09-24", 
            total_nursed_piglets=10, 
            total_weaning_piglets=9, 
        )
        self.assertEqual(weaning, got)
        self.assertRaises(TypeError, self.model.dict_to_weaning, "No")
        self.assertIsNone(self.model.dict_to_weaning({"id": "12345"}))

    def test_get_weaning_attributes(self):

        weaning_dict = {
            "id": "123456", 
            "birthday": date(1999, 5, 12), 
            "farm": "test farm", 
            "estrus_datetime": datetime(2000, 5, 12, 12), 
            "weaning_date": date(2000, 9, 24), 
            "total_nursed_piglets": 10, 
            "total_weaning_piglets": 9, 
        }
        sow = Pig(
            id="123456", 
            birthday="1999-05-12", 
            farm="test farm"
        )
        estrus = Estrus(sow, "2000-05-12 12:00:00")
        farrowing = Farrowing(estrus, "2000-09-03")
        weaning = Weaning(
            farrowing=farrowing, 
            weaning_date="2000-09-24", 
            total_nursed_piglets=10, 
            total_weaning_piglets=9, 
        )
        got = self.model._Model__get_weaning_attributes(weaning)
        self.assertEqual(weaning_dict, got)
        weaning = Weaning(
            weaning_date="2000-09-24", 
            total_nursed_piglets=10, 
            total_weaning_piglets=9, 
        )
        weaning_dict = {
            "id": None, 
            "birthday": None, 
            "farm": None, 
            "estrus_datetime": None, 
            "weaning_date": date(2000, 9, 24), 
            "total_nursed_piglets": 10, 
            "total_weaning_piglets": 9, 
        }
        got = self.model._Model__get_weaning_attributes(weaning)
        self.assertEqual(weaning_dict, got)
        self.assertRaises(TypeError, self.model._Model__get_weaning_attributes, None)

    def test_insert_weaning(self):

        sow = Pig(id="123456", birthday="1999-05-12", farm="test farm")
        self.model.insert_pig(sow)
        estrus = Estrus(sow=sow, estrus_datetime="2000-05-12 12:00:00")
        self.model.insert_estrus(estrus)
        farrowing = Farrowing(estrus=estrus, farrowing_date="2000-09-03")
        self.model.insert_farrowing(farrowing)
        weaning = Weaning(
            farrowing=farrowing, 
            weaning_date="2000-09-24", 
            total_nursed_piglets=10, 
            total_weaning_piglets=9, 
        )
        self.model.insert_weaning(weaning)

    def test_find_weaning(self):

        sow = Pig(id="123456", birthday="1999-05-12", farm="test farm")
        self.model.insert_pig(sow)
        estrus = Estrus(sow=sow, estrus_datetime="2000-05-12 12:00:00")
        self.model.insert_estrus(estrus)
        farrowing = Farrowing(estrus=estrus, farrowing_date="2000-09-03")
        self.model.insert_farrowing(farrowing)
        weaning = Weaning(
            farrowing=farrowing, 
            weaning_date="2000-09-24", 
            total_nursed_piglets=10, 
            total_weaning_piglets=9, 
        )
        self.model.insert_weaning(weaning)

        estrus = Estrus(sow=sow, estrus_datetime="2001-05-12 12:00:00")
        self.model.insert_estrus(estrus)
        farrowing = Farrowing(estrus=estrus, farrowing_date="2001-09-03")
        self.model.insert_farrowing(farrowing)
        weaning = Weaning(
            farrowing=farrowing, 
            weaning_date="2001-09-24", 
            total_nursed_piglets=10, 
            total_weaning_piglets=9, 
        )
        self.model.insert_weaning(weaning)

        found = self.model.find_weanings(equal={"id": "123456"})
        self.assertEqual(2, len(found))
        found = self.model.find_weanings(equal={"weaning_date": "2001-09-24"})
        self.assertEqual(found[0], weaning)

    def test_update_weaning(self):

        sow = Pig(id="123456", birthday="1999-05-12", farm="test farm")
        self.model.insert_pig(sow)
        estrus = Estrus(sow=sow, estrus_datetime="2000-05-12 12:00:00")
        self.model.insert_estrus(estrus)
        farrowing = Farrowing(estrus=estrus, farrowing_date="2000-09-03")
        self.model.insert_farrowing(farrowing)
        weaning = Weaning(
            farrowing=farrowing, 
            weaning_date="2000-09-24", 
            total_nursed_piglets=10, 
            total_weaning_piglets=9, 
        )
        self.model.insert_weaning(weaning)

        estrus = Estrus(sow=sow, estrus_datetime="2001-05-12 12:00:00")
        self.model.insert_estrus(estrus)
        farrowing = Farrowing(estrus=estrus, farrowing_date="2001-09-03")
        self.model.insert_farrowing(farrowing)
        weaning = Weaning(
            farrowing=farrowing, 
            weaning_date="2001-09-24", 
            total_nursed_piglets=10, 
            total_weaning_piglets=9, 
        )
        self.model.insert_weaning(weaning)

        weaning = Weaning(
            farrowing=farrowing, 
            weaning_date="2001-09-24", 
            total_nursed_piglets=20, 
            total_weaning_piglets=9, 
        )
        self.model.update_weaning(weaning)
        found = self.model.find_weanings(equal={"weaning_date": "2000-09-24"})
        self.assertEqual(10, found[0].get_total_nursed_piglets())
        found = self.model.find_weanings(equal={"weaning_date": "2001-09-24"})
        self.assertEqual(20, found[0].get_total_nursed_piglets())

    def test_dict_to_individual(self):

        individual_dict = {
            "birth_sow_id": "123456", 
            "birth_sow_farm": "test farm", 
            "birth_sow_birthday": "1999-05-12", 
            "birth_estrus_datetime": "2000-05-12 10:00:00", 
            "nurse_sow_id": "123456", 
            "nurse_sow_farm": "test farm", 
            "nurse_sow_birthday": "1999-05-12", 
            "nurse_estrus_datetime": "2000-05-12 10:00:00", 
            "in_litter_id": "12", 
            "born_weight": 1.2, 
            "weaning_weight": 12, 
            "gender": "F"
        }
        got = self.model.dict_to_individual(individual_dict)
        sow = Pig(id="123456", farm="test farm", birthday="1999-05-12")
        estrus = Estrus(sow=sow, estrus_datetime="2000-05-12 10:00:00")
        farrowing = Farrowing(estrus=estrus)
        weaning = Weaning(farrowing=farrowing)
        individual = Individual(
            birth_litter=farrowing, 
            nurse_litter=weaning, 
            in_litter_id="12", 
            born_weight=1.2, 
            weaning_weight=12, 
            gender="F"
        )
        self.assertEqual(got, individual)

    def test_get_individual_attributes(self):

        sow = Pig(id="123456", farm="test farm", birthday="1999-05-12")
        estrus = Estrus(sow=sow, estrus_datetime="2000-05-12 10:00:00")
        farrowing = Farrowing(estrus=estrus)
        weaning = Weaning(farrowing=farrowing)
        individual = Individual(
            birth_litter=farrowing, 
            nurse_litter=weaning, 
            in_litter_id="12", 
            born_weight=1.2, 
            weaning_weight=12, 
            gender="2"
        )
        got = self.model._Model__get_individual_attributes(individual)
        individual_dict = {
            "birth_sow_id": "123456", 
            "birth_sow_farm": "test farm", 
            "birth_sow_birthday": date(1999, 5, 12), 
            "birth_estrus_datetime": datetime(2000, 5, 12, 10), 
            "nurse_sow_id": "123456", 
            "nurse_sow_farm": "test farm", 
            "nurse_sow_birthday": date(1999, 5, 12), 
            "nurse_estrus_datetime": datetime(2000, 5, 12, 10), 
            "in_litter_id": "12", 
            "born_weight": 1.2, 
            "weaning_weight": 12, 
            "gender": "F"
        }
        self.assertEqual(got, individual_dict)

    def test_insert_individual(self):

        sow = Pig(id="123456", farm="test farm", birthday="1999-05-12")
        estrus = Estrus(sow=sow, estrus_datetime="2000-05-12 10:00:00")
        farrowing = Farrowing(estrus=estrus, farrowing_date="2000-09-03")
        weaning = Weaning(farrowing=farrowing, weaning_date="2000-09-24")
        individual = Individual(
            birth_litter=farrowing, 
            nurse_litter=weaning, 
            in_litter_id="12", 
            born_weight=1.2, 
            weaning_weight=12, 
            gender="F"
        )
        self.model.insert_pig(sow)
        self.model.insert_estrus(estrus)
        self.model.insert_farrowing(farrowing)
        self.model.insert_weaning(weaning)
        self.model.insert_individual(individual)
        self.assertRaises(TypeError, self.model.insert_individual, "HI")
        self.assertRaises(ValueError, self.model.insert_individual, Individual())

    def test_find_individuals(self):

        sow = Pig(id="123456", farm="test farm", birthday="1999-05-12")
        estrus = Estrus(sow=sow, estrus_datetime="2000-05-12 10:00:00")
        farrowing = Farrowing(estrus=estrus, farrowing_date="2000-09-03")
        weaning = Weaning(farrowing=farrowing, weaning_date="2000-09-24")
        individual = Individual(
            birth_litter=farrowing, 
            nurse_litter=weaning, 
            in_litter_id="12", 
            born_weight=1.2, 
            weaning_weight=12, 
            gender="F"
        )
        self.model.insert_pig(sow)
        self.model.insert_estrus(estrus)
        self.model.insert_farrowing(farrowing)
        self.model.insert_weaning(weaning)
        self.model.insert_individual(individual)
        got = self.model.find_individuals(
            equal={"birth_sow_id": "123456"}, 
            larger={"birth_estrus_datetime": datetime(2000, 5, 11, 11)},
            smaller={"nurse_estrus_datetime": datetime(2000, 5, 13)},
            larger_equal={"in_litter_id": "10"},
            smaller_equal={"born_weight": 1.8}
        )
        self.assertEqual(got[0], individual)

    def test_update_individual(self):

        sow = Pig(id="123456", farm="test farm", birthday="1999-05-12")
        estrus = Estrus(sow=sow, estrus_datetime="2000-05-12 10:00:00")
        farrowing = Farrowing(estrus=estrus, farrowing_date="2000-09-03")
        weaning = Weaning(farrowing=farrowing, weaning_date="2000-09-24")
        individual = Individual(
            birth_litter=farrowing, 
            nurse_litter=weaning, 
            in_litter_id="12", 
            born_weight=1.2, 
            weaning_weight=12, 
            gender="F"
        )
        self.model.insert_pig(sow)
        self.model.insert_estrus(estrus)
        self.model.insert_farrowing(farrowing)
        self.model.insert_weaning(weaning)
        self.model.insert_individual(individual)

        individual.set_born_weight(0.9)
        self.model.update_individual(individual)
        got = self.model.find_individuals(equal={"birth_sow_farm": "test farm"})
        self.assertEqual(0.9, got[0].get_born_weight())


if __name__ == '__main__':
    unittest.main()