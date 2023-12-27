from tools.general import ask
from models.pig import PigModel
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
        '''

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

        # Find the index of the first and second character in id
        first = 0
        second = len(id)
        for i in range(len(id)):
            if not id[i].isnumeric():
                if first == 0:
                    first = i + 1
                elif second == len(id):
                    second = i
                    break
        return id[first:second]

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
            self.error_messages.append("品種型別 {type_} 錯誤".format(type_=type(breed)))
            raise TypeError("品種型別 {type_} 錯誤".format(type_=type(breed)))
        
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
    
    def set_parent(self, parent: str, parent_id: str) -> None:  
        '''
        * param parent: ['dam','sire']
        * param parent_id: breed + id + *
        * The parent should exist in the database. The query is based on breed and id.
        * If more than one result exist, they will be shown for user to select the correct one.
        * If the parent does not exist, two cases possible: 1. the parent is in the rest of the file; 2. the parent does not exist.
        * To handle case 1, the method will raise a special exception `ParentError` so the csv_reader can record these pigs and re-generate them after others are done.
        * The birthday of parent is checked to make sure it was borned before its child.
        * Raise ValueError, KeyError and ParentError
        '''

        if parent not in ["dam", "sire"]:
            raise ValueError(
                "The argument parent should be either dam or sire. {parent} is recieved"
                .format(parent=parent)
            )

        # Take the first letter as breed
        breed = ''
        id = ''
        for c in parent_id:
            if c.encode().isalpha():
                breed = c.upper()
                id = parent_id.split(c)[1]
                break
        if breed not in Pig.BREED and not breed == "":
            if parent == "dam":
                self._turn_on_flag(self.DAM_FLAG)
                self.error_messages.append("母畜品種不在常見名單內")
            else:
                self._turn_on_flag(self.SIRE_FLAG)
                self.error_messages.append("父畜品種不在常見名單內")
            return None
        
        id = self.remove_dash_from_id(id)

        # Find the parent in db
        # -------------------------------------------- NOT DONE ----------------------------------------------
        parent_pig = Pig()
        parent_pig.set_id("123456")
        parent_pig.set_birthday("2020-02-03")
        
        
        # Check birthday
        if parent_pig.get_birthday() > self.pig.get_birthday():
            if parent == "dam":
                self._turn_on_flag(self.DAM_FLAG)
                self.error_messages.append("母畜生日比後代生日晚")
            else:
                self._turn_on_flag(self.SIRE_FLAG)
                self.error_messages.append("父畜生日比後代生日晚")
            return None

        # Set parent
        if parent == "dam":
            try:
                self.pig.set_dam(parent_pig.get_id(), parent_pig.get_birthday())
                return None
            # Error should not happen here since parent_pig comes from the database.
            except (TypeError, ValueError) as error:  
                self.error_messages.append(str(error))
                self._turn_on_flag(self.DAM_FLAG)
                raise error
        else:
            try:
                self.pig.set_sire(parent_pig.get_id(), parent_pig.get_birthday())
                return None
            # Error should not happen here since parent_pig comes from the database.
            except (TypeError, ValueError) as error:  
                self.error_messages.append(str(error))
                self._turn_on_flag(self.SIRE_FLAG)
                raise error
        
    def set_naif_id(self, naif: str):
        '''
        naif id is a six-digit unique id.
        '''
        if naif == '' or naif == '無登':
            return
        
        naif = str(naif)
        
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
