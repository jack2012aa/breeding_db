from datetime import datetime
from enum import Enum

from data_structures.pig import Pig

class PregnantStatus(Enum):

    YES = "Yes"
    NO = "No"
    UNKNOWN = "Unknown"
    ABORTION = "Abortion"


class Estrus:
    '''
    A class recording an estrus of a sow.

    ### Variables:
    * sow: an unique Pig object.
    * estrus_datetime: when did the estrus be observed.
    * pregnant: whether the sow got pregnant after this estrus.
    * parity: a non-negative int indicates how many time did the sow being pregnant.
    '''

    def __init__(self):

        self.__sow: Pig = None
        self.__estrus_datetime: datetime.datetime = None
        self.__pregnant: PregnantStatus = None
        self.__parity: int = None

    def __str__(self):

        id = birthday = farm = status = str(None)
        if self.__sow is not None:
            id = str(self.__sow.get_id())
            birthday = str(self.__sow.get_birthday())
            farm = str(self.__sow.get_farm())
        if self.__pregnant is not None:
            status = self.__pregnant.value
        

        s = "母豬耳號 id：{id}\n".format(id=str(id)) \
            + "母豬生日 birthday：{birthday}\n".format(birthday=str(birthday)) \
            + "母豬所屬牧場 farm：{farm}\n".format(farm=str(farm)) \
            + "發情日期 estrus_datetime：{date_}\n".format(date_=str(self.__estrus_datetime)) \
            + "是否懷孕 pregnant：{status}\n".format(status=str(status)) \
            + "生產批次 parity：{parity}\n".format(parity=str(self.__parity))
        
        return s
    
    def __eq__(self, __value: object) -> bool:
        
        if __value == None:
            return False

        if not isinstance(__value, Estrus):
            raise TypeError("Can not compare Estrus to {type_}".format(type_=str(type(__value))))
        
        # Deal with the case that self.__sow is None.
        result = True
        if (self.__sow is None) ^ (__value.get_sow() is None):
            return False
        elif (self.__sow is not None) and (__value.get_sow() is not None):
            # I do not care other attributes of the sow.
            result = self.__sow.is_identical(__value.get_sow())
        
        return  result \
            and self.__estrus_datetime == __value.__estrus_datetime \
            and self.__pregnant == __value.get_pregnant() \
            and self.__parity == __value.get_parity()

    def is_unique(self) -> bool:

        return (self.__sow is not None) and (self.__estrus_datetime is not None)

    def set_sow(self, sow: Pig):
        '''
        * param sow: an unique Pig object.
        * Raise TypeError, ValueError'''

        if not isinstance(sow, Pig):
            raise TypeError("sow should be a Pig. Get {type_}".format(type_=str(type(sow))))
        
        if not sow.is_unique():
            raise ValueError("sow should be unique.\n{sow}".format(sow=str(sow)))
        
        self.__sow = sow

    def set_estrus_datetime(self, date_time):
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

        self.__estrus_datetime = date_time

    def set_pregnant(self, status: PregnantStatus):
        '''
        * param status: whether the sow got pregnant after this estrus.
        * Raise TypeError
        '''
        
        if not isinstance(status, PregnantStatus):
            raise TypeError("status should be a Pregnan_status. Get {type_}".format(type_=str(type(status))))
        
        self.__pregnant = status

    def set_parity(self, parity: int):
        '''
        * param parity: a non-negative int indicates how many time did the sow being pregnant.
          The value should between 0 to 12.
        * Raise TypeError, ValueError
        '''

        if not isinstance(parity, int):
            raise TypeError("parity should be an int. Get {type_}".format(type_=str(type(parity))))

        # I guess no sow can give birth more than 10 times.        
        if parity < 0 or parity > 12:
            raise ValueError("parity should between 0 to 12. Get {parity}".format(parity=parity))
        
        self.__parity = parity

    def get_sow(self) -> Pig:
        return self.__sow
    
    def get_estrus_datetime(self) -> datetime:
        return self.__estrus_datetime
    
    def get_pregnant(self) -> PregnantStatus:
        return self.__pregnant
    
    def get_parity(self) -> int:
        return self.__parity