from tools.general import ask
from tools.general import ask_multiple
from models.pig_model import PigModel
from data_structures.pig import Pig

class ParentError(BaseException):

    def __init__(self, message):
        super().__init__(message)

class PigFactory:

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
        self.__review_flag: int = 0
        self.error_messages: list = []

    def _turn_on_flag(self, flag: int):
        self.__review_flag = self.__review_flag | flag

    def _turn_off_flag(self, flag: int):
        self.__review_flag = self.__review_flag & ~flag
    
    def check_flag(self, flag: int):
        return self.__review_flag & flag != 0

    def get_flag(self):
        return self.__review_flag

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
        

class DongYingFactory(PigFactory):
    
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
            self._turn_on_flag(self.BREED_FLAG)
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

        n_id = self.remove_dash_from_id(id)
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
                self._turn_on_flag(self.DAM_FLAG)
                self.error_messages.append("母畜品種不在常見名單內")
            else:
                self._turn_on_flag(self.SIRE_FLAG)
                self.error_messages.append("父畜品種不在常見名單內")
            return None
        
        id = self.remove_dash_from_id(id)

        # Find the parent in the database.
        if dam:
            gender = 'F'
        else:
            gender = 'M'
        equal = {"id": id, "gender": gender}
        smaller = {"birthday": str(self.pig.get_birthday())}
        if breed != "":
            equal["breed"] = breed
        if in_farm:
            equal["farm"] = "Dong-Ying"

        model = PigModel()
        found_pigs = model.find_pigs(equal=equal, smaller=smaller)

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
        
    def set_naif_id(self, naif: str):
        '''naif id is a six-digit unique id.'''

        if not isinstance(naif, str):
            raise TypeError("naif should be a string. Get {type_}".format(type_=str(type(naif))))
        
        if naif == '' or naif == '無登':
            return
        
        if not naif.isnumeric():
            n_naif = self.remove_nonnumeric(naif)
            if not ask("是否可以將登錄號從 " + naif + " 修改為 " + n_naif + "？"):
                self._turn_on_flag(self.NAIF_FLAG)
                self.error_messages.append('登錄號有非數字字元')
                return
            naif = n_naif

        try:
            self.pig.set_naif_id(naif)
            return
        except BaseException as ex:
            self._turn_on_flag(self.NAIF_FLAG)
            self.error_messages.append(str(ex))
            return

    def set_farm(self, farm: str = "Dong-Ying"):
        '''Default set Dong-Ying'''

        return super().set_farm(farm)