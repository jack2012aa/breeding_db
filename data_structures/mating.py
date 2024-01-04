from datetime import datetime

from data_structures.pig import Pig
from data_structures.estrus import Estrus

class Mating:
    '''
    A class recording an mating after an estrus.

    ### Variables:
    * estrus: an unique Estrus object.
    * mating_datetime: when did the mating done.
    * boar: an unique Pig object.
    '''

    def __init__(self) -> None:

        self.__estrus: Estrus = None
        self.__mating_datetime: datetime = None
        self.__boar: Pig = None

    def __str__(self) -> str:
        
        if self.__estrus is not None:
            s = "\n".join([
                "母豬耳號 sow_id：{id}".format(id=str(self.__estrus.get_sow().get_id())),
                "母豬生日 sow_birthday：{birthday}".format(birthday=str(self.__estrus.get_sow().get_birthday())), 
                "母豬所屬牧場 sow_farm：{farm}".format(farm=str(self.__estrus.get_sow().get_farm())),
                "發情日期 sow_estrus_datetime：{date_}".format(date_=str(self.__estrus.get_estrus_datetime())),
            ])
        else:
            s = "\n".join([
                "母豬耳號 sow_id：None",
                "母豬生日 sow_birthday：None", 
                "母豬所屬牧場 sow_farm：None", 
                "發情日期 sow_estrus_datetime：None"
            ])
        if self.__boar is not None:
            s = "\n".join([
                s,
                "配種日期 mating_datetime：{datetime_}".format(datetime_=str(self.__mating_datetime)),
                "公豬耳號 boar_id：{id}".format(id=str(self.__boar.get_id())),
                "公豬生日 boar_birthday：{birthday}".format(birthday=str(self.__boar.get_birthday())),
                "公豬所屬牧場 boar_farm：{farm}".format(farm=str(self.__boar.get_farm()))
            ])
        else:
            s = "\n".join([
                s,
                "配種日期 mating_datetime：{datetime_}".format(datetime_=str(self.__mating_datetime)),
                "公豬耳號 boar_id：None",
                "公豬生日 boar_birthday：None",
                "公豬所屬牧場 boar_farm：None"
            ])

    def __eq__(self, __value: object) -> bool:
        
        if __value == None:
            return False

        if not isinstance(__value, Mating):
            raise TypeError("Can not compare Mating with {type_}".format(type_=str(type(__value))))
        
        # Deal with the case that self.__boar is None
        result = True
        if (self.__boar is None) ^ (__value.get_boar() is None):
            return False
        elif (self.__boar is not None) and (__value.get_boar() is not None):
            # I do not care other attributes of the boar.
            result = self.__boar.is_identical(__value.get_boar())

        return \
            (self.__estrus == __value.get_estrus()) \
            and (self.__mating_datetime == __value.get_mating_datetime()) \
            and result
    
    def is_unique(self) -> bool:

        return (self.__estrus is not None) and (self.__mating_datetime is not None)
    
    def set_estrus(self, estrus: Estrus):
        '''
        * param estrus: an unique Estrus object.
        * Raise TypeError, ValueError
        '''

        if not isinstance(estrus, Estrus):
            raise TypeError("estrus should be an Estrus. Get {type_}".format(type_=str(type(estrus))))
        
        if not estrus.is_unique():
            raise ValueError("estrus should be unique.\n{estrus}".format(estrus=str(estrus)))
        
        self.__estrus = estrus

    def set_mating_datetime(self, date_time):
        '''
        * param date_time: a string in format '%Y-%m-%d %H:%M:%S', 
          '%Y-%m-%d' or a datetime object.
        * Raise TypeError, ValueError
        '''

        if not (isinstance(date_time, (str, datetime))):
            raise TypeError("date_time should be a string or datetime. Get {type_}"
                            .format(type_=str(type(date_time))))

        if isinstance(date_time, str):
            try:
                date_time = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
            except ValueError as error:
                try:
                    date_time = datetime.strptime(date_time, "%Y-%m-%d")
                except ValueError as error:
                    raise error

        self.__mating_datetime = date_time

    def set_boar(self, boar: Pig):
        '''
        * param boar: an unique Pig object.
        * Raise TypeError, ValueError
        '''

        if not isinstance(boar, Pig):
            raise TypeError("boar should be a Pig. Get {type_}".format(type_=str(type(boar))))
        
        if not boar.is_unique():
            raise ValueError("boar should be unique.\n{boar}".format(boar=str(boar)))
        
        self.__boar = boar

    def get_estrus(self) -> Estrus:

        return self.__estrus
    
    def get_mating_datetime(self) -> datetime:

        return self.__mating_datetime
    
    def get_boar(self) -> Pig:

        return self.__boar