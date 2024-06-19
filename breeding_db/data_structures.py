import logging
from enum import Enum
from datetime import date, datetime, timedelta

from breeding_db.general import type_check, transform_date


class Pig:

    # Define enums.
    BREED = ("L", "Y", "D") # Acceptable breeds.
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
        farm: str = None
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
            and self.get_sire_id() == other.get_sire_id()

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

    def is_unique(self):
        ''' Whether this pig has id, birthday and farm.'''
        return self.__id is not None and self.__birthday is not None and self.__farm is not None


class PregnantStatus(Enum):

    YES = "Yes"
    NO = "No"
    UNKNOWN = "Unknown"
    ABORTION = "Abortion"


class Estrus:

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

        if sow is not None:
            self.set_sow(sow)
        else:
            self.__sow: Pig = None
        if estrus_datetime is not None:
            self.set_estrus_datetime(estrus_datetime)
        else:
            self.__estrus_datetime: datetime = None
        if pregnant is not None:
            self.set_pregnant(pregnant)
        else:
            self.__pregnant: PregnantStatus = None
        if parity is not None:
            self.__parity(parity)
        else:
            self.__parity: int = None

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
        result = True
        if (self.__sow is None) ^ (__value.get_sow() is None):
            return False
        elif (self.__sow is not None) and (__value.get_sow() is not None):
            # I do not care other attributes of the sow.
            result = self.__sow.is_identical(__value.get_sow())

        return  result \
            and self.__estrus_datetime == __value.__estrus_datetime \
            and self.__pregnant == __value.get_pregnant() \
            and self.__parity == __value.get_parity()

    def is_unique(self) -> bool:

        result = self.__sow is not None
        result = result and self.__sow.is_unique()
        result = result and self.__estrus_datetime is not None
        return result

    def set_sow(self, sow: Pig):
        """ Set sow.

        :param sow: the sow/gilt which has estrus.
        :raises: TypeError, ValueError
        """

        type_check(sow, "sow", Pig)

        if not sow.is_unique():
            msg = f"sow should be unique. Get {sow}."
            logging.error(msg)
            raise ValueError(msg)

        self.__sow = sow

    def set_estrus_datetime(self, date_time: str | datetime):
        """Set estrus datetime. Estrus datetime should be the accurate date 
        and time when estrus is observed.

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

        parity should greater or equal to 0 and less than 12.

        :param parity: a non-negative int indicates how many time did the sow \
            being pregnant.
        :raises: ValueError, TypeError
        """

        type_check(parity, "parity", int)

        # I guess no sow can give birth more than 10 times.        
        if parity < 0 or parity > 12:
            msg = f"parity should between 0 to 12. Got {parity}."
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

        if estrus is not None:
            self.set_estrus(estrus)
        else:
            self.__estrus: Estrus = None
        if mating_datetime is not None:
            self.set_mating_datetime(mating_datetime)
        else:
            self.__mating_datetime: datetime = None
        if boar is not None:
            self.set_boar(boar)
        else:
            self.__boar: Pig = None

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

        # Deal with the case that self.__boar is None
        result = True
        if (self.__boar is None) ^ (__value.get_boar() is None):
            return False
        elif (self.__boar is not None) and (__value.get_boar() is not None):
            # I do not care other attributes of the boar.
            result = self.__boar.is_identical(__value.get_boar())

        return \
            (self.__estrus == __value.get_estrus()) \
            and (self.__mating_datetime == __value.get_mating_datetime()) \
            and result

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

    def get_estrus(self) -> Estrus:

        return self.__estrus

    def get_mating_datetime(self) -> datetime:

        return self.__mating_datetime

    def get_boar(self) -> Pig:

        return self.__boar