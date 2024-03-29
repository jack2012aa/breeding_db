from datetime import datetime

from data_structures.estrus import Estrus
from data_structures.estrus import TestResult
from data_structures.pig import Pig
from factory import PigFactory
from factory import ParentError
from factory import EstrusFactory
from factory import MatingFactory
from factory import FarrowingFactory
from general import ask
from general import ask_multiple
from general import transform_date
from general import type_check
from models.pig_model import PigModel


class DongYingPigFactory(PigFactory):

    def __init__(self):
        super().__init__()

    def set_breed(self, breed: str):
        '''
        1. Does breed in {L, Y, D}?
        2. Is breed an English word?
        3. Is breed in BREED_DICT?
        * Raise TypeError
        '''

        if breed is None:
            return

        if not isinstance(breed, str):
            self._turn_on_flag(self.Flags.BREED_FLAG.value)
            raise TypeError("breed should be a string. Get {type_}".format(type_=type(breed)))

        if breed in Pig.BREED:
            self.pig.set_breed(breed)
            return

        # Chinese string is recognized as alpha in the isalpha method. 
        if breed.encode('UTF-8').isalpha():
            n_breed = self.get_breed_abbrevation(breed)
            if ask("是否可以將品種從 {breed} 修改為 {n_breed} ？".format(breed=breed,n_breed=n_breed)):
                self.pig.set_breed(n_breed)
                return

        if breed in Pig.BREED_DICT:
            n_breed = Pig.BREED_DICT[breed]
            if ask("是否可以將品種從 {breed} 修改為 {n_breed} ？".format(breed=breed,n_breed=n_breed)):
                self.pig.set_breed(n_breed)
                return

        self.error_messages.append('品種不在常見品種名單中，或有錯誤字元')
        self._turn_on_flag(self.ID_FLAG)

    def set_id(self, id: str):
        '''
        * Can be turn into an int -> valid
        * Contain a dash -> Remove the dash
        * Get the number between first two nonnumeric characters (if any)
        * Raise TypeError
        '''

        if id is None:
            return

        if not isinstance(id, str):
            self._turn_on_flag(self.ID_FLAG)
            self.error_messages.append('耳號格式 {type_} 錯誤'.format(type_=str(type(id))))
            raise TypeError('耳號格式 {type_} 錯誤'.format(type_=str(type(id))))

        n_id = self.standardize_id(id)
        if (n_id != id and ask("是否可以將耳號從 {id} 修改為 {n_id} ？".format(id=id, n_id=n_id))) or n_id == id:
            try:
                self.pig.set_id(n_id)
                return
            except ValueError as error:
                self.error_messages.append(str(error))
                self._turn_on_flag(self.ID_FLAG)
                return
            except TypeError as error: # TypeError should not happen here.
                self.error_messages.append(str(error))
                self._turn_on_flag(self.ID_FLAG)
                raise error

        self.error_messages.append('耳號格式錯誤')
        self._turn_on_flag(self.ID_FLAG)
        return

    def set_parent(self, dam: bool, parent_id: str, in_farm: bool, nearest: bool) -> None:
        '''
        Find the parent in the database using id and breed and assign the parent to iteself.


        Parents may be pigs in Dong-Ying or pigs imported from different nations.
        In other words, they have different `farm` attribute. 
        You can restrict the `farm` attribute by param `in_farm`.


        Dong-Ying reuses id (ear tag) every several years. 
        If more than one result exist, they will be shown for user to select the correct one.
        Or, you can automatically select the one whose birthday is the closest to the pig 
        by param `nearest`.\\
        When `nearest` is true, those pigs with None `birthday` attribute will be ignored.


        The birthday and gender of parent will be checked. So the birthday of the pig can not be None.


        * param dam: `True` if setting dam, `False` if setting sire
        * param parent_id: breed + id + *
        * param in_farm: `True` if the parent belongs to Dong-Ying
        * param nearest: `True` to auto-select the pig with the nearest birthday as the parent.
        * Raise ValueError
        '''

        if parent_id is None:
            return

        if not isinstance(dam, bool):
            raise TypeError("dam should be a bool. Get {type_}".format(type_=str(type(dam))))
        if not isinstance(in_farm, bool):
            raise TypeError("in_farm should be a bool. Get {type_}".format(type_=str(type(in_farm))))
        if not isinstance(nearest, bool):
            raise TypeError("dam should be a bool. Get {type_}".format(type_=str(type(nearest))))

        if self.pig.get_birthday() is None:
            self.error_messages.append("需要有子代的生日才能設定親代")
            return None

        # Take the first letter as breed
        breed = ""
        id = ""
        for c in parent_id:
            if c.encode().isalpha():
                breed = c.upper()
                id = parent_id.split(c)[1]
                break
        if breed not in Pig.BREED and not breed == "":
            if dam:
                self._turn_on_flag(self.Flags.DAM_FLAG.value)
                self.error_messages.append("母畜品種不在常見名單內")
            else:
                self._turn_on_flag(self.Flags.SIRE_FLAG.value)
                self.error_messages.append("父畜品種不在常見名單內")
            return None

        id = self.standardize_id(id)

        # Find the parent in the database.
        if dam:
            gender = "F"
        else:
            gender = "M"
        equal = {"id": id, "gender": gender}
        smaller = {"birthday": str(self.pig.get_birthday())}
        if breed != "":
            equal["breed"] = breed
        if in_farm:
            equal["farm"] = "Dong-Ying"

        model = PigModel()
        found_pigs = model.find_multiple(equal=equal, smaller=smaller)

        if len(found_pigs) == 0:
            if dam:
                self._turn_on_flag(self.Flags.DAM_FLAG.value)
            else:
                self._turn_on_flag(self.Flags.SIRE_FLAG.value)
            self.error_messages.append("親代不在資料庫中")
            return

        parent: Pig = None
        # More than one result
        if len(found_pigs) > 1:
            if nearest:
                parent = found_pigs[0]
                for pig in found_pigs:
                    if (
                        self.pig.get_birthday() - pig.get_birthday()
                        < self.pig.get_birthday() - parent.get_birthday()
                    ):
                        parent = pig
            else:
                choice = ask_multiple(
                    "請問下列何者為{id}的親代？".format(id=self.pig.get_id()),
                    found_pigs
                )
                if choice is None:
                    if dam:
                        self._turn_on_flag(self.Flags.DAM_FLAG.value)
                    else:
                        self._turn_on_flag(self.Flags.SIRE_FLAG.value)
                    self.error_messages.append("親代不在資料庫中")
                    return
                else:
                    parent = found_pigs[choice]
        else:
            parent = found_pigs[0]

        # Set parent
        if dam:
            try:
                self.pig.set_dam(parent)
                return None
            # Error should not happen here since parent comes from the database.
            except (TypeError, ValueError) as error:
                self.error_messages.append(str(error))
                self._turn_on_flag(self.Flags.DAM_FLAG.value)
                raise error
        else:
            try:
                self.pig.set_sire(parent)
                return None
            # Error should not happen here since parent comes from the database.
            except (TypeError, ValueError) as error:
                self.error_messages.append(str(error))
                self._turn_on_flag(self.Flags.SIRE_FLAG.value)
                raise error

    def set_reg_id(self, reg: str):
        '''reg id is a six-digit unique id.'''

        if reg is None:
            return

        if not isinstance(reg, str):
            raise TypeError("reg should be a string. Get {type_}".format(type_=str(type(reg))))

        if reg == '' or reg == '無登':
            return

        if not reg.isnumeric():
            n_reg = self.remove_nonnumeric(reg)
            if not ask("是否可以將登錄號從 " + reg + " 修改為 " + n_reg + "？"):
                self._turn_on_flag(self.Flags.REG_FLAG.value)
                self.error_messages.append('登錄號有非數字字元')
                return
            reg = n_reg

        try:
            self.pig.set_reg_id(reg)
            return
        except BaseException as ex:
            self._turn_on_flag(self.Flags.REG_FLAG.value)
            self.error_messages.append(str(ex))
            return

    def set_farm(self, farm: str = "Dong-Ying"):
        '''Default set Dong-Ying'''

        return super().set_farm(farm)
    

class DongYingEstrusFactory(EstrusFactory):

    def __init__(self) -> None:
        super().__init__()

    def set_sow(self, id: str, estrus_date: str, nearest: bool = False):
        '''
        Search sows which have correct id and farm and born before the estrus date.\\
        Some id in the excel which Dong-Ying provides contain breed information, 
        while some do not. So the breed will not be in the sql query.
        * param id: an id in the form *1234-56*
        * param estrus_date: an ISO formate date string
        * Raise TypeError
        '''

        if id is None or estrus_date is None:
            return

        type_check(id, "id", str)
        type_check(estrus_date, "estrus_date", str)
        type_check(nearest, "nearest", bool)
        
        # Transform id and estrus_date
        standardized_id = PigFactory().standardize_id(id)
        try:
            date = transform_date(estrus_date)
        except ValueError:
            self._turn_on_flag(self.Flags.SOW_FLAG.value)
            self._turn_on_flag(self.Flags.ESTRUS_DATE_FLAG.value)
            self.error_messages.append("配種日期應該符合 ISO 格式，例如2024-01-03")
            return

        # Find the youngest sow born before the estrus_date
        model = PigModel()
        pigs = model.find_multiple(
            equal={"id": standardized_id, "farm": "Dong-Ying", "gender": "F"},
            smaller={"birthday": str(date)},
            order_by="birthday DESC"
        )
        if len(pigs) == 0:
            self._turn_on_flag(self.Flags.SOW_FLAG.value)
            self.error_messages.append("{id}母豬資料不在資料庫中".format(id=standardized_id))
            return
        
        # Set the sow
        if len(pigs) > 1 and not nearest:
            choice = ask_multiple(
                message="找到多頭符合耳號{id}的母豬，請問選擇下列何者？".format(id=id),
                choices=pigs
            )
            if choice is None:
                self._turn_on_flag(self.Flags.SOW_FLAG.value)
                self.error_messages.append("{id}母豬資料不在資料庫中".format(id=standardized_id))
                return
            pig = pigs[choice]
        else:
            pig = pigs[0]

        self.estrus.set_sow(pig)

    def set_estrus_datetime(self, date: str, time: str):
        '''
        * param date: format should be yyyy-mm-dd
        * param time: format should be HH:MM:SS
        '''

        if date is None or time is None:
            return

        if not isinstance(date, str):
            raise TypeError("date should be a string. Get {type_}".format(type_=str(type(date))))
        if not isinstance(time, str):
            raise TypeError("time should be a string. Get {type_}".format(type_=str(type(time))))
        
        try:
            date_time = datetime.strptime(" ".join([date, time]), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            self._turn_on_flag(self.Flags.ESTRUS_DATE_FLAG.value)
            self.error_messages.append("配種日期或配種時間格式錯誤。請參考2023-01-01 13:00")
            return
        
        self.estrus.set_estrus_datetime(date_time)

    def set_21th_day_test(self, result: str):
        ''' Call Estrus.transform_test_result and set result.'''

        try:
            return super().set_21th_day_test(Estrus.transform_test_result(result))
        except ValueError:
            self._turn_on_flag(self.Flags._21TH_DAY_TEST_FLAG.value)
            self.error_messages.append("字串'{result}'並未在轉換表中被定義".format(result=result))

    def set_60th_day_test(self, result: str):
        ''' Call Estrus.transform_test_result and set result.'''

        try:
            return super().set_60th_day_test(Estrus.transform_test_result(result))
        except ValueError:
            self._turn_on_flag(self.Flags._60TH_DAY_TEST_FLAG.value)
            self.error_messages.append("字串'{result}'並未在轉換表中被定義".format(result=result))
    

class DongYingMatingFactory(MatingFactory):

    def __init__(self):
        super().__init__()

    def set_mating_datetime(self, date: str, time: str):
        '''
        * param date: format should be yyyy-mm-dd
        * param time: format should be HH:MM:SS
        * Raise TypeError and ValueError
        '''

        if not isinstance(date, str):
            raise TypeError("date should be a string. Get {type_}".format(type_=str(type(date))))
        if not isinstance(time, str):
            raise TypeError("time should be a string. Get {type_}".format(type_=str(type(time))))
        
        try:
            date_time = datetime.strptime(" ".join([date, time]), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            self._turn_on_flag(self.Flags.MATING_DATE_FLAG.value)
            self.error_messages.append("配種日期或配種時間格式錯誤。請參考2023-01-01 13:00")
            return
        
        self.mating.set_mating_datetime(date_time)
    
    def set_boar(self, id: str, mating_date: str, nearest: bool = False):
        '''
        Search the youngest boar which has correct id and farm and born before the mating date.\\
        Some id in the excel which Dong-Ying provides contain breed information, 
        while some do not. So the breed will not be in the sql query.
        * param id: an id in the form *1234-56*
        * param mating_date: an ISO formate date string
        * Raise TypeError
        '''

        if id is None or mating_date is None:
            return
        type_check(id, "id", str)
        type_check(mating_date, "mating_date", str)
        type_check(nearest, "nearest", bool)
        
        # Transform id and estrus_date
        standardized_id = PigFactory().standardize_id(id)
        try:
            date = transform_date(mating_date)
        except ValueError:
            self._turn_on_flag(self.Flags.BOAR_FLAG.value)
            self._turn_on_flag(self.Flags.MATING_DATE_FLAG.value)
            self.error_messages.append("配種日期應該符合 ISO 格式，例如2024-01-03")
            return

        # Find the youngest sow born before the estrus_date
        model = PigModel()
        pigs = model.find_multiple(
            equal={"id": standardized_id, "farm": "Dong-Ying", "gender": "M"},
            smaller={"birthday": str(date)},
            order_by="birthday DESC"
        )
        if len(pigs) == 0:
            self._turn_on_flag(self.Flags.BOAR_FLAG.value)
            self.error_messages.append("{id}公豬資料不在資料庫中".format(id=standardized_id))
            return
        
        # Set the boar
        if len(pigs) > 1 and not nearest:
            CHOICE = ask_multiple(
                message="找到多頭符合耳號{id}的公豬，請問選擇下列何者？".format(id=id),
                choices=pigs
            )
            if CHOICE is None:
                self._turn_on_flag(self.Flags.BOAR_FLAG.value)
                self.error_messages.append("{id}公豬資料不在資料庫中".format(id=standardized_id))
                return
            boar = pigs[CHOICE]
        else:
            boar = pigs[0]
        self.mating.set_boar(boar)


class DongYingFarrowingFactory(FarrowingFactory):

    def __init__(self):
        super().__init__("Dong-Ying")