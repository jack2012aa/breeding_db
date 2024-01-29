from datetime import datetime

from data_structures.pig import Pig
from factory import PigFactory
from factory import ParentError
from factory import EstrusFactory
from factory import MatingFactory
from factory import FarrowingFactory
from general import ask
from general import ask_multiple
from general import transform_date
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


        If the parent does not exist, two cases possible: 
        1. the parent is in the rest of the file; 
        2. the parent does not exist.


        To handle case 1, the method will raise a special exception `ParentError` 
        so the csv_reader can record these pigs and re-generate them after others are done.


        The birthday and gender of parent will be checked. So the birthday of the pig can not be None.


        * param dam: `True` if setting dam, `False` if setting sire
        * param parent_id: breed + id + *
        * param in_farm: `True` if the parent belongs to Dong-Ying
        * param nearest: `True` to auto-select the pig with the nearest birthday as the parent.
        * Raise ValueError and ParentError
        '''

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
            raise ParentError("親代不在資料庫中")

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
                    raise ParentError("親代不在資料庫中")
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
                self._turn_on_flag(self.DAM_FLAG)
                raise error
        else:
            try:
                self.pig.set_sire(parent)
                return None
            # Error should not happen here since parent comes from the database.
            except (TypeError, ValueError) as error:
                self.error_messages.append(str(error))
                self._turn_on_flag(self.SIRE_FLAG)
                raise error

    def set_reg_id(self, reg: str):
        '''reg id is a six-digit unique id.'''

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

    def set_sow(self, id: str, estrus_date: str):
        '''
        Search the youngest sow which has correct id and farm and born before the estrus date.\\
        Some id in the excel which Dong-Ying provides contain breed information, 
        while some do not. So the breed will not be in the sql query.
        * param id: an id in the form *1234-56*
        * param estrus_date: an ISO formate date string
        * Raise TypeError
        '''

        if not isinstance(id, str):
            raise TypeError("id should be a string. Get {type_}".format(type_=str(type(id))))
        if not isinstance(estrus_date, str):
            raise TypeError("estrus_date should be a string. Get {type_}"
                            .format(type_=str(type(estrus_date))))
        
        # Transform id and estrus_date
        id = PigFactory().standardize_id(id)
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
            equal={"id": id, "farm": "Dong-Ying", "gender": "F"},
            smaller={"birthday": str(date)},
            order_by="birthday DESC"
        )
        if len(pigs) == 0:
            self._turn_on_flag(self.Flags.SOW_FLAG.value)
            self.error_messages.append("{id}母豬資料不在資料庫中".format(id=id))
            return
        # Set the sow
        else:
            self.estrus.set_sow(pigs[0])

    def set_estrus_datetime(self, date: str, time: str):
        '''
        * param date: format should be yyyy-mm-dd
        * param time: format should be HH:MM:SS
        '''

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
    
    def set_boar(self, id: str, mating_date: str):
        '''
        Search the youngest boar which has correct id and farm and born before the mating date.\\
        Some id in the excel which Dong-Ying provides contain breed information, 
        while some do not. So the breed will not be in the sql query.
        * param id: an id in the form *1234-56*
        * param mating_date: an ISO formate date string
        * Raise TypeError
        '''


        if not isinstance(id, str):
            raise TypeError("id should be a string. Get {type_}".format(type_=str(type(id))))
        if not isinstance(mating_date, str):
            raise TypeError("mating_date should be a string. Get {type_}"
                            .format(type_=str(type(mating_date))))
        
        # Transform id and estrus_date
        id = PigFactory().standardize_id(id)
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
            equal={"id": id, "farm": "Dong-Ying", "gender": "M"},
            smaller={"birthday": str(date)},
            order_by="birthday DESC"
        )
        if len(pigs) == 0:
            self._turn_on_flag(self.Flags.BOAR_FLAG.value)
            self.error_messages.append("{id}公豬資料不在資料庫中".format(id=id))
            return
        # Set the sow
        else:
            self.mating.set_boar(pigs[0])


class DongYingFarrowingFactory(FarrowingFactory):

    def __init__(self):
        super().__init__("Dong-Ying")