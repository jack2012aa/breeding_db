from enum import Enum
from datetime import timedelta

from data_structures.pig import Pig
from data_structures.estrus import Estrus
from data_structures.estrus import PregnantStatus
from data_structures.mating import Mating
from data_structures.farrowing import Farrowing
from general import ask
from general import transform_date
from models.estrus_model import EstrusModel


class Factory():

    def __init__(self):

        self.__review_flag = 0
        self.error_messages = []

    def _turn_on_flag(self, flag: int):
        self.__review_flag = self.__review_flag | flag

    def _turn_off_flag(self, flag: int):
        self.__review_flag = self.__review_flag & ~flag

    def check_flag(self, flag: int) -> bool:
        return self.__review_flag & flag != 0

    def get_flag(self):
        return self.__review_flag


class PigFactory(Factory):

    class Flags(Enum):
        BREED_FLAG = 1
        ID_FLAG = 2
        BIRTHDAY_FLAG = 4
        SIRE_FLAG = 8
        DAM_FLAG = 16
        REG_FLAG = 32
        GENDER_FLAG = 64

    def __init__(self):
        self.pig = Pig()
        super().__init__()

    def get_breed_abbrevation(self, breed: str) -> str:
        '''Return the first letter of breed in upper case as the abbrevation of the breed.'''

        return breed.upper()[0]

    def translate_breed_to_english(self, breed: str) -> str:
        '''Return the English of breed'''

        return Pig.BREED_DICT[breed]

    def remove_dash_from_id(self, id: str) -> str:
        '''
        * Remove the dash in an id. 
        * Remove none numeric characters.
        * Add additional zero to the later hind of dash.
        * Ex: 1234-2 -> 123402
        * If more than one dash appear in id, only string before the second string will be considered.
        * Ex: 1234-2-2 -> 123402
        * If any character is in the id, only string between first two characters will be considered.
        * Ex: 20Y1234-2cao -> 123402
        * Ex: 20Y1234-12 -> 123412
        * Ex: 1234-2cao -> 123402
        '''

        if not isinstance(id, str):
            raise TypeError("id should be a string. Get {type_}".format(type_=str(type(id))))

        # Deal with the dash
        if "-" in id:
            front, hind = id.split('-')[0:2]
            # Add additional 0
            try:
                hind = hind + "tail"
                int(hind[0:2])
                hind = hind[0:2]
            except:
                hind = '0' + hind[0]
            id = front + hind

        # Find the index of every nonnumeric characters and slice the string between them.
        nonnumeric = []
        for i in range(len(id)):
            if not id[i].isnumeric():
                nonnumeric.append(i)
        if len(nonnumeric) > 0:
            slices = []
            for i in nonnumeric:
                slices.append(id[:i])
                id = id[i:]
            slices.append(id)
            # The longest digits is the most possible to be the id.
            id = max(slices, key=len, default="")

        return self.remove_nonnumeric(id)

    def remove_nonnumeric(self, s: str) -> str:
        ''' Remove all nonnumeric characters in s.'''

        result = ''
        for c in s:
            if c.isnumeric():
                result = ''.join([result,c])
        return result

    def set_gender(self, gender:str):

        try:
            self.pig.set_gender(gender)
        except KeyError as error:
            self._turn_on_flag(self.Flags.GENDER_FLAG.value)
            self.error_messages.append(str(error))

    def set_birthday(self, date):
        '''
        * param date: in ISO format or a `date` object.
        * Raise TypeError
        '''

        try:
            self.pig.set_birthday(date)
            return
        except ValueError:
            self.error_messages.append("日期格式不是 ISO format")
            self._turn_on_flag(self.Flags.BIRTHDAY_FLAG.value)
            return
        except TypeError as error:
            self.error_messages.append(str(error))
            self._turn_on_flag(self.Flags.BIRTHDAY_FLAG.value)
            raise error

    def set_reg_id(self, reg: str) -> None:
        '''* Raise `TypeError`'''

        if reg in [
            "",
            "無登",
            ]:
            return None

        try:
            self.pig.set_reg_id(reg)
        except TypeError as error:
            self._turn_on_flag(self.Flags.REG_FLAG.value)
            self.error_messages.append(str(error))
            raise error
        except ValueError as error:
            if not reg.isnumeric():
                n_reg = self.remove_nonnumeric(reg)
                if ask("是否可以將登錄號從 {reg} 修改為 {n_reg} ？".format(reg=reg,n_reg=n_reg)):
                    self.pig.set_reg_id(n_reg)
                    return None
            self._turn_on_flag(self.Flags.REG_FLAG.value)
            self.error_messages.append(str(error))
            return None

    def set_farm(self, farm: str):
        ''' * Raise TypeError'''

        try:
            self.pig.set_farm(farm)
        except TypeError as error:
            raise error

    def set_chinese_name(self, name: str):
        ''' * Raise TypeError'''

        try:
            self.pig.set_chinese_name(name)
        except TypeError as error:
            raise error


class ParentError(BaseException):

    def __init__(self, message):
        super().__init__(message)


class EstrusFactory(Factory):

    class Flags(Enum):

        SOW_FLAG = 1
        ESTRUS_DATE_FLAG = 2
        PREGNANT_FLAG = 4
        PARITY_FLAG = 8

    def __init__(self) -> None:
        
        self.estrus = Estrus()
        super().__init__()

    def set_pregnant(self, status: PregnantStatus):

        self.estrus.set_pregnant(status)

    def set_parity(self, parity: int):

        try:
            self.estrus.set_parity(parity)
        except ValueError:
            self._turn_on_flag(self.Flags.PARITY_FLAG.value)
            self.error_messages.append("批次應該要介於0~12之間")


class MatingFactory(Factory):

    class Flags(Enum):

        ESTRUS_FLAG = 1
        MATING_DATE_FLAG = 2
        BOAR_FLAG = 4

    def __init__(self):
        
        super().__init__()
        self.mating: Mating = Mating()
        

    def set_estrus(self, estrus: Estrus):

        self.mating.set_estrus(estrus)

    def set_mating_datetime(self, datetime_):

        self.mating.set_mating_datetime(datetime_)


class FarrowingFactory(Factory):

    class Flags(Enum):

        ESTRUS_FLAG = 1
        FARROWING_DATE_FLAG = 2
        CRUSHING_FLAG = 4
        BLACK_FLAG = 8
        WEAK_FLAG = 16
        MALFORMATION_FLAG = 32
        DEAD_FLAG = 64
        N_OF_MALE_FLAG = 128
        N_OF_FEMALE_FLAG = 256
        TOTAL_WEIGHT_FLAG = 512

    def __init__(self, farm: str, ceil: int = 20):

        if not isinstance(farm, str):
            raise TypeError("farm should be a string. Get {type_}".format(str(type(farm))))

        if not isinstance(ceil, int):
            raise TypeError("ceil should be a string. Get {type_}".format(str(type(ceil))))

        super().__init__()
        self.farrowing = Farrowing()

        # The farm attribute can be used in some basic query such as set_estrus, 
        # so children classes do not need to implement their own method.
        self.farm = farm
        
        # The ceil attribute is the possible maximum number of piglet born/dead in 
        # a batch.
        self.ceil = ceil

    def __check_numeric(self, attribute: str, n: int, flag: int) -> int:
        '''
        Check 0 < n < ceil. If n out of range, ask the user how to deal with. 
        If the user agree with the change, return the corrected value. Else, 
        turn on the flag and return None.
        Steps:
        1. Check n < ceil
        2. Chekc n > 0
        '''

        if n > self.ceil:
            if ask("{attribute}數量過多（{n}），請確認是否正確".format(attribute=attribute, n=str(n))):
                return n
            else:
                self.error_messages.append("{attribute}數量不正常".format(attribute=attribute))
                self._turn_on_flag(flag)
                return None
        if n < 0:
            if ask("{attribute}數量不能為負值（{n}），是否修正為正？".format(attribute=attribute, n=str(n))):
                return -n
            else:
                self.error_messages.append("{attribute}數量不正常".format(attribute=attribute))
                self._turn_on_flag(flag)
                return None
        return n

    def set_estrus(self, id: str, farrowing_date) -> None:
        '''
        This method will find the nearest estrus record in the database base on 
        sow id, farrowing date and farm. If no such record or the time delta is
        larger than 250 days, then the estrus flag will turn on.
        * param id: a sow id
        * param farrowing_date: any ISO format
        * Raise TypeError, ValueError
        '''

        if not isinstance(id, str):
            raise TypeError("id should be a string. Get {type_}".format(type_=str(type(id))))
        farrowing_date = transform_date(farrowing_date)
        
        estrus = EstrusModel().find_multiple(
            equal={"id": PigFactory().remove_dash_from_id(id), "farm": self.farm},
            smaller_equal={"estrus_datetime": farrowing_date},
            larger_equal={"estrus_datetime": (farrowing_date - timedelta(250))},
            order_by="estrus_datetime DESC"
        )

        if len(estrus) == 0:
            self.error_messages.append("找不到先前的發情/配種紀錄")
            self._turn_on_flag(self.Flags.ESTRUS_FLAG.value)
            return None
        
        self.farrowing.set_estrus(estrus[0])

    def set_farrowing_date(self, date) -> None:
        ''' * Raise TypeError, ValueError'''

        self.farrowing.set_farrowing_date(date)

    def set_crushing(self, n: int) -> None:

        n = self.__check_numeric("壓死", n, self.Flags.CRUSHING_FLAG.value)
        if n is not None:
            self.farrowing.set_crushing(n)

    def set_black(self, n: int) -> None:

        n = self.__check_numeric("黑胎", n, self.Flags.BLACK_FLAG.value)
        if n is not None:
            self.farrowing.set_black(n)

    def set_weak(self, n: int) -> None:

        n = self.__check_numeric("虛弱死", n, self.Flags.WEAK_FLAG.value)
        if n is not None:
            self.farrowing.set_weak(n)

    def set_malformation(self, n: int) -> None:

        n = self.__check_numeric("畸形", n, self.Flags.MALFORMATION_FLAG.value)
        if n is not None:
            self.farrowing.set_malformation(n)

    def set_dead(self, n: int) -> None:

        n = self.__check_numeric("死胎", n, self.Flags.DEAD_FLAG.value)
        if n is not None:
            self.farrowing.set_dead(n)

    def set_n_of_male(self, n: int) -> None:

        n = self.__check_numeric("公小豬", n, self.Flags.N_OF_MALE_FLAG.value)
        if n is not None:
            self.farrowing.set_n_of_male(n)

    def set_n_of_female(self, n: int) -> None:

        n = self.__check_numeric("母小豬", n, self.Flags.N_OF_FEMALE_FLAG.value)
        if n is not None:
            self.farrowing.set_n_of_female(n)

    def set_total_weight(self, weight: int) -> None:

        self.farrowing.set_total_weight(weight)

    def set_note(self, note: str) -> None:

        self.farrowing.set_note(note)