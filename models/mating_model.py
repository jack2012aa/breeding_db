import pymysql

from models import BaseModel
from data_structures.mating import Mating


class MatingModel(BaseModel):

    def __init__(self):
        super().__init__()

    def insert(self, mating: Mating):
        '''
        Insert a mating record to the database. \\
        Checking the format of estrus is not `MatingModel`'s responsibility. This method only confirm 
        primary keys are not None. Please use this method after you make sure the format is correct.
        * Raise TypeError, ValueError, KeyError
        '''

        if not isinstance(mating, Mating):
            raise TypeError("mating should be an Mating. Get {type_}".format(str(type(mating))))
        
        if not mating.is_unique():
            raise ValueError("{mating} should be unique.".format(mating=str(mating)))
        
        attributes = {
            "sow_id": mating.get_estrus().get_sow().get_id(),
            "sow_birthday": mating.get_estrus().get_sow().get_birthday(),
            "sow_farm": mating.get_estrus().get_sow().get_farm(),
            "estrus_datetime": mating.get_estrus().get_estrus_datetime(),
            "mating_datetime": mating.get_mating_datetime() if (mating.get_mating_datetime() is not None) else None,
            "boar_id": mating.get_boar().get_id(),
            "boar_birthday": mating.get_boar().get_birthday(),
            "boar_farm": mating.get_boar().get_farm()
        }

        # Pick non-empty attributes.
        columns = []
        values = []
        for key, item in attributes.items():
            if item is not None:
                columns.append(key)
                values.append("'{item}'".format(item=str(item)))
        sql_query = "INSERT INTO Matings ({columns}) VALUES ({values});".format(
            columns=", ".join(columns), 
            values=", ".join(values)
        )

        try:
            self.query(sql_query)
        except pymysql.err.IntegrityError as error:
            raise KeyError("Estrus or boar does not exist in the database.")
        # Not sure what type of error may come up.
        except Exception as error:
            raise error