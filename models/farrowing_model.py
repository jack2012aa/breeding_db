import pymysql

from models import BaseModel
from data_structures.farrowing import Farrowing


class FarrowingModel(BaseModel):

    def __init__(self):
        super().__init__()

    def insert(self, farrowing: Farrowing):
        '''
        Insert a farrwoing record to the database. \\
        Checking the format of farrowing is not `FarrowingModel`'s responsibility. This method only confirm 
        primary keys are not None. Please use this method after you make sure the format is correct.
        * Raise TypeError, ValueError, KeyError
        '''

        if not isinstance(farrowing, Farrowing):
            raise TypeError("farrowing should be a Farrowing. Get {type_}".format(str(type(farrowing))))
        
        if not farrowing.is_unique():
            raise ValueError("{farrowing} should be unique.".format(farrowing=str(farrowing)))
        
        attributes = {
            "id": farrowing.get_estrus().get_sow().get_id(),
            "birthday": str(farrowing.get_estrus().get_sow().get_birthday()),
            "farm": farrowing.get_estrus().get_sow().get_farm(),
            "estrus_datetime": str(farrowing.get_estrus().get_estrus_datetime()),
            "farrowing_date": str(farrowing.get_farrowing_date()),
            "crushing": farrowing.get_crushing(),
            "black": farrowing.get_black(),
            "weak": farrowing.get_weak(),
            "malformation": farrowing.get_malformation(),
            "dead": farrowing.get_dead(),
            "n_of_male": farrowing.get_n_of_male(),
            "n_of_female": farrowing.get_n_of_female(),
            "note": farrowing.get_note(), 
            "total_weight": farrowing.get_total_weight()
        }

        # Pick non-empty attributes.
        columns = []
        values = []
        for key, item in attributes.items():
            if item is not None:
                columns.append(key)
                values.append("'{item}'".format(item=str(item)))
        sql_query = "INSERT INTO Farrowings ({columns}) VALUES ({values});".format(
            columns=", ".join(columns), 
            values=", ".join(values)
        )

        try:
            self.query(sql_query)
        except pymysql.err.IntegrityError as error:
            if 1062 in error.args:
                raise ValueError("Duplicate key")
            if 1452 in error.args:
                raise KeyError("Estrus does not exist in the database.")
            raise error
        # Not sure what type of error may come up.
        except Exception as error:
            raise error