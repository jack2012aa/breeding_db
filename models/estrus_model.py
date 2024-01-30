import pymysql

from data_structures.estrus import Estrus
from data_structures.estrus import PregnantStatus
from data_structures.pig import Pig
from general import type_check
from models import BaseModel


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

        type_check(estrus, "estrus", Estrus)        
        if not estrus.is_unique():
            raise ValueError("{estrus} should be unique.".format(estrus=str(estrus)))
        
        attributes = {
            "id": estrus.get_sow().get_id(),
            "birthday": estrus.get_sow().get_birthday(),
            "farm": estrus.get_sow().get_farm(),
            "estrus_datetime": estrus.get_estrus_datetime(),
            "pregnant": estrus.get_pregnant().value 
                if (estrus.get_pregnant() is not None) else None,
            "parity": estrus.get_parity(), 
            "21th_day_test": estrus.get_21th_day_test().value 
                if (estrus.get_21th_day_test() is not None) else None,
            "60th_day_test": estrus.get_60th_day_test().value 
                if (estrus.get_60th_day_test() is not None) else None,
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
        
    def dict_to_estrus(self, estrus_dict):

        estrus = Estrus()
        sow = Pig()
        sow.set_id(estrus_dict["id"])
        sow.set_birthday(estrus_dict["birthday"])
        sow.set_farm(estrus_dict["farm"])
        estrus.set_sow(sow)
        estrus.set_estrus_datetime(estrus_dict["estrus_datetime"])
        if estrus_dict["pregnant"] is not None:
            estrus.set_pregnant(PregnantStatus(estrus_dict["pregnant"]))
        if estrus_dict["parity"] is not None:
            estrus.set_parity(int(estrus_dict["parity"]))

        return estrus
    
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
        Find all estrus satisfy the conditions. 
        Keys of the dictionary should be same as attributes.
        * Different conditions will be connected by AND.
        * Sire and Dam should be listed as sire_id, sire_birthday, ...
        * param equal: query will be `key`=`value`
        * param larger: query will be `key`>`value`
        * param smaller: query will be `key`<`value`
        * param order_by: `column_name` `ASC|DESC`
        * Raise TypeError, ValueError
        '''

        results = super().find_multiple(
            "Estrus",
            equal,
            larger,
            smaller,
            larger_equal,
            smaller_equal,
            order_by
        )
        estrus = []
        for estrus_dict in results:
            estrus.append(self.dict_to_estrus(estrus_dict))

        return estrus
    
    def update_pregnant(self, estrus: Estrus, status: PregnantStatus):
        '''
        * param estrus: an unique estrus
        * Raise TypeError, ValueError
        '''

        if not isinstance(estrus, Estrus):
            raise TypeError("estrus should be an Estrus. Get {type_}".format(type_=str(type(estrus))))
        if not isinstance(status, PregnantStatus):
            raise TypeError("status should be a PregnantStatus. Get {type_}".format(type_=str(type(status))))
        
        if not estrus.is_unique():
            raise ValueError("estrus should be unique.\n{estrus}".format(estrus=str(estrus)))

        sql_query = "UPDATE Estrus SET pregnant='{status}' WHERE id='{id}' AND birthday='{birthday}' AND farm='{farm}' AND estrus_datetime='{datetime}';"
        sql_query = sql_query.format(
            status=status.value, 
            id=estrus.get_sow().get_id(),
            birthday=str(estrus.get_sow().get_birthday()), 
            farm=estrus.get_sow().get_farm(),
            datetime=str(estrus.get_estrus_datetime())
        )

        try:
            self.query(sql_query)
        except pymysql.err.IntegrityError as error:
            raise KeyError("Estrus does not exist in the database.")
        # Not sure what type of error may come up.
        except Exception as error:
            raise error