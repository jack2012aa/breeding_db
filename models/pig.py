from data_structures.pig import Pig
from . import BaseModel


class PigModel(BaseModel):

    def __init__(self):
        super().__init__()

    def insert(self, pig: Pig) -> None:
        '''
        Insert a pig to the database. \\
        Checking the format of pig is not `PigModel`'s responsibility. This method only confirm 
        primary keys are not None. Please use this method after you make sure the format is correct.
        * Raise TypeError
        '''

        if not isinstance(pig, Pig):
            raise TypeError("pig should be an object of Pig. Get {type_}".format(type_=type(pig)))

        # Check primary key.
        if pig.get_id() is None:
            raise TypeError("id can not be None")
        if pig.get_birthday is None:
            raise TypeError("birthday can not be None")
        if pig.get_farm is None:
            raise TypeError("farm can not be None")
        
        # Pick non-empty attributes.
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
        # Not sure what type of error may come up.
        except Exception as error:
            raise error

    def delete_all(self) -> None:
        '''Delete all data in the table. Should only be used in debugging.'''

        try:
            self.query("DELETE FROM Pigs;")
        except Exception as error:
            raise error

    def find_pig(self, pig: Pig) -> Pig:

        pig = Pig()
        pig.set_id('123456')
        pig.set_birthday('2020-02-03')
        return pig