"""Define data structures used in breeding db."""

__all__ = [
    "Pig", 
    "PregnantStatus", 
    "Estrus", 
    "Mating", 
    "Farrowing", 
    "Weaning", 
    "Individual"
]

import logging
from enum import Enum
from datetime import date, datetime, timedelta

from breeding_db.general import type_check, transform_date, add_with_none


class Pig:

    # Define enums.
    BREED = ("LY", "YL", "F", "L", "Y", "D", "F") # Acceptable breeds.
    BREED_CHINESE_TO_ENGLISH = {"藍瑞斯":"L","約克夏":"Y","杜洛克":"D"}
    GENDER = {"公":"M", "母":"F", "M":"M", "F":"F", "1":"M", "2":"F"}
    MAX_ID_LENGTH = 20

    def __init__(
        self, 
        breed: str = None, 
        id: str = None, 
        birthday: str | date = None, 
        sire: "Pig" = None, 
        dam: "Pig" = None, 
        reg_id: str = None, 
        gender: str = None, 
        chinese_name: str = None, 
        farm: str = None, 
        litter: int = None
    ):
        """A data class represents a pig.
        
        Please set attributes through set() methods.

        :param breed: pig's breed which is defined in Pig.BREED, defaults to None
        :param id: ID or ear tag of the pig, defaults to None
        :param birthday: pig's birthday in date or ISO format string. Such as \
            yyyy-mm-dd.
        :param sire: a unique Pig instance, defaults to None
        :param dam: a unique Pig instance, defaults to None
        :param reg_id: a six digit id string, defaults to None
        :param gender: pig's gender, defaults to None
        :param chinese_name: a Chinese name shorter than 5 characters, defaults \
            to None
        :param farm: farm's name, defaults to None
        :param litter: the born parity of this pig.
        """
        if breed is not None:
            self.set_breed(breed)
        else:
            self.__breed: str = None
        if id is not None:
            self.set_id(id)
        else:
            self.__id: str = None
        if birthday is not None:
            self.set_birthday(birthday)
        else:
            self.__birthday: date = None
        if sire is not None:
            self.set_sire(sire)
        else:
            self.__sire: Pig = None
        if dam is not None:
            self.set_dam(dam)
        else:
            self.__dam: Pig = None
        if reg_id is not None:
            self.set_reg_id(reg_id)
        else:
            self.__reg_id: str = None # ID registered in National Animal Industry Fundation.
        if gender is not None:
            self.set_gender(gender)
        else:
            self.__gender: str = None
        if chinese_name is not None:
            self.set_chinese_name(chinese_name)
        else:
            self.__chinese_name: str = None
        if farm is not None:
            self.set_farm(farm)
        else:
            self.__farm: str = None
        if litter is not None:
            self.set_litter(litter)
        else:
            self.__litter: int = None

    def __str__(self):
        s = (
            "耳號 ID: {id}\n".format(id=self.__id)
            + "生日 birthday: {birth}\n".format(birth=str(self.__birthday))
            + "所屬牧場 farm: {farm}\n".format(farm=self.__farm)
            + "品種 breed: {breed}\n".format(breed=self.__breed)
            + "性別 gender: {gender}\n".format(gender=self.__gender)
            + "中文名 Chinese name: {name}\n".format(name=self.__chinese_name)
            + "母畜耳號 dam id: {dam}\n".format(dam=self.get_dam_id())
            + "父畜耳號 sire id: {sire}\n".format(sire=self.get_sire_id())
            )
        return str(s)

    def __eq__(self, other):

        if other is None:
            return False

        if not isinstance(other, Pig):
            msg = f"Can not compare Pig with {type(other)}"
            logging.error(msg)
            raise TypeError(msg)

        return \
            self.__id == other.get_id()\
            and self.__farm == other.get_farm()\
            and self.__birthday == other.get_birthday()\
            and self.__breed == other.get_breed()\
            and self.__gender == other.get_gender()\
            and self.__chinese_name == other.get_chinese_name()\
            and self.get_dam_id() == other.get_dam_id()\
            and self.get_sire_id() == other.get_sire_id()\
            and self.get_litter() == other.get_litter()

    def __is_valid_id(self, id:str):
        return len(id) > 0 and len(id) < Pig.MAX_ID_LENGTH

    def is_identical(self, other) -> bool:
        """Return whether their primary keys are identical.

        :param other: another Pig instance.
        :raises: TypeError
        :return: True if their id, farm and birthday are same.
        """

        # Type check.
        if other is None:
            return False
        type_check(other, "other", Pig)

        return \
            self.__id == other.get_id()\
            and self.__farm == other.get_farm()\
            and self.__birthday == other.get_birthday()\

    def set_breed(self, breed: str) -> None:
        """ Set breed. Breed should be defined in Pig.BREED.

        :param breed: pig's breed which is defined in Pig.BREED.
        :raises: ValueError
        """

        type_check(breed, "breed", str)

        if breed in Pig.BREED:
            self.__breed = breed
        elif breed in Pig.BREED_CHINESE_TO_ENGLISH:
            self.__breed = Pig.BREED_CHINESE_TO_ENGLISH[breed]
        else:
            msg = f"Breed \"{breed}\" is not defined in Pig.BREED."
            logging.error(msg)
            raise ValueError(msg)

    def set_id(self, id: str) -> None:
        """ Set id. ID has not to be unique but should not repeat too often.

        :param id: ID of the pig.
        :raises: ValueError
        """

        type_check(id, "id", str)

        if not self.__is_valid_id(id):
            msg = f"ID length should between 0 ~ {Pig.MAX_ID_LENGTH}. Get {len(id)}."
            logging.error(msg)
            raise ValueError(msg)
        self.__id = id

    def set_birthday(self, date: str | date) -> None:
        """ Set pig's birthday. Birthday should be before today.

        :param date: Pig's birthday in date or ISO format string. Such as \
            yyyy-mm-dd.
        """

        self.__birthday = transform_date(date)

    def set_dam(self, parent) -> None:
        """ Set pig's dam. Dam should be unique.

        :param parent: A unique Pig instance.
        :raises: ValueError.
        """

        type_check(parent, "parent", Pig)
        if not parent.is_unique():
            msg = f"parent shold be unique. Get {parent}."
            logging.error(msg)
            raise ValueError(msg)
        
        self.__dam = parent

    def set_sire(self, parent) -> None:
        """ Set pig's sire. Sire should be unique.

        :param parent: A unique Pig instance.
        :raises: ValueError.
        """

        type_check(parent, "parent", Pig)
        if not parent.is_unique():
            msg = f"parent shold be unique. Get {parent}."
            logging.error(msg)
            raise ValueError(msg)
        self.__sire = parent

    def set_reg_id(self, id: str) -> None:
        """ Set reg id. Reg id is an unique id which is registered in NAIF's 
        system.

        :param id: A six digit id string.
        :raises: ValueError
        """

        type_check(id, "id", str)

        if not id.isdigit() or len(id) != 6:
            msg = f"Reg id should be a six digit string. Get {id}."
            logging.error(msg)
            raise ValueError(msg)

        self.__reg_id = id

    def set_gender(self, gender: str) -> None:
        """ Set pig's gender. Gender must be defined in Pig.GENDER.

        :param gender: pig's gender.
        :raises: KeyError.
        """

        if gender not in Pig.GENDER:
            msg = f"gender should be defined in Pig.GENDER. Get {gender}."
            logging.error(msg)
            raise KeyError(msg)
        
        self.__gender = Pig.GENDER[gender]

    def set_chinese_name(self, name: str) -> None:
        """ Set a Chinese name which is shorter than 5 characters.

        :param name: a Chinese name shorter than 5 characters.
        :raises: ValueError.
        """

        type_check(name, "name", str)
        if len(name) > 5 or len(name) == 0:
            msg = f"Chinese name should be shorter than 5 characters. Get {len(name)}."
            logging.error(msg)
            raise ValueError(msg)
        self.__chinese_name = name

    def set_farm(self, farm: str) -> None:

        type_check(farm, "farm", str)
        self.__farm = farm

    def set_litter(self, litter: int) -> None:
        """ Set litter of this pig, which is the parity which it was born.

        :param litter: parity the pig was born.
        :raises TypeError: if litter is not an int.
        :raises ValueError: if litter is not in range [1,12].
        """

        type_check(litter, "litter", int)
        if litter not in range(1, 13):
            msg = f"Litter should be in range [1, 12]. Got {litter}."
            logging.error(msg)
            raise ValueError(msg)
        self.__litter = litter

    def get_breed(self):
        return self.__breed

    def get_id(self):
        return self.__id

    def get_birthday(self):
        return self.__birthday

    def get_dam(self):
        return self.__dam

    def get_dam_id(self):

        if self.__dam is None:
            return "None"
        return self.__dam.get_id()

    def get_sire(self):
        return self.__sire

    def get_sire_id(self):

        if self.__sire is None:
            return "None"
        return self.__sire.get_id()

    def get_reg_id(self):
        return self.__reg_id

    def get_gender(self):
        return self.__gender

    def get_chinese_name(self):
        return self.__chinese_name

    def get_farm(self):
        return self.__farm
    
    def get_litter(self):
        return self.__litter

    def is_unique(self):
        ''' Whether this pig has id, birthday and farm.'''
        return self.__id is not None and self.__birthday is not None and self.__farm is not None


class PregnantStatus(Enum):

    YES = "Yes"
    NO = "No"
    UNKNOWN = "Unknown"
    ABORTION = "Abortion"


class Estrus:

    PARITY_UPPER_BOUND = 12

    def __init__(
        self, 
        sow: Pig = None, 
        estrus_datetime: str | datetime = None, 
        pregnant: PregnantStatus = None, 
        parity: int = None
    ):
        """ A class represent an estrus.

        :param sow: an unique Pig object which has estrus, defaults to None
        :param estrus_datetime: a string in format "%Y-%m-%d %H:%M:%S", \
            defaults to None
        :param pregnant: pregnant status of the sow/gilt after this estrus, \
            defined as PregnantStatus enum, defaults to None
        :param parity: a non-negative int indicates how many time did the sow \
            being pregnant, defaults to None
        """
        self.__sow: Pig = None
        self.__estrus_datetime: datetime = None
        self.__pregnant: PregnantStatus = None
        self.__parity: int = None

        if sow is not None:
            self.set_sow(sow)
        if estrus_datetime is not None:
            self.set_estrus_datetime(estrus_datetime)
        if pregnant is not None:
            self.set_pregnant(pregnant)
        if parity is not None:
            self.__parity(parity)

    def __str__(self):

        id = birthday = farm = status = str(None)
        if self.__sow is not None:
            id = str(self.__sow.get_id())
            birthday = str(self.__sow.get_birthday())
            farm = str(self.__sow.get_farm())
        if self.__pregnant is not None:
            status = self.__pregnant.value


        s = "母豬耳號 id：{id}\n".format(id=str(id)) \
            + "母豬生日 birthday：{birthday}\n".format(birthday=str(birthday)) \
            + "母豬所屬牧場 farm：{farm}\n".format(farm=str(farm)) \
            + "發情日期 estrus_datetime：{date_}\n".format(date_=str(self.__estrus_datetime)) \
            + "是否懷孕 pregnant：{status}\n".format(status=str(status)) \
            + "生產批次 parity：{parity}\n".format(parity=str(self.__parity))

        return s

    def __eq__(self, __value: object) -> bool:

        if __value == None:
            return False

        if not isinstance(__value, Estrus):
            msg = f"Cannot compare Estrus to {type(__value)}."
            logging.error(msg)
            raise TypeError(msg)

        # Deal with the case that self.__sow is None.
        if self.__sow is None and __value.get_sow() is None:
            result = True
        elif self.__sow is not None and __value.get_sow() is not None:
            # I do not care other attributes of the sow.
            result = self.__sow.is_identical(__value.get_sow())
        else:
            return False

        return  result \
            and self.__estrus_datetime == __value.__estrus_datetime \
            and self.__pregnant == __value.get_pregnant() \
            and self.__parity == __value.get_parity()
    
    def is_identical(self, estrus: "Estrus") -> bool:
        """Check whether the primary key of self and estrus are same.
        
        :param estrus: an Estrus instance.
        """

        type_check(estrus, "estrus", Estrus)

        if self.__sow is not None and estrus.get_sow() is not None:
            return self.__sow.is_identical(estrus.get_sow()) \
            and self.__estrus_datetime == estrus.get_estrus_datetime()
        return False

    def is_unique(self) -> bool:

        result = self.__sow is not None
        result = result and self.__sow.is_unique()
        result = result and self.__estrus_datetime is not None
        return result

    def set_sow(self, sow: Pig):
        """ Set sow.

        The sow's birthday should be earlier than estrus datetime.

        :param sow: the sow/gilt which has estrus.
        :raises: TypeError, ValueError.
        """

        type_check(sow, "sow", Pig)

        if not sow.is_unique():
            msg = f"sow should be unique. Get {sow}."
            logging.error(msg)
            raise ValueError(msg)
        
        if self.__estrus_datetime is not None:
            if sow.get_birthday() > self.__estrus_datetime.date():
                msg = "estrus_datetime should be later than the sow's birthday."
                msg += f"\nestrus_datetime: {self.__estrus_datetime}, "
                msg += f"sow's birthday: {sow.get_birthday()}."
                logging.error(msg)
                raise ValueError(msg)

        self.__sow = sow

    def set_estrus_datetime(self, date_time: str | datetime):
        """Set estrus datetime. Estrus datetime should be the accurate date 
        and time when estrus is observed.

        The estrus_datetime should be larger than sow's birthday.

        :param date_time: a string in format "%Y-%m-%d %H:%M:%S".
        :raises: TypeError, ValueError.
        """

        if not (isinstance(date_time, (str, datetime))):
            msg = f"date_time should be a string or datetime. Got {type(date_time)}"
            logging.error(msg)
            raise TypeError(msg)
        
        if isinstance(date_time, str):
            try:
                date_time = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
            except ValueError as ex:
                logging.error(ex.args[0])
                raise ex
            
        if self.__sow is not None:
            if self.__sow.get_birthday() > date_time.date():
                msg = "estrus_datetime should be later than the sow's birthday."
                msg += f"\nestrus_datetime: {date_time}, "
                msg += f"sow's birthday: {self.__sow.get_birthday()}."
                logging.error(msg)
                raise ValueError(msg)

        self.__estrus_datetime = date_time

    def set_pregnant(self, status: PregnantStatus):
        """ Set the pregnant status after this estrus. Status is defined in 
        PregnantStatus enum.

        :param status: a PregnantStatus.
        :raises: TypeError
        """

        type_check(status, "status", PregnantStatus)
        self.__pregnant = status

    def set_parity(self, parity: int):
        """ Set parity. Parity is a non-negative int indicates how many time 
        did the sow being pregnant.

        parity should greater or equal to 1 and less than 12.

        :param parity: a non-negative int indicates how many time did the sow \
            being pregnant.
        :raises: ValueError, TypeError
        """

        type_check(parity, "parity", int)

        # I guess no sow can give birth more than 10 times.        
        if parity not in range(1, Estrus.PARITY_UPPER_BOUND):
            msg = f"parity should between 1 to 12. Got {parity}."
            logging.error(msg)
            raise ValueError(msg)

        self.__parity = parity

    def get_sow(self):
        return self.__sow

    def get_estrus_datetime(self):
        return self.__estrus_datetime

    def get_pregnant(self):
        return self.__pregnant

    def get_parity(self):
        return self.__parity


class Mating:

    def __init__(
        self, 
        estrus: Estrus = None, 
        mating_datetime: str | datetime = None, 
        boar: Pig = None
    ) -> None:
        """A class represents a mating during estrus.

        :param estrus: corresponding estrus, should be unqiue, defaults to None
        :param mating_datetime: a string in format "%Y-%m-%d %H:%M:%S", \
            defaults to None
        :param boar: the male in the mating, should be unique , defaults to None
        """
        
        self.__estrus: Estrus = None
        self.__mating_datetime: datetime = None
        self.__boar: Pig = None

        if estrus is not None:
            self.set_estrus(estrus)
        if mating_datetime is not None:
            self.set_mating_datetime(mating_datetime)
        if boar is not None:
            self.set_boar(boar)

    def __str__(self) -> str:

        if self.__estrus is not None:
            s = "\n".join([
                "母豬耳號 sow_id：{id}".format(id=str(self.__estrus.get_sow().get_id())),
                "母豬生日 sow_birthday：{birthday}".format(birthday=str(self.__estrus.get_sow().get_birthday())),
                "母豬所屬牧場 sow_farm：{farm}".format(farm=str(self.__estrus.get_sow().get_farm())),
                "發情日期 sow_estrus_datetime：{date_}".format(date_=str(self.__estrus.get_estrus_datetime())),
            ])
        else:
            s = "\n".join([
                "母豬耳號 sow_id：None",
                "母豬生日 sow_birthday：None",
                "母豬所屬牧場 sow_farm：None",
                "發情日期 sow_estrus_datetime：None"
            ])
        if self.__boar is not None:
            s = "\n".join([
                s,
                "配種日期 mating_datetime：{datetime_}".format(datetime_=str(self.__mating_datetime)),
                "公豬耳號 boar_id：{id}".format(id=str(self.__boar.get_id())),
                "公豬生日 boar_birthday：{birthday}".format(birthday=str(self.__boar.get_birthday())),
                "公豬所屬牧場 boar_farm：{farm}".format(farm=str(self.__boar.get_farm()))
            ])
        else:
            s = "\n".join([
                s,
                "配種日期 mating_datetime：{datetime_}".format(datetime_=str(self.__mating_datetime)),
                "公豬耳號 boar_id：None",
                "公豬生日 boar_birthday：None",
                "公豬所屬牧場 boar_farm：None"
            ])

        return s

    def __eq__(self, __value: object) -> bool:

        if __value == None:
            return False
        
        if not isinstance(__value, Mating):
            msg = f"Cannot compare Mating with {type(__value)}."
            logging.error(msg)
            raise TypeError(msg)
        
        return self.is_identical(__value)\
        and self.__boar == __value.get_boar()
    
    def is_identical(self, mating: "Mating") -> bool:

        type_check(mating, "mating", Mating)

        if self.__estrus is not None and mating.get_estrus() is not None:
            return self.__estrus.is_identical(mating.get_estrus())\
            and self.__mating_datetime == mating.get_mating_datetime()
        return False

    def is_unique(self) -> bool:

        return (self.__estrus is not None) and (self.__mating_datetime is not None)

    def set_estrus(self, estrus: Estrus):
        """ Set estrus.

        The gap between mating datetime and estrus datetime cannot longer than 
        three days.

        :param estrus: corresponding estrus, should be unqiue, defaults to None
        :raises: TypeError, ValueError
        """

        type_check(estrus, "estru", Estrus)

        if not estrus.is_unique():
            msg = f"estrus should be unique. Got {estrus}."
            logging.error(msg)
            raise ValueError(msg)

        if self.__mating_datetime is not None:
            delta = self.__mating_datetime - estrus.get_estrus_datetime()
            if delta > timedelta(days=3):
                msg = "The gap between estrus date and mating date is too "
                msg += "long.\nEstrus datetime: "
                msg += f"{estrus.get_estrus_datetime()}.\n Mating "
                msg += f"datetime: {self.__mating_datetime}."
                logging.error(msg)
                raise ValueError(msg)
            if delta < timedelta(days=0):
                msg = "Mating datetime should be later than estrus datetime.\n"
                msg += f"Estrus datetime: {estrus.get_estrus_datetime()}.\n"
                msg += f"Mating datetime: {self.__mating_datetime}."
                logging.error(msg)
                raise ValueError(msg)
            
        if self.__boar is not None:
            if estrus.get_estrus_datetime().date() < self.__boar.get_birthday():
                msg = "Boar birthday is later than mating date.\n"
                msg += f"Boar: {self.__boar}\n"
                msg += f"Estrus date: {estrus.get_estrus_datetime().date()}."
                logging.error(msg)
                raise ValueError(msg)

        self.__estrus = estrus

    def set_mating_datetime(self, date_time: str | datetime):
        """ Set mating datetime.
        
        The gap between mating datetime and estrus datetime cannot longer than 
        three days.

        :param date_time: a string in format "%Y-%m-%d %H:%M:%S".
        :raises: TypeError, ValueError
        """

        if not (isinstance(date_time, (str, datetime))):
            msg = f"date_time should be a string or datetime. Get {type(date_time)}."
            logging.error(msg)
            raise TypeError(msg)
        
        if isinstance(date_time, str):
            try:
                date_time = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
            except ValueError as ex:
                logging.error(ex.args[0])
                raise ex
            
        if self.__estrus is not None:
            delta = date_time - self.__estrus.get_estrus_datetime()
            if delta > timedelta(days=3) or delta < timedelta(days=0):
                msg = "The gap between estrus date and mating date is too "
                msg += "long.\nEstrus datetime: "
                msg += f"{self.__estrus.get_estrus_datetime()}.\n Mating "
                msg += f"datetime: {date_time}."
                logging.error(msg)
                raise ValueError(msg)
            if delta < timedelta(days=0):
                msg = "Mating datetime should be later than estrus datetime.\n"
                msg += f"Estrus datetime: {self.__estrus.get_estrus_datetime()}."
                msg += f"\nMating datetime: {date_time}."
                logging.error(msg)
                raise ValueError(msg)
            
        if self.__boar is not None:
            if date_time.date() < self.__boar.get_birthday():
                msg = "Boar birthday is later than mating date.\n"
                msg += f"Boar: {self.__boar}\n"
                msg += f"Mating date: {date_time}."
                logging.error(msg)
                raise ValueError(msg)

        self.__mating_datetime = date_time

    def set_boar(self, boar: Pig):
        """ Set boar. Boar is the male in the mating.

        :param boar: a unique Pig object.
        :raises: TypeError, ValueError
        """

        type_check(boar, "boar", Pig)

        if not boar.is_unique():
            msg = f"boar should be unique. Got {boar}."
            logging.error(msg)
            raise ValueError(msg)

        self.__boar = boar

        if self.__estrus is not None:
            if self.__estrus.get_estrus_datetime().date() < boar.get_birthday():
                msg = "Boar birthday is later than estrus date.\n"
                msg += f"Boar: {boar}\n Estrus date: "
                msg += f"{self.__estrus.get_estrus_datetime().date()}."
                logging.error(msg)
                raise ValueError(msg)
            
        if self.__mating_datetime is not None:
            if self.__mating_datetime.date() < boar.get_birthday():
                msg = "Boar birthday is later than mating date.\n"
                msg += f"Boar: {boar}\n Mating date: "
                msg += f"{self.__mating_datetime.date()}."
                logging.error(msg)
                raise ValueError(msg)

    def get_estrus(self) -> Estrus:

        return self.__estrus

    def get_mating_datetime(self) -> datetime:

        return self.__mating_datetime

    def get_boar(self) -> Pig:

        return self.__boar
    

class Farrowing():

    PREGNANT_LOWER_BOUND = timedelta(100)
    PREGNANT_UPPER_BOUND = timedelta(130)
    TOTAL_BORN_UPPER_BOUND = 30

    def __init__(
        self, 
        estrus: Estrus = None, 
        farrowing_date: str | date = None,
        litter_id: str = None,  
        crushed: int = None, 
        black: int = None, 
        weak: int = None, 
        malformation: int = None,
        dead: int = None,
        n_of_male: int = None,
        n_of_female: int = None,
    ) -> None:
        """A class represent a farrowing record.

        :param estrus: which estrus record is this farrowing record belongs.
        :param farrowing_date: date of farrowing, should be in ISO format.
        :param litter_id: litter id in the farm of this birth, should be a \
            numeric in range [1, 9999].
        :param crushed: number of piglets killed by being crushed by the sow.
        :param black: number of piglets born as black dead bodies.
        :param weak: number of piglets die because of weakness.
        :param malformation: number of piglets born as malformation dead bodies.
        :param dead: number of piglets born as dead bodies which have no \
            symptoms.
        :param n_of_male: total number of alive male piglets.
        :param n_of_female: total number of alive female piglets.
        :raises TypeError: if pass in wrong arguments type.
        :raises ValueError: if pass in incorrect arguments.
        """
        
        self.__estrus: Estrus = None
        self.__farrowing_date: date = None
        self.__litter_id: str = None
        self.__crushed: int = None
        self.__black: int = None
        self.__weak: int = None
        self.__malformation: int = None
        self.__dead: int = None
        self.__total_weight: float = None
        self.__n_of_male: int = None
        self.__n_of_female: int = None
        self.__note: str = None

        if estrus is not None:
            self.set_estrus(estrus)
        if farrowing_date is not None:
            self.set_farrowing_date(farrowing_date)
        if litter_id is not None:
            self.set_litter_id(litter_id)
        if crushed is not None:
            self.set_crushed(crushed)
        if black is not None:
            self.set_black(black)
        if weak is not None:
            self.set_weak(weak)
        if malformation is not None:
            self.set_malformation(malformation)
        if dead is not None:
            self.set_dead(dead)
        if n_of_male is not None:
            self.set_n_of_male(n_of_male)
        if n_of_female is not None:
            self.set_n_of_female(n_of_female)

    def __str__(self) -> str:
        
        if self.__estrus is not None:
            s = "\n".join([
                "母豬耳號 sow_id：{id}".format(id=str(self.__estrus.get_sow().get_id())),
                "母豬生日 sow_birthday：{birthday}".format(birthday=str(self.__estrus.get_sow().get_birthday())), 
                "母豬所屬牧場 sow_farm：{farm}".format(farm=str(self.__estrus.get_sow().get_farm())),
                "發情日期 sow_estrus_datetime：{date_}".format(date_=str(self.__estrus.get_estrus_datetime())),
            ])
        else:
            s = "\n".join([
                "母豬耳號 sow_id：None",
                "母豬生日 sow_birthday：None", 
                "母豬所屬牧場 sow_farm：None", 
                "發情日期 sow_estrus_datetime：None"
            ])
        s = "\n".join([
            s,
            "分娩日期 farrowing_date：{date}".format(date=str(self.__farrowing_date)),
            "壓死 crushing：{crushing}".format(crushing=str(self.__crushed)),
            "黑胎 black：{black}".format(black=str(self.__black)),
            "體弱 weak：{weak}".format(weak=str(self.__weak)),
            "畸形 malformation:{malformation}".format(malformation=str(self.__malformation)),
            "死胎 dead：{dead}".format(dead=str(self.__dead)),
            "總仔數 total_born：{total_born}".format(total_born=str(self.get_total_born())),
            "活仔數 born_alive：{born_alive}".format(born_alive=str(self.get_born_alive())),
            "死仔數 born_dead：{born_dead}".format(born_dead=str(self.get_born_dead())),
            "公豬數 n_of_male：{male}".format(male=str(self.__n_of_male)),
            "母豬數 n_of_female：{female}".format(female=str(self.__n_of_female)),
        ])

        return s
    
    def __eq__(self, __value: object) -> bool:
        
        if __value is None:
            return False
        
        if not isinstance(__value, Farrowing):
            raise TypeError("Can not compare Farrowing with {type_}".format(type_=str(type(__value))))
        
        return self.is_identical(__value)\
            and (self.__farrowing_date == __value.get_farrowing_date()) \
            and (self.__crushed == __value.get_crushed()) \
            and (self.__black == __value.get_black()) \
            and (self.__weak == __value.get_weak()) \
            and (self.__malformation == __value.get_malformation()) \
            and (self.__dead == __value.get_dead())\
            and (self.__n_of_male == __value.get_n_of_male()) \
            and (self.__n_of_female == __value.get_n_of_female())\
            and self.__litter_id == __value.get_litter_id()
    
    def __check_total_born(self) -> None:
        """Check whether total born is smaller or equal to 30.

        :param added: number want to add after check.
        :raises ValueError: if total born is larger than 30.
        """

        if self.get_total_born() > Farrowing.TOTAL_BORN_UPPER_BOUND:
            msg = "total born can not be larger than 30. "
            msg += f"Got {self.get_total_born()}."
            logging.error(msg)
            raise ValueError(msg)
        
    def is_identical(self, farrowing: "Farrowing") -> bool:

        type_check(farrowing, "farrowing", Farrowing)

        if self.__estrus is not None:
            return self.__estrus.is_identical(farrowing.get_estrus())
        return False
        
    def is_unique(self) -> bool:

        return self.__estrus is not None

    def set_estrus(self, estrus: Estrus) -> None:
        """Set the estrus which this farrowing record belongs to.

        estrus date must in range [farrowing date - 130, farrowing date - 100].

        :param estrus: an unique Estrus object.
        :raises TypeError: if pass in incorrect type.
        :raises ValueError: if pass in not unique `estrus`
        :raises ValueError: if farrowing date - estrus date is larger than 130 \
            days or smaller than 100 days.
        """

        type_check(estrus, "estrus", Estrus)
        
        if not estrus.is_unique():
            msg = f"estrus should be unique. \nGot {estrus}."
            logging.error(msg)
            raise ValueError(estrus)
        
        if self.__farrowing_date is not None:
            estrus_date = estrus.get_estrus_datetime().date()
            farrowing_date = self.__farrowing_date # Make name shorter.
            if farrowing_date - estrus_date > Farrowing.PREGNANT_UPPER_BOUND:
                msg = f"Time gap between estrus date is longer than 130 days."
                msg += f"\nestrus date: {estrus_date}."
                msg += f"\nfarrowing date: {self.__farrowing_date}."
                logging.error(msg)
                raise ValueError(msg)
            if farrowing_date - estrus_date < Farrowing.PREGNANT_LOWER_BOUND:
                msg = f"Time gap between estrus date is shorter than 100 days."
                msg += f"\nestrus date: {estrus_date}."
                msg += f"\nfarrowing date: {self.__farrowing_date}."
                logging.error(msg)
                raise ValueError(msg)
            
        self.__estrus = estrus

    def set_farrowing_date(self, farrowing_date: str | date) -> None:
        """Set farrowing date.

        farrowing date must in range [estrus date + 100, estrus date + 130]

        :param farrowing_date: a string in ISO date format or a datetime.date \
            object.
        :raises TypeError: if pass in incorrect argument type.
        :raises ValueError: if string format incorrect.
        :raises ValueError: if farrowing date not in range.
        """
        
        farrowing_date = transform_date(farrowing_date)
        if self.__estrus is not None:
            estrus_date = self.__estrus.get_estrus_datetime().date()
            if farrowing_date - estrus_date > Farrowing.PREGNANT_UPPER_BOUND:
                msg = f"Time gap between estrus date is longer than 130 days."
                msg += f"\nestrus date: {estrus_date}."
                msg += f"\nfarrowing date: {farrowing_date}."
                logging.error(msg)
                raise ValueError(msg)
            if farrowing_date - estrus_date < Farrowing.PREGNANT_LOWER_BOUND:
                msg = f"Time gap between estrus date is shorter than 100 days."
                msg += f"\nestrus date: {estrus_date}."
                msg += f"\nfarrowing date: {farrowing_date}."
                logging.error(msg)
                raise ValueError(msg)
            
        self.__farrowing_date = farrowing_date
  
    def set_litter_id(self, litter_id: str) -> None:
        """Set the litter id in the farm of this birth.

        The id can include leading zero and those zeros will be remained.
        
        :param litter_id: litter id in the farm of this birth, should be a \
            numeric in range [1,9999].
        :raises TypeError: if litter_id is not a string.
        :raises ValueError: if litter_id is not a numeric.
        :raises ValueError: if int(litter_id) is not in range [1, 9999].
        """

        type_check(litter_id, "litter_id", str)

        if not litter_id.isnumeric():
            msg = f"litter_id must be a numeric. Got {litter_id}."
            logging.error(msg)
            raise ValueError(msg)
        
        litter_num = int(litter_id)
        if litter_num not in range(1, 10000):
            msg = f"litter_id must be in range [1, 9999]. Got {litter_id}."
            logging.error(msg)
            raise ValueError(msg)
        
        self.__litter_id = litter_id
    
    def set_crushed(self, crushed: int) -> None:
        """Set the number of piglets killed by being crushed by the sow.

        :param crushed: the number of piglets killed by being crushed by the sow.
        :raises TypeError: if pass in incorrect argument type.
        :raises ValueError: if crushed is smaller than 0.
        :raises ValueError: if total born is larger than 30.
        """

        type_check(crushed, "crushed", int)
        if crushed < 0:
            msg = f"crushed can not be smaller than 0. Got {crushed}."
            logging.error(msg)
            raise ValueError(msg)
        
        old = self.__crushed
        try:
            self.__crushed = crushed
            self.__check_total_born()
        except ValueError as e:
            self.__crushed = old
            raise e

    def set_black(self, black: int) -> None:
        """Set the number of piglets born as black dead bodies.

        :param black: number of piglets born as black dead bodies.
        :raises TypeError: if pass in incorrect argument type.
        :raises ValueError: if black is smaller than 0.
        :raises ValueError: if total born is larger than 30.
        """

        type_check(black, "black", int)

        if black < 0:
            msg = f"black can not be smaller than 0. Got {black}."
            logging.error(msg)
            raise ValueError(msg)
        
        old = self.__black
        try:
            self.__black = black
            self.__check_total_born()
        except Exception as e:
            self.__black = old
            raise e

    def set_weak(self, weak: int) -> None:
        """Set the number of piglets die because of weakness.

        :param weak: number of piglets die because of weakness.
        :raises TypeError: if pass in incorrect argument type.
        :raises ValueError: if weak is smaller than 0.
        :raises ValueError: if total born is larger than 30.
        """

        type_check(weak, "weak", int)

        if weak < 0:
            msg = f"weak can not be smaller than 0. Got {weak}."
            logging.error(msg)
            raise ValueError(msg)
        
        old = self.__weak
        try:
            self.__weak = weak
            self.__check_total_born()
        except Exception as e:
            self.__weak = old
            raise e

    def set_malformation(self, malformation: int) -> None:
        """Set the number of piglets born as malformation dead bodies.

        :param malformation: number of piglets born as malformation dead bodies.
        :raises TypeError: if pass in incorrect argument type.
        :raises ValueError: if malformation is smaller than 0.
        :raises ValueError: if total born is larger than 30.
        """

        type_check(malformation, "malformation", int)

        if malformation < 0:
            msg = f"malformation can not be smaller than 0. Got {malformation}."
            logging.error(msg)
            raise ValueError(msg)
        
        old = self.__malformation
        try:
            self.__malformation = malformation
            self.__check_total_born()
        except Exception as e:
            self.__malformation = old
            raise e

    def set_dead(self, dead: int) -> None:
        """Set number of piglets born as dead bodies which have no symptoms.\

        :param dead: number of piglets born as dead bodies which have no \
            symptoms.
        :raises TypeError: if pass in incorrect argument type.
        :raises ValueError: if dead is smaller than 0.
        :raises ValueError: if total born is larger than 30.
        """

        type_check(dead, "dead", int)

        if dead < 0:
            msg = f"dead can not be smaller than 0. Got {dead}."
            logging.error(msg)
            raise ValueError(msg)
        
        old = self.__dead
        try:
            self.__dead = dead
            self.__check_total_born()
        except Exception as e:
            self.__dead = old
            raise e

    def set_n_of_male(self, n_of_male: int) -> None:
        """Set the total number of alive male piglets.

        :param n_of_male: total number of alive male piglets.
        :raises TypeError: if pass in incorrect argument type.
        :raises ValueError: if n_of_male is smaller than 0.
        :raises ValueError: if total born is larger than 30.
        """

        type_check(n_of_male, "n_of_male", int)

        if n_of_male < 0:
            msg = f"n_of_male can not be smaller than 0. Got {n_of_male}."
            logging.error(msg)
            raise ValueError(msg)

        old = self.__n_of_male
        try:
            self.__n_of_male = n_of_male
            self.__check_total_born()
        except Exception as e:
            self.__n_of_male = old
            raise e

    def set_n_of_female(self, n_of_female: int) -> None:
        """Set the total number of alive female piglets.

        :param n_of_male: total number of alive female piglets.
        :raises TypeError: if pass in incorrect argument type.
        :raises ValueError: if n_of_female is smaller than 0.
        :raises ValueError: if total born is larger than 30.
        """

        type_check(n_of_female, "n_of_male", int)

        if n_of_female < 0:
            msg = f"n_of_female can not be smaller than 0. Got {n_of_female}."
            logging.error(msg)
            raise ValueError(msg)

        old = self.__n_of_female
        try:
            self.__n_of_female = n_of_female
            self.__check_total_born()
        except Exception as e:
            self.__n_of_female = old
            raise e

    def get_estrus(self) -> Estrus:
        return self.__estrus
    
    def get_farrowing_date(self) -> date:
        return self.__farrowing_date
    
    def get_litter_id(self) -> str:
        return self.__litter_id
    
    def get_crushed(self) -> int:
        return self.__crushed
    
    def get_black(self) -> int:
        return self.__black
    
    def get_weak(self) -> int:
        return self.__weak
    
    def get_malformation(self) -> int:
        return self.__malformation
    
    def get_dead(self) -> int:
        return self.__dead
    
    def get_n_of_male(self) -> int:
        return self.__n_of_male
    
    def get_n_of_female(self) -> int:
        return self.__n_of_female
    
    def get_born_alive(self) -> int:
        return add_with_none(self.__n_of_male, self.__n_of_female)        
        
    def get_born_dead(self) -> int:
        return add_with_none(
            self.__crushed, 
            self.__black, 
            self.__malformation, 
            self.__weak, 
            self.__dead
        )

    def get_total_born(self) -> int:
        return self.get_born_alive() + self.get_born_dead()
    

class Weaning:

    NURSING_DATE_UPPER_BOUND = timedelta(40)
    NURSING_DATE_LOWER_BOUND = timedelta(14)
    NURSED_UPPER_BOUND = 30

    def __init__(
        self, 
        farrowing: Farrowing = None, 
        weaning_date: str | date = None, 
        total_nursed_piglets: int = None, 
        total_weaning_piglets: int = None, 
    ) -> None:
        """A class represents a weaning record.

        The primary key of Weaning is estrus. However, corresponding farrowing 
        data should be in the database.

        :param farrowing: an unique Farrowing.
        :param weaning_date: weaning date.
        :param total_nursed_piglets: number of piglets at the beginning \
            of nursing, which should equal to total born alive + number of \
            fosterred piglets.
        :param total_weaning_piglets: number of alive piglets when weaning. 
        :raises TypeError: if pass in wrong arguments type.
        :raises ValueError: if pass in incorrect arguments.
        """
        
        self.__farrowing: Farrowing = None
        self.__weaning_date: date = None
        self.__total_nursed_piglets: int = None
        self.__total_weaning_piglets: int = None

        if farrowing is not None:
            self.set_farrowing(farrowing)
        if weaning_date is not None:
            self.set_weaning_date(weaning_date)
        if total_nursed_piglets is not None:
            self.set_total_nursed_piglets(total_nursed_piglets)
        if total_weaning_piglets is not None:
            self.set_total_weaning_piglets(total_weaning_piglets)

    def __str__(self) -> str:

        s = ""
        if self.__farrowing is not None:
            s = "\n".join([
                f"耳號 id: {self.__farrowing.get_estrus().get_sow().get_id()}", 
                f"生日 birthday: {str(self.__farrowing.get_estrus().get_sow().get_birthday())}", 
                f"牧場 farm: {self.__farrowing.get_estrus().get_sow().get_farm()}"
            ])

        s = "\n".join([
            s, 
            f"離乳日 weaning_date: {self.__weaning_date}",
            f"哺乳數 total_nursed_piglets: {self.__total_weaning_piglets}", 
            f"離乳數 total_weaning_piglets: {self.__total_weaning_piglets}"
        ])

        return s
    
    def __eq__(self, __value: object) -> bool:

        if __value is None:
            return False
        
        if not isinstance(__value, Weaning):
            msg = f"Can not compare Weaning to {type(__value)}."
            logging.error(msg)
            raise TypeError(msg)
        
        return self.is_identical(__value) \
            and (self.__weaning_date == __value.get_weaning_date()) \
            and (self.__total_nursed_piglets == __value.get_total_nursed_piglets()) \
            and (self.__total_weaning_piglets == __value.get_total_weaning_piglets())
    
    def is_identical(self, weaning: "Weaning") -> bool:

        if self.__farrowing is not None:
            return self.__farrowing.is_identical(weaning.get_farrowing())
        return False
    
    def is_unique(self) -> bool:
        
        return self.__farrowing is not None

    def set_farrowing(self, farrowing: Farrowing) -> None:
        """Set the farrowing which this weaning record belongs to.

        Farrowing date must in range [weaning date - 40, weaning date - 14].

        :param farrowing: an unique Farrowing object.
        :raises ValueError: if farrowing is not unique.
        :raises ValueError: if farrowing date out of range.
        """
        
        type_check(farrowing, "farrowing", Farrowing)

        if not farrowing.is_unique():
            msg = f"farrowing should be unique. \nGot {farrowing}."
            logging.error(msg)
            raise ValueError(farrowing)

        farrowing_date = farrowing.get_farrowing_date()
        if self.__weaning_date is not None and farrowing_date is not None:
            weaning_date = self.__weaning_date
            if weaning_date - farrowing_date < Weaning.NURSING_DATE_LOWER_BOUND:
                msg = "The nursing time is too short.\n"
                msg += f"Weaning date: {self.__weaning_date}. \n"
                msg += f"Farrowing date: {farrowing_date}."
                logging.error(msg)
                raise ValueError(msg)
            if weaning_date - farrowing_date > Weaning.NURSING_DATE_UPPER_BOUND:
                msg = "The nursing time is too long.\n"
                msg += f"Weaning date: {self.__weaning_date}. \n"
                msg += f"Farrowing date: {farrowing_date}."
                logging.error(msg)
                raise ValueError(msg)
            
        self.__farrowing = farrowing

    def set_weaning_date(self, weaning_date: str | date) -> None:
        """Set weaning date.

        Weaning date must in range [farrowing date + 14, farrowing date + 40].

        :param weaning_date: weaning date in ISO format.
        :raises TypeError: if weaning_date is not string or datetime.date.
        :raises ValueError: if weaning_date not in ISO format.
        :raises ValueError: if weaning_date out of range.
        """
        
        weaning_date = transform_date(weaning_date)
        farrowing_date = None
        if self.__farrowing is not None:
            farrowing_date = self.__farrowing.get_farrowing_date()
        if farrowing_date is not None:
            if weaning_date - farrowing_date < Weaning.NURSING_DATE_LOWER_BOUND:
                msg = "The nursing time is too short.\n"
                msg += f"Weaning date: {weaning_date}. \n"
                msg += f"Farrowing date: {farrowing_date}."
                logging.error(msg)
                raise ValueError(msg)
            if weaning_date - farrowing_date > Weaning.NURSING_DATE_UPPER_BOUND:
                msg = "The nursing time is too long.\n"
                msg += f"Weaning date: {weaning_date}. \n"
                msg += f"Farrowing date: {farrowing_date}."
                logging.error(msg)
                raise ValueError(msg)
        self.__weaning_date = weaning_date

    def set_total_nursed_piglets(self, total_nursed_piglets: int) -> None:
        """Set number of piglets at the beginning of nursing, which should 
        equal to total born alive + number of fosterred piglets.

        total_nursed_piglets must be in range (0, 30]

        :param total_nursed_piglets: number of piglets at the beginning of \
            nursing, which should equal to total born alive + number of \
            fosterred piglets.
        :raises TypeError: if total_nursed_piglets is not int.
        :raises ValueError: if total_nursed_piglets is smaller than 0.
        :raises ValueError: if total_nursed_piglets is greater than 30.
        :raises ValueError: if total_nursed_piglets is less than \
            total_weaning_piglets.
        """
        
        type_check(total_nursed_piglets, "total_nursed_piglets", int)
        
        if total_nursed_piglets <= 0:
            msg = "total_nursed_piglets must be greater than 0. "
            msg += f"Got {total_nursed_piglets}."
            logging.error(msg)
            raise ValueError(msg)
        if total_nursed_piglets > Weaning.NURSED_UPPER_BOUND:
            msg = "total_nursed_piglets must be smaller than 30. "
            msg += f"Got {total_nursed_piglets}."
            logging.error(msg)
            raise ValueError(msg)
        if self.__total_weaning_piglets is not None:
            if total_nursed_piglets < self.__total_weaning_piglets:
                msg = "total_nursed_piglets must be more than "
                msg += "total_weaning_piglets. \n"
                msg += f"total_nursed_piglets: {total_nursed_piglets}. \n"
                msg += f"total_weaning_piglets: {self.__total_weaning_piglets}."
                logging.error(msg)
                raise ValueError(msg)
        
        self.__total_nursed_piglets = total_nursed_piglets

    def set_total_weaning_piglets(self, total_weaning_piglets: int) -> None:
        """Set number of alive piglets when weaning.

        total_weaning_piglets must in range [0, 30] and smaller or equal to 
        total_nursed_piglets.

        :param total_weaning_piglets: number of alive piglets when weaning.
        :raises TypeError: if total_weaning_piglets is not int.
        :raises ValueError: if total_weaning_piglets not in range.
        :raises ValueError: if total_weaning_piglets > total_nursed_piglets.
        """

        type_check(total_weaning_piglets, "total_weaning_piglets", int)

        if total_weaning_piglets < 0:
            msg = "total_weaning_piglets must be greater or equal to 0. "
            msg += f"Got {total_weaning_piglets}."
            logging.error(msg)
            raise ValueError(msg)
        if total_weaning_piglets > Weaning.NURSED_UPPER_BOUND:
            msg = "total_weaning_piglets must be smaller or equal to 30. "
            msg += f"Got {total_weaning_piglets}."
            logging.error(msg)
            raise ValueError(msg)
        if self.__total_nursed_piglets is not None:
            if total_weaning_piglets > self.__total_nursed_piglets:
                msg = "total_nursed_piglets must be more than "
                msg += "total_weaning_piglets. \n"
                msg += f"total_nursed_piglets: {self.__total_nursed_piglets}. \n"
                msg += f"total_weaning_piglets: {total_weaning_piglets}."
                logging.error(msg)
                raise ValueError(msg)

        self.__total_weaning_piglets = total_weaning_piglets
        
    def get_farrowing(self) -> Farrowing:
        return self.__farrowing
    
    def get_weaning_date(self) -> date:
        return self.__weaning_date
    
    def get_total_nursed_piglets(self) -> int:
        return self.__total_nursed_piglets
    
    def get_total_weaning_piglets(self) -> int:
        return self.__total_weaning_piglets
    

class Individual:

    def __init__(
        self, 
        birth_litter: Farrowing = None, 
        nurse_litter: Weaning = None, 
        in_litter_id: str = None, 
        born_weight: float = None, 
        weaning_weight: float = None
    ) -> None:
        """The individual info of a piglet.
        
        :param birth_litter: the farrowing which the piglet born.
        :param nurse_litter: the weaning which the piglet was nursed.
        :param in_litter_id: the piglet id in birth litter.
        :param born_weight: born weight in kg.
        :param weaning_weight: weaning weight in kg.
        :raises TypeError: if pass in incorrect type.
        """
        
        self.__birth_litter: Farrowing = None
        self.__nurse_litter: Weaning = None
        self.__in_litter_id: str = None
        self.__born_weight: float = None
        self.__weaning_weight: float = None

        if birth_litter is not None:
            self.set_birth_litter(birth_litter)
        if nurse_litter is not None:
            self.set_nurse_litter(nurse_litter)
        if in_litter_id is not None:
            self.set_in_litter_id(in_litter_id)
        if born_weight is not None:
            self.set_born_weight(born_weight)
        if weaning_weight is not None:
            self.set_weaning_weight(weaning_weight)
    
    def __str__(self) -> str:
        
        descriptions = [
            "Individual: ", 
            f"Birth litter: {str(self.__birth_litter)}", 
            f"Nurse litter: {str(self.__nurse_litter)}",
            f"In litter id: {str(self.__in_litter_id)}", 
            f"Born weight: {str(self.__born_weight)}" 
            f"Weaning weight: {str(self.__weaning_weight)}"
        ]
        return "\n".join(descriptions)
    
    def __eq__(self, __value: object) -> bool:
        
        if __value is None:
            return False
        
        if not isinstance(__value, Individual):
            msg = f"Can not compare Individual to {type(__value)}."
            logging.error(msg)
            raise TypeError(msg)
        
        if self.__nurse_litter is not None:
            result = self.__nurse_litter.is_identical(__value.get_nurse_litter())
        elif self.__nurse_litter is None and __value.get_nurse_litter() is None:
            result = True
        else:
            return False
        
        return self.is_identical(__value)\
        and result\
        and self.__born_weight == __value.get_born_weight()\
        and self.__weaning_weight == __value.get_weaning_weight()
    
    def is_identical(self, individual: "Individual") -> bool:

        if self.__birth_litter is not None:
            return self.__birth_litter.is_identical(individual.get_birth_litter())\
            and self.__in_litter_id == individual.get_in_litter_id()
        return False
    
    def is_unique(self) -> bool:

        return self.__birth_litter is not None and self.__in_litter_id is not None
    
    def __check_birthdate_and_weaning_date(
            self, 
            birthdate: date, 
            weaning_date: date
        ) -> None:
        """Check whether birthdate is earlier than weaning date. 
        
        Raise a ValueError if birthdate is later than weaning date.
        :param birthdate: piglet birthdate.
        :param weaning_date: piglet weaning date.
        """

        if weaning_date < birthdate:
            msg = "Birthdate must be earlier than weaning date. "
            msg += f"Birthdate: {birthdate}. "
            msg += f"Weaning date: {weaning_date}."
            logging.error(msg)
            raise ValueError(msg)
    
    def set_birth_litter(self, birth_litter: Farrowing) -> None:
        """Set the farrowing which the piglet born.
        
        :param birth_litter: the farrowing which the piglet born. Must be an \
            unqiue Farrowing.
        :raises TypeError: if birth_litter is not a Farrowing.
        :raises ValueError: if birth_litter is not unique.
        :raises ValueError: if weaning date is earlier than birthdate.
        """
        
        type_check(birth_litter, "birth_litter", Farrowing)
        
        if not birth_litter.is_unique():
            msg = f"birth_litter should be unique. \nGot {birth_litter}."
            logging.error(msg)
            raise ValueError(msg)
        
        birthdate = birth_litter.get_farrowing_date()
        weaning_date = None
        if self.get_nurse_litter() is not None:
            weaning_date = self.get_nurse_litter().get_weaning_date()
        if birthdate is not None and weaning_date is not None:
            self.__check_birthdate_and_weaning_date(birthdate, weaning_date)
        
        self.__birth_litter = birth_litter

    def set_nurse_litter(self, nurse_litter: Weaning) -> None:
        """Set the weaning which the piglet was nursed.

        :param nurse_litter: an unique Weaning.
        :raises TypeError: if nurse_litter is not a Weaning.
        :raises ValueError: if nurse_litter is not unique.
        :raises ValueError: if weaning date is earlier than birthdate.
        """
        
        type_check(nurse_litter, "nurse_litter", Weaning)

        if not nurse_litter.is_unique():
            msg = f"weaning_litter should be unique. \nGot {nurse_litter}."
            logging.error(msg)
            raise ValueError(msg)
        
        birthdate = None
        weaning_date = nurse_litter.get_weaning_date()
        if self.get_birth_litter() is not None:
            birthdate = self.get_birth_litter().get_farrowing_date()
        if birthdate is not None and weaning_date is not None:
            self.__check_birthdate_and_weaning_date(birthdate, weaning_date)
        
        self.__nurse_litter = nurse_litter
        
    def set_in_litter_id(self, in_litter_id: str) -> None:
        """Set the piglet id in birth litter.

        :param in_litter_id: the piglet id in birth litter.
        :raises TypeError: if in_litter_id is not a string.
        :raises ValueError: if in_litter_id is not a numeric.
        :raises ValueError: if in_litter_id not in range [1, 30].
        """

        type_check(in_litter_id, "in_litter_id", str)
        
        if not in_litter_id.isnumeric():
            msg = f"in_litter_id should be a numeric. Got {in_litter_id}."
            logging.error(msg)
            raise ValueError(msg)
        
        if int(in_litter_id) not in range(1, 31):
            msg = f"in_litter_id should be in range [1, 30]. Got {in_litter_id}."
            logging.error(msg)
            raise ValueError(msg)
        
        self.__in_litter_id = in_litter_id

    def set_born_weight(self, born_weight: int | float) -> None:
        """Set the born weight in kg of the piglet.

        :param born_weight: the born weight in kg.
        :raises TypeError: if born_weight is not an int or a float.
        :raises ValueError: if born_weight <= 0.
        """

        if isinstance(born_weight, int):
            born_weight = float(born_weight)
        type_check(born_weight, "born_weight", float)

        if born_weight <= 0:
            msg = f"born_weight must be greater than 0. Got {born_weight}."
            logging.error(msg)
            raise ValueError(msg)
        
        self.__born_weight = born_weight

    def set_weaning_weight(self, weaning_weight: float) -> None:
        """Set the weaning weight in kg of the piglet.

        :param weaning_weight: the weaning weight in kg.
        :raises TypeError: if weaning_weight is not an int or a float.
        :raises ValueError: if weaning_weight <= 0.
        """

        if isinstance(weaning_weight, int):
            weaning_weight = float(weaning_weight)
        type_check(weaning_weight, "weaning_weight", float)

        if weaning_weight <= 0:
            msg = f"weaning_weight must be greater than 0. Got {weaning_weight}."
            logging.error(msg)
            raise ValueError(msg)
        
        self.__weaning_weight = weaning_weight

    def get_birth_litter(self) -> Farrowing:
        return self.__birth_litter
    
    def get_nurse_litter(self) -> Weaning:
        return self.__nurse_litter
    
    def get_in_litter_id(self) -> str:
        return self.__in_litter_id
    
    def get_born_weight(self) -> float:
        return self.__born_weight
    
    def get_weaning_weight(self) -> float:
        return self.__weaning_weight