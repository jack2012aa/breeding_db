import pymysql

from data_structures.pig import Pig
from . import BaseModel


class PigModel(BaseModel):

    def __init__(self):
        super().__init__()

    def __get_attributes(self, pig: Pig) -> dict:
        ''' Generate a dictionary of non-empty attributes'''

        attributes = {
            "id": pig.get_id(),
            "birthday": str(pig.get_birthday()),
            "farm": pig.get_farm(),
            "breed": pig.get_breed(),
            "naif_id": pig.get_naif_id(),
            "gender": pig.get_gender(),
            "chinese_name": pig.get_chinese_name(),
        }
        if pig.get_dam() is not None:
            attributes["dam_id"] = pig.get_dam().get_id()
            attributes["dam_birthday"] = str(pig.get_dam().get_birthday())
            attributes["dam_farm"] = pig.get_dam().get_farm()
        if pig.get_sire() is not None:
            attributes["sire_id"] = pig.get_sire().get_id()
            attributes["sire_birthday"] = str(pig.get_sire().get_birthday())
            attributes["sire_farm"] = pig.get_sire().get_farm()

        return attributes


    def insert(self, pig: Pig) -> None:
        '''
        Insert a pig to the database. \\
        Checking the format of pig is not `PigModel`'s responsibility. This method only confirm 
        primary keys are not None. Please use this method after you make sure the format is correct.
        * Raise TypeError, ValueError
        '''

        if not isinstance(pig, Pig):
            raise TypeError("pig should be an object of Pig. Get {type_}".format(type_=type(pig)))

        # Check primary key.
        if pig.get_id() is None:
            raise TypeError("id can not be None")
        if pig.get_birthday() is None:
            raise TypeError("birthday can not be None")
        if pig.get_farm() is None:
            raise TypeError("farm can not be None")
        
        # Pick non-empty attributes.
        attributes = self.__get_attributes(pig)
        columns = []
        values = []
        for key, item in attributes.items():
            if item is not None:
                columns.append(key)
                values.append("'{item}'".format(item=item))
        sql_query = "INSERT INTO Pigs ({columns}) VALUES ({values});".format(
            columns=", ".join(columns), 
            values=", ".join(values)
        )

        try:
            self.query(sql_query)
        except pymysql.err.IntegrityError as error:
            raise ValueError(str(error))
        # Not sure what type of error may come up.
        except Exception as error:
            raise error

    def dict_to_pig(self, pig_dict: dict) -> Pig:
        '''
        Transform a dictionary from query to a pig instance.
        * If the pig is not unique, return None.
        * Raise TypeError
        '''

        if not isinstance(pig_dict, dict):
            raise TypeError("pig_dict should be a dict. Get {type_}".format(type_=str(type(pig_dict))))
        
        pig = Pig()
        if pig_dict["id"] is not None:
            pig.set_id(pig_dict["id"])
        if pig_dict["birthday"] is not None:
            pig.set_birthday(pig_dict["birthday"])
        if pig_dict["farm"] is not None:
            pig.set_farm(pig_dict["farm"])
        if pig_dict["breed"] is not None:
            pig.set_breed(pig_dict["breed"])
        if pig_dict["naif_id"] is not None:
            pig.set_naif_id(pig_dict["naif_id"])
        if pig_dict["gender"] is not None:
            pig.set_gender(pig_dict["gender"])
        if pig_dict["chinese_name"] is not None:
            pig.set_chinese_name(pig_dict["chinese_name"])
        if pig_dict["sire_id"] is not None:
            sire = Pig()
            sire.set_id(pig_dict["sire_id"])
            sire.set_birthday(pig_dict["sire_birthday"])
            sire.set_farm(pig_dict["sire_farm"])
            pig.set_sire(sire)
        if pig_dict["dam_id"] is not None:
            dam = Pig()
            dam.set_id(pig_dict["dam_id"])
            dam.set_birthday(pig_dict["dam_birthday"])
            dam.set_farm(pig_dict["dam_farm"])
            pig.set_dam(dam)

        if not pig.is_unique():
            return None

        return pig

    def find_pig(self, pig: Pig) -> Pig:
        '''
        Find a pig in the database through primary keys.
        * Raise TypeError, ValueError
        '''

        if not isinstance(pig, Pig):
            raise TypeError("pig should be a Pig. Get {type_}".format(type_=str(type(pig))))
        
        if not pig.is_unique():
            raise ValueError("pig {pig} should be unique".format(pig=str(pig)))
        
        sql_query = "SELECT * FROM Pigs WHERE id='{id}' AND birthday='{birthday}' AND farm='{farm}';".format(
            id=pig.get_id(),
            birthday=str(pig.get_birthday()),
            farm=pig.get_farm()
        )

        result = self.query(sql_query)

        # pig not found
        if len(result) == 0:
            return None

        return self.dict_to_pig(result[0])

    def find_multiple(
            self, 
            equal: dict = {}, 
            larger: dict = {}, 
            smaller: dict = {},
            larger_equal: dict = {},
            smaller_equal: dict = {},
            order_by: str = None
        ) -> list:
        '''
        Find all pigs satisfy the conditions. 
        Keys of the dictionary should be same as attributes.
        * Different conditions will be connected by AND.
        * Sire and Dam should be listed as sire_id, sire_birthday, ...
        * param equal: query will be `key`=`value`
        * param larger: query will be `key`>`value`
        * param smaller: query will be `key`<`value`
        * param order_by: `column_name` `ASC|DESC`
        * Raise TypeError, ValueError
        '''

        results = super().find_multiple("Pigs", 
            equal, 
            larger, 
            smaller, 
            larger_equal, 
            smaller_equal, 
            order_by
        )
        pigs = []
        for pig in results:
            pigs.append(self.dict_to_pig(pig))
        
        return pigs
    
    def update(self, pig: Pig):
        '''
        Update attributes of a single pig. 
        The attributes of the argument `pig` excluding id, birthday and farm will be changed.
        * param pig: an unique pig.
        * Raise ValueError and TypeError.
        '''

        if not isinstance(pig, Pig):
            raise TypeError("pig must be a Pig. Get {type_}".format(type_=str(type(pig))))

        if not pig.is_unique():
            raise ValueError("The pig must have id, birthday and farm.")
        
        attributes = self.__get_attributes(pig)
        setting = []
        for key, value in attributes.items():
            if value is not None:
                setting.append("{key}='{value}'".format(key=key, value=value))
        condition = "id='{id}' AND birthday='{birthday}' AND farm='{farm}'".format(
            id=pig.get_id(),
            birthday=str(pig.get_birthday()),
            farm=pig.get_farm()
        )
        sql_query = "UPDATE Pigs SET {setting} WHERE {condition};".format(
            setting=", ".join(setting),
            condition=condition
        )

        self.query(sql_query)
        
    def find_all(self) -> None:
        '''Should only be used in debugging'''

        print(self.query("SELECT * FROM Pigs;"))

