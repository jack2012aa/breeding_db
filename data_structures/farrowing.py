from datetime import date

from data_structures.estrus import Estrus
from general import add_with_None
from general import transform_date

class Farrowing():
    '''
    total_born = born_alive + born_dead
    born_dead = crushing + black + weak + malformation + dead
    born_alive = n_of_male + n_of_female
    '''

    def __init__(self) -> None:
        
        self.__estrus: Estrus = None
        self.__farrowing_date: date = None
        self.__crushing: int = None
        self.__black: int = None
        self.__weak: int = None
        self.__malformation: int = None
        self.__dead: int = None
        self.__total_weight: int = None
        self.__n_of_male: int = None
        self.__n_of_female: int = None
        self.__note: str = None

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
        s = "\n".join([
            s,
            "分娩日期 farrowing_date：{date}".format(date=str(self.__farrowing_date)),
            "壓死 crushing：{crushing}".format(crushing=str(self.__crushing)),
            "黑胎 black：{black}".format(black=str(self.__black)),
            "體弱 weak：{weak}".format(weak=str(self.__weak)),
            "畸形 malformation:{malformation}".format(malformation=str(self.__malformation)),
            "死胎 dead：{dead}".format(dead=str(self.__dead)),
            "總仔數 total_born：{total_born}".format(total_born=str(self.get_total_born())),
            "活仔數 born_alive：{born_alive}".format(born_alive=str(self.get_born_alive())),
            "死仔數 born_dead：{born_dead}".format(born_dead=str(self.get_born_dead())),
            "窩重 total_weight：{weight}".format(weigth=str(self.__total_weight)),
            "公豬數 n_of_male：{male}".format(male=str(self.__n_of_male)),
            "母豬數 n_of_female：{female}".format(female=str(self.__n_of_female)),
            "備註 note：{note}".format(note=str(self.__note))
        ])

        return s
    
    def __eq__(self, __value: object) -> bool:
        
        if __value is None:
            return False
        
        if not isinstance(__value, Farrowing):
            raise TypeError("Can not compare Farrowing with {type_}".format(type_=str(type(__value))))
        
        result = True

        # Compare estrus
        if self.__estrus is None and __value.get_estrus() is None:
            pass
        elif self.__estrus is None or __value.get_estrus() is None:
            return False
        else:
            result = result \
                and (self.__estrus.get_sow().get_id() == __value.get_estrus().get_sow().get_id())\
                and (self.__estrus.get_sow().get_birthday() == __value.get_estrus().get_sow().get_birthday())\
                and (self.__estrus.get_sow().get_farm() == __value.get_estrus().get_sow().get_farm())\
                and (self.__estrus.get_estrus_datetime() == __value.get_estrus().get_estrus_datetime())
            
        return result \
            and (self.__farrowing_date == __value.get_farrowing_date()) \
            and (self.__crushing == __value.get_crushing()) \
            and (self.__black == __value.get_black()) \
            and (self.__weak == __value.get_weak()) \
            and (self.__malformation == __value.get_malformation()) \
            and (self.__dead == __value.get_dead())\
            and (self.__total_weight == __value.get_total_weight()) \
            and (self.__n_of_male == __value.get_n_of_male()) \
            and (self.__n_of_female == __value.get_n_of_female())
    
    def set_estrus(self, estrus: Estrus) -> None:
        '''* Raise TypeError and ValueError'''

        if not isinstance(estrus, Estrus):
            raise TypeError("estrus should be an estrus. Get {type_}".format(type_=str(type(estrus))))
        if not estrus.is_unique():
            raise ValueError("estrus should be unqiue.\n{estrus}".format(estrus=estrus))
        
        self.__estrus = estrus

    def set_farrowing_date(self, farrowing_date) -> None:
        '''
        * param date: any ISO format
        * Raise TypeError and ValueError
        '''

        self.__farrowing_date = transform_date(farrowing_date)
  
    def set_crushing(self, crushing: int) -> None:

        if not isinstance(crushing, int):
            raise TypeError("crushing should be an int. Get {type_}".format(type_=str(type(crushing))))
        self.__crushing = crushing

    def set_black(self, black: int) -> None:

        if not isinstance(black, int):
            raise TypeError("black should be an int. Get {type_}".format(type_=str(type(black))))
        self.__black = black

    def set_weak(self, weak: int) -> None:

        if not isinstance(weak, int):
            raise TypeError("weak should be an int. Get {type_}".format(type_=str(type(weak))))
        self.__weak = weak

    def set_malformation(self, malformation: int) -> None:

        if not isinstance(malformation, int):
            raise TypeError("malformation should be an int. Get {type_}".format(type_=str(type(malformation))))
        self.__malformation = malformation

    def set_dead(self, dead: int) -> None:

        if not isinstance(dead, int):
            raise TypeError("dead should be an int. Get {type_}".format(type_=str(type(dead))))
        self.__dead = dead

    def set_n_of_male(self, n_of_male: int) -> None:

        if not isinstance(n_of_male, int):
            raise TypeError("n_of_male should be an int. Get {type_}".format(type_=str(type(n_of_male))))
        self.__n_of_male = n_of_male

    def set_n_of_female(self, n_of_female: int) -> None:

        if not isinstance(n_of_female, int):
            raise TypeError("n_of_female should be an int. Get {type_}".format(type_=str(type(n_of_female))))
        self.__n_of_female = n_of_female

    def set_total_weight(self, total_weight: int) -> None:

        if not isinstance(total_weight, int):
            raise TypeError("total_weight should be an int. Get {type_}".format(type_=str(type(total_weight))))
        self.__total_weight = total_weight

    def set_note(self, note: str) -> None:

        if not isinstance(note, str):
            raise TypeError("note should be a string. Get {type_}".format(type_=str(type(note))))
        self.__note = note

    def get_estrus(self) -> Estrus:
        return self.__estrus
    
    def get_farrowing_date(self) -> date:
        return self.__farrowing_date
    
    def get_crushing(self) -> int:
        return self.__crushing
    
    def get_black(self) -> int:
        return self.__black
    
    def get_weak(self) -> int:
        return self.__weak
    
    def get_malformation(self) -> int:
        return self.__malformation
    
    def get_dead(self) -> int:
        return self.__dead
    
    def get_n_of_male(self) -> int:
        return self.__n_of_male
    
    def get_n_of_female(self) -> int:
        return self.__n_of_female
    
    def get_born_alive(self) -> int:
        return add_with_None(self.__n_of_male, self.__n_of_female)        
        
    def get_born_dead(self) -> int:
        return add_with_None(self.__crushing, self.__black, self.__malformation, self.__weak, self.__dead)

    def get_total_born(self) -> int:
        return self.get_born_alive() + self.get_born_dead()
    
    def get_total_weight(self) -> int:
        return self.__total_weight
    
    def get_note(self) -> int:
        return self.__note