import datetime

class PigSettingException(BaseException):

    def __init__(self, message:str):
        super().__init__(message)

class Pig:

    __breed: str = ''
    '''Breed: {'L', 'Y', 'D'}'''

    __id: str = ''
    '''aka "Ear tag" in some cases. 0 < Length < MAX_ID_LENGTH'''

    __birthday: datetime.date = datetime.datetime.today()
    '''Birthday'''

    __boar = {'id':'','birthday':''}
    '''Boar's key value.'''

    __dam = {'id':'','birthday':''}
    '''Dam's key value'''

    __naif_id: str = ''
    '''ID that is documented in naif's system. Necessary to be turned into int.'''

    __gender: chr = ''
    '''{'M','F'}'''

    BREED = (
        'L',
        'Y',
        'D'
    )
    '''All posible breeds.'''

    GENDER = {
        '公':'M',
        '母':'F',
        'M':'M',
        'F':'F',
        '1':'M',
        '2':'F'
    }
    '''All acceptable gender format.'''

    MAX_ID_LENGTH = 20

    def __init__(self):
        '''An empty entity.'''
        pass

    def __is_valid_id(self, id:str):
        return len(id) > 0 and len(id) < Pig.MAX_ID_LENGTH

    def set_breed(self, breed: str):

        if breed in Pig.BREED:
            self.__breed = breed
        else:
            raise PigSettingException("Invalid breed. Breed must in " + str(Pig.BREED) +", but setting " + str(breed))
    
    def set_id(self, id: str):
        
        if id == None:
            raise PigSettingException("None argument.")
        elif not self.__is_valid_id(id):
            raise PigSettingException("Invalid id length. Expect 0 < len < " + str(Pig.MAX_ID_LENGTH) + " but setting " + str(len(id)))
        else:
            self.__id = id

    def set_birthday(self, date):
        '''yyyy/mm/dd'''

        if (type(date) == str):

            if date == None:
                raise PigSettingException("None argument.")
            
            try:
                yyyy, mm, dd = date.split('/')
                self.__birthday = datetime.date(int(yyyy), int(mm), int(dd))
            except:
                raise PigSettingException("Invalid date format. Expect yyyy/mm/dd but receive " + str(date))
        
        elif (type(date) == datetime.date):
            if date == None:
                raise PigSettingException("None argument.")
            else:
                self.__birthday = date

        else:
            raise PigSettingException("Unknown type")

    def set_dam(self, id: str, date):

        if not self.__is_valid_id(id):
            raise PigSettingException("Invalid id length. Expect 0 < len < " + str(Pig.MAX_ID_LENGTH) + " but setting " + str(len(id)))
        
        if id == None or date == None:
            raise PigSettingException("None argument.")

        self.__dam['id'] = id
        if type(date) == str:
            try:
                yyyy, mm, dd = date.split('/')
                self.__dam['birthday'] = datetime.date(int(yyyy),int(mm),int(dd))
            except:
                raise PigSettingException("Invalid date format. Expect yyyy/mm/dd but receive " + str(date))
        elif type(date) == datetime.date:
            self.__dam['birthday'] = date
        else:
            raise PigSettingException("Unknown type")


    def set_boar(self, id: str, date):

        if not self.__is_valid_id(id):
            raise PigSettingException("Invalid id length. Expect 0 < len < " + str(Pig.MAX_ID_LENGTH) + " but setting " + str(len(id)))
        
        if id == None or date == None:
            raise PigSettingException("None argument.")

        self.__boar['id'] = id
        if type(date) == str:
            try:
                yyyy, mm, dd = date.split('/')
                self.__boar['birthday'] = datetime.date(int(yyyy),int(mm),int(dd))
            except:
                raise PigSettingException("Invalid date format. Expect yyyy/mm/dd but receive " + str(date))
        elif type(date) == datetime.date:
            self.__boar['birthday'] = date
        else:
            raise PigSettingException("Unknown type")

    def set_naif_id(self, id: str):

        if id == '' or id == None:
            raise PigSettingException("None argument.")
        
        try:
            int(id)
            if str(int(id)) != str(id):
                raise PigSettingException("Invalid naif id. ID should be an integer, but receive " + str(id) + ".")
            self.__naif_id = str(id)
        except:
            raise PigSettingException("Invalid naif id. ID should be an integer, but receive " + str(id) + ".")
        
    def set_gender(self, gender: str):

        if gender not in Pig.GENDER:
            raise PigSettingException("Invalid gender format. Gender should be in\n" + str(Pig.GENDER))
        else:
            self.__gender = Pig.GENDER[gender]

    def get_breed(self):
        return self.__breed
    
    def get_id(self):
        return self.__id
    
    def get_birthday(self):
        return self.__birthday
    
    def get_dam(self):
        return self.__dam
    
    def get_boar(self):
        return self.__boar
    
    def get_naif_id(self):
        return self.__naif_id
    
    def get_gender(self):
        return self.__gender