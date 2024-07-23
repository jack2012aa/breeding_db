import unittest
from unittest.mock import MagicMock, patch
from datetime import date, datetime

from breeding_db.data_structures import *


class PigTestCase(unittest.TestCase):

    def setUp(self):
        self.pig = Pig()

    def tearDown(self):
        self.pig = None

    def test_set_id(self):

        self.pig.set_id("123456")
        self.assertEqual(self.pig.get_id(),"123456")

        # Length Error
        self.assertRaises(ValueError, self.pig.set_id, id = '')
        self.assertRaises(ValueError, self.pig.set_id, 'asduflsdfjskabdfijaslfefiudsbufbliadbf')

        # TypeError
        self.assertRaises(TypeError, self.pig.set_id, None)

    def test_set_breed(self):

        self.pig.set_breed("L")
        self.assertEqual("L", self.pig.get_breed())
        self.pig.set_breed("藍瑞斯")
        self.assertEqual("L", self.pig.get_breed())
        breed = "Landrace"
        self.assertRaises(ValueError, self.pig.set_breed, breed)
        self.assertRaises(TypeError, self.pig.set_breed, None)

    def test_set_birthday(self):

        self.pig.set_birthday("2021-02-03")
        self.assertEqual(date(2021, 2, 3), self.pig.get_birthday())
        birthday = date(2021, 2, 3)
        self.pig.set_birthday(birthday)
        self.assertEqual(birthday, self.pig.get_birthday())

        # Error
        self.assertRaises(ValueError, self.pig.set_birthday, "2021.12.03")
        self.assertRaises(TypeError, self.pig.set_birthday, 123456)
        self.assertRaises(TypeError, self.pig.set_birthday, None)

    def test_set_dam(self):

        dam = Pig()
        dam.set_id("dsfisdif")
        dam.set_birthday("2021-02-03")
        dam.set_farm("test_farm")
        self.pig.set_dam(dam)
        self.assertEqual(dam, self.pig.get_dam())
        dam = Pig()
        dam.set_id("dsfisdif")
        dam.set_birthday("2021-02-03")
        self.assertRaises(ValueError, self.pig.set_dam, dam)
        self.assertRaises(TypeError, self.pig.set_dam, None)

    def test_set_sire(self):

        sire = Pig()
        sire.set_id("dsfisdif")
        sire.set_birthday("2021-02-03")
        sire.set_farm("test_farm")
        self.pig.set_sire(sire)
        self.assertEqual(sire, self.pig.get_sire())
        sire = Pig()
        sire.set_id("dsfisdif")
        sire.set_birthday("2021-02-03")
        self.assertRaises(ValueError, self.pig.set_sire, sire)
        sire = None
        self.assertRaises(TypeError, self.pig.set_sire, sire)

    def test_set_reg_id(self):

        self.pig.set_reg_id("123456")
        self.assertEqual("123456", self.pig.get_reg_id())

        self.assertRaises(ValueError, self.pig.set_reg_id, "324dsf")
        self.assertRaises(TypeError, self.pig.set_reg_id, 12345)
        self.assertRaises(ValueError, self.pig.set_reg_id, "1234567")

    def test_gender(self):

        self.pig.set_gender("公")
        self.assertEqual("M",self.pig.get_gender())
        self.pig.set_gender("M")
        self.assertEqual("M",self.pig.get_gender())
        self.pig.set_gender("1")
        self.assertEqual("M",self.pig.get_gender())
        self.assertRaises(KeyError, self.pig.set_gender, None)

    def test_set_chinese_name(self):

        self.pig.set_chinese_name("你好")
        self.assertEqual("你好", self.pig.get_chinese_name())
        self.assertRaises(TypeError, self.pig.set_chinese_name, None)
        self.assertRaises(ValueError, self.pig.set_chinese_name, "你好恭喜發財")

    def test_set_farm(self):

        self.pig.set_farm("Dong-Ying")
        self.assertEqual("Dong-Ying", self.pig.get_farm())
        self.assertRaises(TypeError, self.pig.set_farm, None)

    def test_set_litter(self):

        self.assertIsNone(self.pig.get_litter())
        self.pig.set_litter(2)
        self.assertEqual(self.pig.get_litter(), 2)
        self.assertRaises(TypeError, self.pig.set_litter, "2")
        self.assertRaises(ValueError, self.pig.set_litter, 22)

    def test_equality(self):

        pig1 = Pig()
        pig1.set_id("123456")
        pig1.set_birthday("2023-02-02")
        pig2 = Pig()
        pig2.set_id("123456")
        pig2.set_birthday("2023-02-02")
        self.assertEqual(pig1, pig2)
        pig2.set_farm("Dong-Ying")
        self.assertNotEqual(pig1, pig2)
        self.assertNotEqual(pig1, None)


class EstrusTestCase(unittest.TestCase):

    def setUp(self):
        self.estrus = Estrus()

    def tearDown(self):
        self.estrus = None

    def test_set_sow(self):
        
        pig = Pig()
        pig.set_birthday("1999-05-12")
        pig.set_id("123456")
        with self.assertRaises(ValueError):
           self.estrus.set_sow(pig)
        with self.assertRaises(TypeError):
            self.estrus.set_sow(1)
        pig.set_farm("test farm")

        self.estrus.set_estrus_datetime("1998-05-12 12:00:00")
        with self.assertRaises(ValueError):
            self.estrus.set_sow(pig)
        
        self.estrus.set_estrus_datetime("2000-05-12 12:00:00")
        self.estrus.set_sow(pig)
        self.assertEqual(pig, self.estrus.get_sow())


    def test_set_estrus_datetime(self):

        # Correct
        self.estrus.set_estrus_datetime("2023-12-05 9:27:30")
        self.assertEqual(
            self.estrus.get_estrus_datetime(),
            datetime.strptime("2023-12-05 9:27:30", "%Y-%m-%d %H:%M:%S")
        )
        self.estrus.set_estrus_datetime(datetime.strptime("2023-12-05 9:27:30", "%Y-%m-%d %H:%M:%S"))
        self.assertEqual(
            self.estrus.get_estrus_datetime(),
            datetime.strptime("2023-12-05 9:27:30", "%Y-%m-%d %H:%M:%S")
        )

        # Wrong date.
        with self.assertRaises(ValueError):
            self.estrus = Estrus()
            pig = Pig()
            pig.set_birthday("1999-05-12")
            pig.set_id("123456")
            pig.set_farm("test farm")
            self.estrus.set_sow(pig)
            self.estrus.set_estrus_datetime("1998-12-05 9:27:30")

        # Wrong format
        self.assertRaises(ValueError, self.estrus.set_estrus_datetime, "2023/12/15")

        # TypeError
        self.assertRaises(TypeError, self.estrus.set_estrus_datetime, None)

    def test_pregnant(self):

        # Correct
        self.estrus.set_pregnant(PregnantStatus.UNKNOWN)
        self.assertEqual(self.estrus.get_pregnant(), PregnantStatus.UNKNOWN)

        # TypeError
        self.assertRaises(TypeError, self.estrus.set_pregnant, Pig())

    def test_parity(self):

        # Correct
        self.estrus.set_parity(1)
        self.assertEqual(1, self.estrus.get_parity())

        # Out of range
        self.assertRaises(ValueError, self.estrus.set_parity, -1)
        self.assertRaises(ValueError, self.estrus.set_parity, 13)

        # TypeError
        self.assertRaises(TypeError, self.estrus.set_parity, Pig())

    def test_equal(self):

        pig = Pig()
        pig.set_birthday("2022-02-01")
        pig.set_id("123456")
        pig.set_farm("test")

        other = Estrus()
        other.set_sow(pig)
        self.estrus.set_sow(pig)
        other.set_estrus_datetime("2025-03-12 16:00:00")
        self.estrus.set_estrus_datetime("2025-03-12 16:00:00")
        self.assertEqual(self.estrus, other)
        other.set_parity(2)
        self.estrus.set_parity(2)
        other.set_pregnant(PregnantStatus.YES)
        self.estrus.set_pregnant(PregnantStatus.YES)
        self.assertEqual(self.estrus, other)

    def test_inequality(self):

        pig = Pig()
        other = Estrus()
        pig.set_id("123456")
        pig.set_birthday("2021-02-02")
        pig.set_farm("test")
        self.estrus.set_sow(pig)
        self.assertFalse(other == self.estrus)
        other.set_sow(pig)
        self.estrus.set_estrus_datetime("2022-02-02 16:00:00")
        other.set_estrus_datetime("2022-02-01 16:00:00")
        self.assertFalse(other == self.estrus)
        other.set_estrus_datetime("2022-02-02 16:00:00")
        self.estrus.set_parity(3)
        other.set_parity(2)
        self.assertFalse(other == self.estrus)
        self.estrus.set_parity(2)
        self.estrus.set_pregnant(PregnantStatus.ABORTION)
        other.set_pregnant(PregnantStatus.YES)
        self.assertFalse(other == self.estrus)

    def test_is_unique(self):

        self.assertFalse(self.estrus.is_unique())
        pig = Pig()
        pig.set_id("123456")
        pig.set_birthday("2021-02-02")
        pig.set_farm("test")
        self.estrus.set_sow(pig)
        self.assertFalse(self.estrus.is_unique())
        self.estrus.set_estrus_datetime("2023-02-02 01:01:01")
        self.assertTrue(self.estrus.is_unique())


class MatingTestCase(unittest.TestCase):

    def setUp(self):

        self.mating = Mating()
        self.sow = Pig()
        self.sow.set_id("123456")
        self.sow.set_birthday("2020-01-31")
        self.sow.set_farm("test")
        self.estrus = Estrus()
        self.estrus.set_sow(self.sow)
        self.estrus.set_estrus_datetime("2020-07-30 1:1:1")

    def tearDown(self):
        self.pig = None
        self.mating = None

    def test_correctly_set_estrus(self):

        self.mating.set_estrus(self.estrus)
        self.assertEqual(self.mating.get_estrus(), self.estrus)

        with self.assertRaises(ValueError):
            self.mating = Mating()
            self.mating.set_mating_datetime("2020-08-20 1:1:1")
            self.mating.set_estrus(self.estrus)

        boar = Pig(farm="test farm", id="123455", birthday="2021-05-12")
        self.mating = Mating()
        self.mating.set_boar(boar)
        with self.assertRaises(ValueError):
            self.mating.set_estrus(self.estrus)

    def test_set_not_unique_estrus(self):

        estrus = Estrus()
        estrus.set_sow(self.sow)
        self.assertRaises(ValueError, self.mating.set_estrus, estrus)

    def test_set_not_estrus(self):

        self.assertRaises(TypeError, self.mating.set_estrus, 123)

    def test_set_mating_datetime(self):

        # Correct
        self.mating.set_mating_datetime("2023-12-05 9:27:30")
        self.assertEqual(
            self.mating.get_mating_datetime(),
            datetime.strptime("2023-12-05 9:27:30", "%Y-%m-%d %H:%M:%S")
        )
        self.mating.set_mating_datetime(datetime.strptime("2023-12-05 9:27:30", "%Y-%m-%d %H:%M:%S"))
        self.assertEqual(
            self.mating.get_mating_datetime(),
            datetime.strptime("2023-12-05 9:27:30", "%Y-%m-%d %H:%M:%S")
        )

        # Wrong format
        self.assertRaises(ValueError, self.mating.set_mating_datetime, "2023/12/15")

        # TypeError
        self.assertRaises(TypeError, self.mating.set_mating_datetime, None)

        # Gap too long
        with self.assertRaises(ValueError):
            self.mating.set_estrus(self.estrus)
            self.mating.set_mating_datetime("2020-08-09 1:1:1")

        boar = Pig(id="123455", birthday="2024-05-12", farm="test farm")
        with self.assertRaises(ValueError):
            self.mating = Mating()
            self.mating.set_boar(boar)
            self.mating.set_mating_datetime("2022-05-12 12:00:00")

    def test_correctly_set_boar(self):

        self.mating.set_boar(self.sow)
        self.assertEqual(self.sow, self.mating.get_boar())

        boar = Pig()
        boar.set_id("12344")
        self.assertRaises(ValueError, self.mating.set_boar, boar)
        self.assertRaises(TypeError, self.mating.set_boar, "12344")

        with self.assertRaises(ValueError):
            boar = Pig(id="122222", farm="test farm", birthday="2024-05-12")
            self.mating.set_mating_datetime("2022-05-12 12:00:00")
            self.mating.set_boar(boar)
        
        with self.assertRaises(ValueError):
            boar = Pig(id="122222", farm="test farm", birthday="2024-05-12")
            self.mating.set_estrus(self.estrus)
            self.mating.set_boar(boar)
    def test_equality(self):

        mating = Mating()
        self.mating.set_estrus(self.estrus)
        mating.set_estrus(self.estrus)
        self.assertEqual(self.mating, mating)
        self.mating.set_boar(self.sow)
        mating.set_boar(self.sow)
        self.assertEqual(self.mating, mating)
        self.mating.set_mating_datetime("2020-08-01 1:1:1")
        mating.set_mating_datetime("2020-08-01 1:1:1")
        self.assertEqual(self.mating, mating)

    def test_inequality(self):

        mating = Mating()
        estrus = Estrus()
        estrus.set_sow(self.sow)
        estrus.set_estrus_datetime("2023-01-04 16:00:00")
        self.mating.set_estrus(self.estrus)
        mating.set_estrus(estrus)
        self.assertNotEqual(self.mating, mating)
        mating.set_estrus(self.estrus)
        self.mating.set_mating_datetime("2020-08-01 1:1:1")
        mating.set_mating_datetime("2020-08-01 12:1:1")
        self.assertNotEqual(self.mating, mating)
        mating.set_mating_datetime("2020-08-01 1:1:1")
        boar = Pig()
        boar.set_id("12345")
        boar.set_birthday("2019-01-01")
        boar.set_farm("test")
        self.mating.set_boar(boar)
        self.assertNotEqual(self.mating, mating)


class FarrowingTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.farrowing = Farrowing()

    def tearDown(self) -> None:
        self.farrowing = None

    def test_set(self):

        self.assertFalse(self.farrowing.is_unique())

        # Set estrus.
        sow = Pig(id="123456", birthday="1999-05-12", farm="test farm")
        estrus = Estrus(sow=sow)
        with self.assertRaises(ValueError):
            self.farrowing.set_estrus(estrus)
        estrus.set_estrus_datetime("2000-05-12 12:00:00")
        self.farrowing.set_estrus(estrus)
        self.assertEqual(self.farrowing.get_estrus(), estrus)
        self.assertRaises(TypeError, self.farrowing.set_estrus, "No")

        # Set farrowing date.
        self.farrowing.set_farrowing_date("2000-09-19")
        self.assertEqual(self.farrowing.get_farrowing_date(), date(2000, 9, 19))
        self.assertRaises(TypeError, self.farrowing.set_farrowing_date, None)
        self.assertRaises(ValueError, self.farrowing.set_farrowing_date, "2000/9/12")
        self.assertTrue(self.farrowing.is_unique())
        
        # Incorrect farrowing date and estrus date.
        self.assertRaises(ValueError, self.farrowing.set_farrowing_date, "2000-08-10")
        self.assertRaises(ValueError, self.farrowing.set_farrowing_date, "2000-9-20")
        self.farrowing = Farrowing(farrowing_date="2000-08-10")
        estrus.set_estrus_datetime("2000-05-03 12:00:00")
        self.assertRaises(ValueError, self.farrowing.set_estrus, estrus)
        estrus.set_estrus_datetime("2000-04-01 12:00:00")
        self.assertRaises(ValueError, self.farrowing.set_estrus, estrus)

        # Set crushed.
        self.farrowing.set_crushed(5)
        self.assertEqual(5, self.farrowing.get_crushed())
        self.assertRaises(TypeError, self.farrowing.set_crushed, "3")
        self.assertRaises(ValueError, self.farrowing.set_crushed, -1)
        self.assertRaises(ValueError, self.farrowing.set_crushed, 100)
        
        # Set black.
        self.farrowing.set_black(5)
        self.assertEqual(5, self.farrowing.get_black())
        self.assertRaises(TypeError, self.farrowing.set_black, "3")
        self.assertRaises(ValueError, self.farrowing.set_black, -1)
        self.assertRaises(ValueError, self.farrowing.set_black, 100)

        # Set weak.
        self.farrowing.set_weak(5)
        self.assertEqual(5, self.farrowing.get_weak())
        self.assertRaises(TypeError, self.farrowing.set_weak, "3")
        self.assertRaises(ValueError, self.farrowing.set_weak, -1)
        self.assertRaises(ValueError, self.farrowing.set_weak, 100)

        # Set malformation.
        self.farrowing.set_malformation(5)
        self.assertEqual(5, self.farrowing.get_malformation())
        self.assertRaises(TypeError, self.farrowing.set_malformation, "3")
        self.assertRaises(ValueError, self.farrowing.set_malformation, -1)
        self.assertRaises(ValueError, self.farrowing.set_malformation, 100)

        # Set dead.
        self.farrowing.set_dead(5)
        self.assertEqual(5, self.farrowing.get_dead())
        self.assertRaises(TypeError, self.farrowing.set_dead, "3")
        self.assertRaises(ValueError, self.farrowing.set_dead, -1)
        self.assertRaises(ValueError, self.farrowing.set_dead, 100)

        # Set n_of_male.
        self.farrowing.set_n_of_male(1)
        self.assertEqual(1, self.farrowing.get_n_of_male())
        self.assertRaises(TypeError, self.farrowing.set_n_of_male, "3")
        self.assertRaises(ValueError, self.farrowing.set_n_of_male, -1)
        self.assertRaises(ValueError, self.farrowing.set_n_of_male, 6)

        # Set n_of_female.
        self.farrowing.set_n_of_female(1)
        self.assertEqual(1, self.farrowing.get_n_of_female())
        self.assertRaises(TypeError, self.farrowing.set_n_of_female, "3")
        self.assertRaises(ValueError, self.farrowing.set_n_of_female, -1)
        self.assertRaises(ValueError, self.farrowing.set_n_of_male, 5)

        # total number dead.
        self.assertEqual(25, self.farrowing.get_born_dead())
        self.assertEqual(2, self.farrowing.get_born_alive())
        self.assertEqual(27, self.farrowing.get_total_born())

        self.farrowing = Farrowing(
            estrus=estrus, 
            farrowing_date="2000-07-24", 
            crushed=1, 
            black=1, 
            weak=1, 
            malformation=1, 
            dead=1, 
            n_of_male=1, 
            n_of_female=1, 
        )
        self.assertEqual(self.farrowing.get_estrus(), estrus)
        self.assertEqual(self.farrowing.get_farrowing_date(), date(2000, 7, 24))
        self.assertEqual(self.farrowing.get_crushed(), 1)
        self.assertEqual(self.farrowing.get_black(), 1)
        self.assertEqual(self.farrowing.get_weak(), 1)
        self.assertEqual(self.farrowing.get_malformation(), 1)
        self.assertEqual(self.farrowing.get_n_of_male(), 1)
        self.assertEqual(self.farrowing.get_n_of_female(), 1)


class WeaningTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.weaning = Weaning()

    def tearDown(self) -> None:
        self.weaning = None

    def test_set(self):

        sow = Pig(id="123456", farm="test farm", birthday="1999-05-12")
        estrus = Estrus(
            sow=sow, 
            estrus_datetime="2000-05-12 12:00:00"
        )
        farrowing = Farrowing(
            estrus=estrus, 
            farrowing_date="2000-09-03"
        )
        self.weaning.set_weaning_date("2000-09-24")
        self.assertEqual(date(2000, 9, 24), self.weaning.get_weaning_date())
        self.weaning.set_farrowing(farrowing)
        self.assertEqual(farrowing, self.weaning.get_farrowing())
        self.weaning.set_total_nursed_piglets(10)
        self.assertEqual(10, self.weaning.get_total_nursed_piglets())
        self.weaning.set_total_weaning_piglets(9)
        self.assertEqual(9, self.weaning.get_total_weaning_piglets())
        self.weaning = Weaning()
        self.weaning.set_farrowing(farrowing)
        self.assertTrue(self.weaning.is_unique())
        self.assertRaises(ValueError, self.weaning.set_weaning_date, "2024-11-01")
        self.assertRaises(ValueError, self.weaning.set_weaning_date, "2024-09-04")
        self.weaning = Weaning()
        self.weaning.set_weaning_date("2000-09-04")
        farrowing = Farrowing(estrus, "2000-09-03")
        self.assertRaises(ValueError, self.weaning.set_farrowing, farrowing)

        self.weaning = Weaning()
        self.weaning.set_weaning_date("2000-09-16")
        self.assertRaises(ValueError, self.weaning.set_farrowing, farrowing)
        self.weaning.set_weaning_date("2000-09-14")
        self.assertRaises(ValueError, self.weaning.set_farrowing, farrowing)
        self.weaning.set_total_nursed_piglets(10)
        self.assertRaises(ValueError, self.weaning.set_total_weaning_piglets, 11)
        self.weaning.set_total_weaning_piglets(10)
        self.assertRaises(ValueError, self.weaning.set_total_nursed_piglets, 9)
        self.weaning = Weaning()
        self.assertRaises(TypeError, self.weaning.set_farrowing, "HI")
        self.assertRaises(ValueError, self.weaning.set_farrowing, Farrowing())
        self.assertRaises(TypeError, self.weaning.set_weaning_date, farrowing)
        self.assertRaises(ValueError, self.weaning.set_weaning_date, "HI")
        self.assertRaises(TypeError, self.weaning.set_total_nursed_piglets, "HI")
        self.assertRaises(ValueError, self.weaning.set_total_nursed_piglets, -1)
        self.assertRaises(ValueError, self.weaning.set_total_nursed_piglets, 31)
        self.assertRaises(TypeError, self.weaning.set_total_weaning_piglets, "HI")
        self.assertRaises(ValueError, self.weaning.set_total_weaning_piglets, -1)
        self.assertRaises(ValueError, self.weaning.set_total_weaning_piglets, 31)


class IndividualTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.individual = Individual()

    def tearDown(self) -> None:
        self.individual = None

    def test_set_up(self) -> None:
        
        sow = Pig(id="123456", farm="test farm", birthday="1999-05-12")
        estrus = Estrus(sow=sow, estrus_datetime="2000-05-12 10:00:00")
        farrowing = Farrowing(estrus=estrus, farrowing_date="2000-09-03")
        weaning = Weaning(farrowing=farrowing, weaning_date="2000-09-24")
        
        self.individual.set_birth_litter(farrowing)
        self.assertEqual(self.individual.get_birth_litter(), farrowing)
        self.individual.set_nurse_litter(weaning)
        self.assertEqual(self.individual.get_nurse_litter(), weaning)
        self.individual.set_in_litter_id("10")
        self.assertEqual(self.individual.get_in_litter_id(), "10")
        self.individual.set_born_weight(1.2)
        self.assertEqual(self.individual.get_born_weight(), 1.2)
        self.individual.set_weaning_weight(12)
        self.assertEqual(self.individual.get_weaning_weight(), 12.0)
        self.individual.set_gender("1")
        self.assertEqual(self.individual.get_gender(), "M")

        estrus2 = Estrus(sow=sow, estrus_datetime="2000-05-20 10:00:00")
        farrowing2 = Farrowing(estrus=estrus2, farrowing_date="2000-09-25")
        self.assertRaises(ValueError, self.individual.set_birth_litter, farrowing2)
        self.assertRaises(ValueError, self.individual.set_birth_litter, Farrowing())
        self.assertRaises(TypeError, self.individual.set_birth_litter, "IH")

        self.assertRaises(ValueError, self.individual.set_in_litter_id, "99")
        self.assertRaises(ValueError, self.individual.set_in_litter_id, "-1")
        self.assertRaises(ValueError, self.individual.set_in_litter_id, "string")
        
        self.assertRaises(ValueError, self.individual.set_born_weight, -1.0)
        self.assertRaises(ValueError, self.individual.set_weaning_weight, -1.0)

        self.assertRaises(TypeError, self.individual.set_gender, 1)
        self.assertRaises(ValueError, self.individual.set_gender, "Boar")

    def test_equal(self):

        sow = Pig(id="123456", farm="test farm", birthday="1999-05-12")
        estrus = Estrus(sow=sow, estrus_datetime="2000-05-12 10:00:00")
        farrowing = Farrowing(estrus=estrus, farrowing_date="2000-09-03")
        weaning = Weaning(farrowing=farrowing, weaning_date="2000-09-24")
        self.individual = Individual(
            birth_litter=farrowing, 
            nurse_litter=weaning, 
            in_litter_id="12", 
            born_weight=1.2, 
            weaning_weight=12.0
        )

        self.assertNotEqual(self.individual, None)

        individual = Individual(
            birth_litter=farrowing, 
            nurse_litter=weaning, 
            in_litter_id="12", 
            born_weight=1.2, 
            weaning_weight=12.0
        )
        self.assertEqual(self.individual, individual)

        individual = Individual(
            birth_litter=Farrowing(estrus=Estrus(sow, "2000-05-12 12:00:01")), 
            nurse_litter=weaning, 
            in_litter_id="12", 
            born_weight=1.2, 
            weaning_weight=12.0
        )
        self.assertNotEqual(self.individual, individual)

        individual = Individual(
            birth_litter=farrowing, 
            nurse_litter=Weaning(farrowing=Farrowing(Estrus(sow, "2000-05-12 12:00:01"))), 
            in_litter_id="12", 
            born_weight=1.2, 
            weaning_weight=12.0
        )
        self.assertNotEqual(self.individual, individual)

        individual = Individual(
            birth_litter=farrowing, 
            nurse_litter=weaning, 
            in_litter_id="13", 
            born_weight=1.2, 
            weaning_weight=12.0
        )
        self.assertNotEqual(self.individual, individual)

        individual = Individual(
            birth_litter=farrowing, 
            nurse_litter=weaning, 
            in_litter_id="12", 
            born_weight=1.22, 
            weaning_weight=12.0
        )
        self.assertNotEqual(self.individual, individual)

        individual = Individual(
            birth_litter=farrowing, 
            nurse_litter=weaning, 
            in_litter_id="12", 
            born_weight=1.2, 
            weaning_weight=12.1
        )
        self.assertNotEqual(self.individual, individual)


if __name__ == '__main__':
    unittest.main()