import datetime

class PigSettingException(BaseException):

    def __init__(self, message:str):
        super().__init__(message)

class Pig:

    BREED = (
        'L',
        'Y',
        'D'
    )
    '''All posible breeds.'''

    BREED_DICT = {
        "藍瑞斯":'L',
        "約克夏":'Y',
        "杜洛克":'D'
    }

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

        self.__breed: str = ''
        '''Breed: {'L', 'Y', 'D'}'''

        self.__id: str = ''
        '''aka "Ear tag" in some cases. 0 < Length < MAX_ID_LENGTH'''

        self.__birthday: datetime.date = datetime.datetime.today().date()
        '''Birthday'''

        self.__sire = {'id':'','birthday':''}
        '''Sire's key value.'''

        self.__dam = {'id':'','birthday':''}
        '''Dam's key value'''

        self.__naif_id: str = ''
        '''ID that is documented in naif's system. Necessary to be turned into int.'''

        self.__gender: chr = ''
        '''{'M','F'}'''

        self.__chinese_name: str = ''

    def __str__(self):
        s = {'ID':self.__id,
             'breed': self.__breed,
             'gender': self.__gender,
             'dam': self.__dam,
             'sire': self.__sire,
             'birthday': self.__birthday}
        return str(s)


    def __is_valid_id(self, id:str):
        return len(id) > 0 and len(id) < Pig.MAX_ID_LENGTH

    def set_breed(self, breed: str):

        if breed in Pig.BREED:
            self.__breed = breed
        else:
            raise PigSettingException("錯誤的品種值。品種必須定義於下表\n" + str(Pig.BREED) +"\n輸入為" + str(breed))
    
    def set_id(self, id: str):
        
        if id == None:
            raise PigSettingException("耳號不能為空值")
        elif not self.__is_valid_id(id):
            raise PigSettingException("耳號長度過長。須小於 " + str(Pig.MAX_ID_LENGTH) + " 但卻輸入 " + str(len(id)))
        else:
            self.__id = id

    def set_birthday(self, date):
        '''Any ISO format.'''

        if date == None:
            raise PigSettingException("生日不能為空值")

        if (type(date) == str):

            try:
                self.__birthday = datetime.date.fromisoformat(date)
            except:
                raise PigSettingException("生日日期並非使用 ISO format")
        
        elif (type(date) == datetime.date):
            self.__birthday = date

        else:
            raise PigSettingException("生日型別錯誤")

    def set_dam(self, id: str, date):

        if not self.__is_valid_id(id):
            raise PigSettingException("母畜耳號長度過長。須小於 " + str(Pig.MAX_ID_LENGTH) + " 但卻輸入 " + str(len(id)) + " but setting " + str(len(id)))
        
        if id == None or date == None:
            raise PigSettingException("母畜生日型別錯誤")

        self.__dam['id'] = id
        if (type(date) == str):

            try:
                self.__birthday = datetime.date.fromisoformat(date)
            except:
                raise PigSettingException("母畜生日日期並非使用 ISO format")
            
        elif type(date) == datetime.date:
            self.__dam['birthday'] = date
        else:
            raise PigSettingException("母畜生日型別錯誤")


    def set_sire(self, id: str, date):

        if not self.__is_valid_id(id):
            raise PigSettingException("父畜耳號長度過長。須小於 " + str(Pig.MAX_ID_LENGTH) + " 但卻輸入 " + str(len(id)) + " but setting " + str(len(id)))
        
        if id == None or date == None:
            raise PigSettingException("父畜生日型別錯誤")

        self.__sire['id'] = id
        if (type(date) == str):

            try:
                self.__birthday = datetime.date.fromisoformat(date)
            except:
                raise PigSettingException("父畜生日日期並非使用 ISO format")
        elif type(date) == datetime.date:
            self.__sire['birthday'] = date
        else:
            raise PigSettingException("父畜生日型別錯誤")

    def set_naif_id(self, id: str):
        '''
        naif id is a six-digit unique id.
        '''

        if id == '' or id == None:
            raise PigSettingException("登錄號型別錯誤")
        
        try:
            int(id)
        except:
            raise PigSettingException("登錄號不能含有非數字字元 " + str(id) + ".")
        if str(int(id)) != str(id):
            raise PigSettingException("登錄號不能含有非數字字元 " + str(id) + ".")
        if len(str(id)) != 6:
            raise PigSettingException("登錄號須為六位數字，此登錄號位數為： " + str(len(id)) + ".")
        self.__naif_id = str(id)
        
    def set_gender(self, gender: str):

        if gender not in Pig.GENDER:
            raise PigSettingException("性別錯誤。性別需定義於下表：\n" + str(Pig.GENDER))
        else:
            self.__gender = Pig.GENDER[gender]

    def set_chinese_name(self, name):
        self.__chinese_name = name

    def get_breed(self):
        return self.__breed
    
    def get_id(self):
        return self.__id
    
    def get_birthday(self):
        return self.__birthday
    
    def get_dam(self):
        return self.__dam
    
    def get_boar(self):
        return self.__sire
    
    def get_naif_id(self):
        return self.__naif_id
    
    def get_gender(self):
        return self.__gender
    
    def get_chinese_name(self):
        return self.__chinese_name