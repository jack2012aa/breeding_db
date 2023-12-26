import datetime

from tools.general import transform_date

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

        if not isinstance(breed, str):
            raise TypeError("品種應該是 string，現在輸入的是 {type_} ".format(type_=str(type(breed))))

        if breed in Pig.BREED:
            self.__breed = breed
        elif breed in Pig.BREED_DICT:
            self.__breed = Pig.BREED_DICT[breed]
        else:
            raise ValueError("品種 {breed} 不在列表中，請參考下表： {list_} ".format(breed=breed, list_=str(Pig.BREED)))
    
    def set_id(self, id: str):
        '''* Raise TypeError and ValueError'''
        
        if not isinstance(id, str):
            raise TypeError("耳號應該是 string，現在輸入的是 {type_} ".format(type_=str(type(id))))

        if not self.__is_valid_id(id):
            raise ValueError("耳號長度異常，應介於 0 ~ {max_} 之間。輸入長度為 {length}".format(max_=Pig.MAX_ID_LENGTH, length=len(id)))
        else:
            self.__id = id

    def set_birthday(self, date):
        '''
        * param date: any ISO format
        * Raise TypeError and ValueError
        '''

        try:
            self.__birthday = transform_date(date)
        except (TypeError, ValueError) as error:
            raise error

    def set_dam(self, id: str, date):
        '''
        *param date: any ISO format
        *Raise TypeError and ValueError
        '''

        if not isinstance(id, str):
            raise TypeError("耳號應該是 string，現在輸入的是 {type_} ".format(type_=str(type(id))))
        if not self.__is_valid_id(id):
            raise ValueError("耳號長度異常，應介於 0 ~ {max_} 之間。輸入長度為 {length}".format(max_=Pig.MAX_ID_LENGTH, length=len(id)))
        self.__dam['id'] = id

        try:
            self.__dam['birthday'] = transform_date(date)
        except (TypeError, ValueError) as error:
            raise error

    def set_sire(self, id: str, date):
        '''
        *param date: any ISO format
        *Raise TypeError and ValueError
        '''

        if not isinstance(id, str):
            raise TypeError("耳號應該是 string，現在輸入的是 {type_} ".format(type_=str(type(id))))
        if not self.__is_valid_id(id):
            raise ValueError("耳號長度異常，應介於 0 ~ {max_} 之間。輸入長度為 {length}".format(max_=Pig.MAX_ID_LENGTH, length=len(id)))
        self.__sire['id'] = id

        try:
            self.__sire['birthday'] = transform_date(date)
        except (TypeError, ValueError) as error:
            raise error

    def set_naif_id(self, id):
        '''
        * param id: a six-digit unique id
        * Raise TypeError
        '''

        if not isinstance(id, str):
            raise TypeError("id 應該是 string，現在輸入的是 {type_} ".format(type_=str(type(id))))
        
        try:
            int(id)
        except:
            raise ValueError("登錄號不能含有非數字字元 {id}".format(id=id))

        if str(int(id)) != str(id):
            raise ValueError("登錄號不能含有非數字字元 {id}".format(id=id))
        
        if len(str(id)) != 6:
            raise ValueError("{id} 不是六位數字".format(id=id))
        
        self.__naif_id = id
        
    def set_gender(self, gender: str):
        ''' * Raise KeyError'''

        if gender not in Pig.GENDER:
            raise KeyError("性別 {gender} 錯誤。性別需定義於下表：\n{dict_}".format(gender=gender, dict_=Pig.GENDER))
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
    
    def get_sire(self):
        return self.__sire
    
    def get_naif_id(self):
        return self.__naif_id
    
    def get_gender(self):
        return self.__gender
    
    def get_chinese_name(self):
        return self.__chinese_name