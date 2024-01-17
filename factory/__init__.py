from enum import Enum

from data_structures.pig import Pig
from data_structures.estrus import Estrus
from data_structures.estrus import PregnantStatus
from data_structures.mating import Mating
from general import ask


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

    # Mask
    BREED_FLAG = 1
    ID_FLAG = 2
    BIRTHDAY_FLAG = 4
    SIRE_FLAG = 8
    DAM_FLAG = 16
    NAIF_FLAG = 32
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
        if '-' in id:
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
            self._turn_on_flag(self.GENDER_FLAG)
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
            self._turn_on_flag(self.BIRTHDAY_FLAG)
            return
        except TypeError as error:
            self.error_messages.append(str(error))
            self._turn_on_flag(self.BIRTHDAY_FLAG)
            raise error

    def set_naif_id(self, naif: str) -> None:
        '''* Raise `TypeError`'''

        if naif in [
            "",
            "無登",
            ]:
            return None

        try:
            self.pig.set_naif_id(naif)
        except TypeError as error:
            self._turn_on_flag(self.NAIF_FLAG)
            self.error_messages.append(str(error))
            raise error
        except ValueError as error:
            if not naif.isnumeric():
                n_naif = self.remove_nonnumeric(naif)
                if ask("是否可以將登錄號從 {naif} 修改為 {n_naif} ？".format(naif=naif,n_naif=n_naif)):
                    self.pig.set_naif_id(n_naif)
                    return None
            self._turn_on_flag(self.NAIF_FLAG)
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
            self._turn_on_flag(self.PARITY_FLAG)
            self.error_messages.append("批次應該要介於0~12之間")


class MatingFactory(Factory):

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