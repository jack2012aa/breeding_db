import pymysql

from data_structures.estrus import Estrus
from . import BaseModel

class EstrusModel(BaseModel):

    def __init__(self):
        super().__init__()

    def insert(self, estrus: Estrus):
        '''
        Insert an estrus record to the database. \\
        Checking the format of estrus is not `EstrusModel`'s responsibility. This method only confirm 
        primary keys are not None. Please use this method after you make sure the format is correct.
        * Raise TypeError, ValueError, KeyError
        '''

        if not isinstance(estrus, Estrus):
            raise TypeError("estrus should be an Estrus. Get {type_}".format(str(type(estrus))))
        
        if not estrus.is_unique():
            raise ValueError("{estrus} should be unique.".format(estrus=str(estrus)))
        
        attributes = {
            "id": estrus.get_sow().get_id(),
            "birthday": estrus.get_sow().get_birthday(),
            "farm": estrus.get_sow().get_farm(),
            "estrus_datetime": estrus.get_estrus_datetime(),
            "pregnant": estrus.get_pregnant().value if (estrus.get_pregnant() is not None) else None,
            "parity": estrus.get_parity()
        }

        # Pick non-empty attributes.
        columns = []
        values = []
        for key, item in attributes.items():
            if item is not None:
                columns.append(key)
                values.append("'{item}'".format(item=str(item)))
        sql_query = "INSERT INTO Estrus ({columns}) VALUES ({values});".format(
            columns=", ".join(columns), 
            values=", ".join(values)
        )

        try:
            self.query(sql_query)
        except pymysql.err.IntegrityError as error:
            raise KeyError("Sow does not exist in the database.")
        # Not sure what type of error may come up.
        except Exception as error:
            raise error