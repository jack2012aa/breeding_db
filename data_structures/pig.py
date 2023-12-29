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

        self.__breed: str = None
        '''Breed: {'L', 'Y', 'D'}'''

        self.__id: str = None
        '''aka "Ear tag" in some cases. 0 < Length < MAX_ID_LENGTH'''

        self.__birthday: datetime.date = None
        '''Birthday'''

        self.__sire: Pig = None

        self.__dam: Pig = None

        self.__naif_id: str = None
        '''ID that is documented in naif's system. Necessary to be turned into int.'''

        self.__gender: str = None
        '''{'M','F'}'''

        self.__chinese_name: str = None

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

    def set_dam(self, parent):
        '''
        * param parent: a pig with id, birthday and farm.
        * Raise TypeError and ValueError
        '''

        if not isinstance(parent, Pig):
            raise TypeError("parent 應該是 Pig，現在輸入的是 {type_} ".format(type_=str(type(parent))))
        if parent.get_id() is None or parent.get_birthday() is None or parent.get_farm() is None:
            raise ValueError("parent 應該要有id，出生日期與所屬牧場")
        self.__dam = parent
        return None

    def set_sire(self, parent):
        '''
        * param parent: a pig with id, birthday and farm.
        * Raise TypeError and ValueError
        '''

        if not isinstance(parent, Pig):
            raise TypeError("parent 應該是 Pig，現在輸入的是 {type_} ".format(type_=str(type(parent))))
        if parent.get_id() is None or parent.get_birthday() is None or parent.get_farm() is None:
            raise ValueError("parent 應該要有id，出生日期與所屬牧場")
        self.__sire = parent
        return None

    def set_naif_id(self, id):
        '''
        * param id: a six-digit unique id
        * Raise TypeError, ValueError
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

    def set_chinese_name(self, name: str):
        '''* Raise TypeError'''
        if not isinstance(name, str):
            raise TypeError("Chinese name should be a string. Get {type_}".format(str(type(name))))
        self.__chinese_name = name

    def set_farm(self, farm: str):
        '''* Raise TypeError'''
        if not isinstance(farm, str):
            raise TypeError("farm should be a string. Get {type_}".format(str((type(farm)))))
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
    
    def get_naif_id(self):
        return self.__naif_id
    
    def get_gender(self):
        return self.__gender
    
    def get_chinese_name(self):
        return self.__chinese_name
    
    def get_farm(self):
        return self.__farm
    
    def is_unique(self):
        ''' Whether this pig has id, birthday and farm.'''
        return self.__id is not None and self.__birthday is not None and self.__farm is not None