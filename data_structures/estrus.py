from datetime import datetime
from enum import Enum

from data_structures.pig import Pig

class Pregnant_status(Enum):
    YES = 1
    NO = 2
    UNKNOWN = 3

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
        self.__pregnant: Pregnant_status = None
        self.__parity: int = None

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

        if not (isinstance(date_time, str) or isinstance(date_time, datetime)):
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

    def set_pregnant(self, status: Pregnant_status):
        '''
        * param status: whether the sow got pregnant after this estrus.
        * Raise TypeError
        '''
        
        if not isinstance(status, Pregnant_status):
            raise TypeError("status should be a Pregnan_status. Get {type_}".format(type_=str(type(status))))
        
        self.__pregnant = status

    def set_parity(self, parity: int):
        '''
        * param parity: a non-negative int indicates how many time did the sow being pregnant.
          The value should between 0 to 10.
        * Raise TypeError, ValueError
        '''

        if not isinstance(parity, int):
            raise TypeError("parity should be an int. Get {type_}".format(type_=str(type(parity))))

        # I guess no sow can give birth more than 10 times.        
        if parity < 0 or parity > 10:
            raise ValueError("parity should between 0 to 10. Get {parity}".format(parity=parity))
        
        self.__parity = parity

    def get_sow(self):
        return self.__sow
    
    def get_estrus_datetime(self):
        return self.__estrus_datetime
    
    def get_pregnant(self):
        return self.__pregnant
    
    def get_parity(self):
        return self.__parity