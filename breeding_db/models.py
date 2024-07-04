import json
import logging

import pymysql

from breeding_db.general import type_check
from breeding_db.data_structures import Pig, Estrus, Mating, PregnantStatus


class Model():

    def __init__(self, path: str):
        """ A class connects to mysql database and do query.

        Setting file should contain:
        1. DATABASE_HOST
        2. USER
        3. PASSWORD
        4. DATABASE
        5. CHARSET

        :param path: path to the json setting file.
        """
    
        type_check(path, "path", str)
        with open(path) as json_file:
            self.__config = json.load(json_file)

    def __query(self, sql_query: str) -> tuple:
        """ Do query.

        :param sql_query: the query string.
        """

        type_check(sql_query, "sql_query", str)

        with pymysql.connect(
            host=self.__config["DATABASE_HOST"],
            user=self.__config["USER"],
            password=self.__config["PASSWORD"],
            database=self.__config["DATABASE"],
            charset=self.__config["CHARSET"],
            cursorclass=pymysql.cursors.DictCursor
        ) as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(sql_query)
                result = cursor.fetchall()
                cursor.close()
                connection.commit()
                return result
            except Exception as error:
                cursor.close()
                logging.error(error.args[0])                
                raise error

    def _delete_all(self, table: str):
        """Delete all data in the table. Should only be used in debugging.
        
        :param table: name of the table to delete.
        """

        type_check(table, "table", str)

        with pymysql.connect(
            host=self.__config["DATABASE_HOST"],
            user=self.__config["USER"],
            password=self.__config["PASSWORD"],
            database=self.__config["DATABASE"],
            charset=self.__config["CHARSET"],
            cursorclass=pymysql.cursors.DictCursor
        ) as connection:
            cursor = connection.cursor()
            cursor.execute("SET foreign_key_checks = 0;")
            cursor.execute("DELETE FROM {table};".format(table=table))
            cursor.execute("SET foreign_key_checks = 1;")
            cursor.close()
            connection.commit()

    def __get_pig_attributes(self, pig: Pig) -> dict:
        """ Generate a dictionary of non-empty attributes."""

        attributes = {
            "id": pig.get_id(),
            "birthday": str(pig.get_birthday()),
            "farm": pig.get_farm(),
            "breed": pig.get_breed(),
            "reg_id": pig.get_reg_id(),
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

    def insert_pig(self, pig: Pig) -> None:
        """ Insert a pig to the database.

        :param pig: an unique pig instance.
        :raises: TypeError, ValueError.
        """

        type_check(pig, "pig", Pig)

        if not pig.is_unique():
            msg = f"pig should be unique. Got {pig}."
            logging.error(msg)
            raise ValueError(msg)

        # Pick non-empty attributes.
        attributes = self.__get_pig_attributes(pig)
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

        self.__query(sql_query)

    def dict_to_pig(self, pig_dict: dict) -> Pig:
        """ Transform a dictionary from query to an unique pig instance. 
        
        If the pig is not unique, None will be returned. \
        Incomplete sire/dam attributes will raise KeyError.

        :param pig_dict: a dictionary contains attributes of pig.
        :raises: TypeError, KeyError.
        """

        type_check(pig_dict, "pig_dict", dict)

        pig = Pig()
        if pig_dict.get("id") is not None:
            pig.set_id(pig_dict["id"])
        if pig_dict.get("birthday") is not None:
            pig.set_birthday(pig_dict["birthday"])
        if pig_dict.get("farm") is not None:
            pig.set_farm(pig_dict["farm"])
        if pig_dict.get("breed") is not None:
            pig.set_breed(pig_dict["breed"])
        if pig_dict.get("reg_id") is not None:
            pig.set_reg_id(pig_dict["reg_id"])
        if pig_dict.get("gender") is not None:
            pig.set_gender(pig_dict["gender"])
        if pig_dict.get("chinese_name") is not None:
            pig.set_chinese_name(pig_dict["chinese_name"])
        if pig_dict.get("sire_id") is not None:
            sire = Pig()
            sire.set_id(pig_dict["sire_id"])
            sire.set_birthday(pig_dict["sire_birthday"])
            sire.set_farm(pig_dict["sire_farm"])
            pig.set_sire(sire)
        if pig_dict.get("dam_id") is not None:
            dam = Pig()
            dam.set_id(pig_dict["dam_id"])
            dam.set_birthday(pig_dict["dam_birthday"])
            dam.set_farm(pig_dict["dam_farm"])
            pig.set_dam(dam)

        if not pig.is_unique():
            return None

        return pig

    def find_pig(self, pig: Pig) -> Pig:
        """ Find a pig in the database through primary keys.

        If the pig does not exist, return none.

        :param pig: an unique pig instance.
        :raises: TypeError, ValueError.
        """

        type_check(pig, "pig", Pig)

        if not pig.is_unique():
            msg = f"pig should be unique. Got {pig}."
            logging.error(msg)
            raise ValueError(msg)

        sql_query = f"SELECT * FROM Pigs WHERE id={pig.get_id()} "
        sql_query += f"AND birthday='{str(pig.get_birthday())}' "
        sql_query += f"AND farm='{pig.get_farm()}';"
        result = self.__query(sql_query)

        # pig not found
        if len(result) == 0:
            return None

        return self.dict_to_pig(result[0])

    def find_pigs(
            self,
            equal: dict = {},
            larger: dict = {},
            smaller: dict = {},
            larger_equal: dict = {},
            smaller_equal: dict = {},
            order_by: str = None
        ) -> list[Pig]:
        """ Find all pigs satisfy the conditions. 

        Please make sure:
        * Keys of the dictionary should be same as attributes.
        * Different conditions will be connected by AND.
        * Sire and Dam should be listed as sire_id, sire_birthday, ...
        
        :param equal: query will be `key`=`value`
        :param larger: query will be `key`>`value`
        :param smaller: query will be `key`<`value`
        :param larger_equal: query will be `key`>=`value`
        :param smaller_equal: query will be `key`<=`value`
        :param order_by: `column_name` `ASC|DESC`
        :raises: TypeError, ValueError.
        """

        type_check(equal, "equal", dict)
        type_check(smaller, "smaller", dict)
        type_check(larger, "larger", dict)
        type_check(larger_equal, "larger_equal", dict)
        type_check(smaller_equal, "smaller_equal", dict)
        if order_by is not None:
            type_check(order_by, "order_by", str)

        conditions = []
        for key, value in equal.items():
            conditions.append("{key}='{value}'".format(key=str(key), value=str(value)))
        for key, value in larger.items():
            conditions.append("{key}>'{value}'".format(key=str(key), value=str(value)))
        for key, value in smaller.items():
            conditions.append("{key}<'{value}'".format(key=str(key), value=str(value)))
        for key, value in larger_equal.items():
            conditions.append("{key}>='{value}'".format(key=str(key), value=str(value)))
        for key, value in smaller_equal.items():
            conditions.append("{key}<='{value}'".format(key=str(key), value=str(value)))

        if len(conditions) == 0:
            msg = "Searching condition can not be empty."
            logging.error(msg)
            raise ValueError(msg)
        
        sql_query = "SELECT * FROM Pigs WHERE {condition}".format(
            condition=" AND ".join(conditions)
        )
        if order_by is not None:
            sql_query = "".join([sql_query, "ORDER BY ", order_by])
        sql_query = "".join([sql_query, ";"])
        results = self.__query(sql_query)
        pigs = []
        for pig in results:
            pigs.append(self.dict_to_pig(pig))

        return pigs

    def update_pig(self, pig: Pig) -> None:
        """ Update attributes of a pig in the database.

        :param pig: an unique Pig instance. attributes except primary keys \
            will be updatad.
        :raises: TypeError, ValueError.
        """

        type_check(pig, "pig", Pig)
        if not pig.is_unique():
            msg = f"pig should be unique. Got {pig}."
            logging.error(msg)
            raise ValueError(msg)

        attributes = self.__get_pig_attributes(pig)
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

        self.__query(sql_query)

    def __get_estrus_attributes(self, estrus: Estrus) -> dict:
        """Get a dictionary of attributes.

        None attributes will remain None in the dict.
        :param estrus: an Estrus.
        """
        
        attributes = {
            "id": None,
            "birthday": None,
            "farm": None,
            "estrus_datetime": estrus.get_estrus_datetime(),
            "pregnant": estrus.get_pregnant().value if (estrus.get_pregnant() is not None) else None,
            "parity": estrus.get_parity()
        }

        if estrus.get_sow() is not None:
            attributes["id"] = estrus.get_sow().get_id()
            attributes["birthday"] = estrus.get_sow().get_birthday()
            attributes["farm"] = estrus.get_sow().get_farm()

        return attributes
    
    def insert_estrus(self, estrus: Estrus):
        """Insert an estrus record to the database.

        :param estrus: an unqiue Estrus.
        :raises: TypeError, ValueError, KeyError.
        """

        type_check(estrus, "estrus", Estrus)
        
        if not estrus.is_unique():
            msg = f"estrus should be unique. Got {estrus}."
            logging.error(msg)
            raise ValueError(msg)
        
        attributes = self.__get_estrus_attributes(estrus)

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
            self.__query(sql_query)
        except pymysql.err.IntegrityError:
            msg = "Sow does not exist in the database."
            msg += f"\n Get {estrus.get_sow()}"
            raise KeyError(msg)
        
    def dict_to_estrus(self, estrus_dict: dict) -> Estrus | None:
        """Transform a dictionary from query to an unique pig instance.

        If the estrus is not unique, None will be returned. \

        :param estrus_dict: a dictionary contains attributes of estrus.
        :return: an estrus object or None if estrus is not unique.
        """

        type_check(estrus_dict, "estrus_dict", dict)

        estrus = Estrus()
        sow = Pig()
        if estrus_dict.get("id") is not None:
            sow.set_id(estrus_dict.get("id"))
        if estrus_dict.get("birthday") is not None:
            sow.set_birthday(estrus_dict.get("birthday"))
        if estrus_dict.get("farm") is not None:
            sow.set_farm(estrus_dict.get("farm"))
        if not sow.is_unique():
            return None
        estrus.set_sow(sow)
        if estrus_dict.get("estrus_datetime") is not None:
            estrus.set_estrus_datetime(estrus_dict.get("estrus_datetime"))
        if estrus_dict.get("parity") is not None:
            estrus.set_parity(int(estrus_dict.get("parity")))
        if estrus_dict.get("pregnant") is not None:
            estrus.set_pregnant(PregnantStatus(estrus_dict.get("pregnant")))
        if not estrus.is_unique():
            return None
        return estrus

    def find_estrus(
            self,
            equal: dict = {},
            larger: dict = {},
            smaller: dict = {},
            larger_equal: dict = {},
            smaller_equal: dict = {},
            order_by: str = None
        ) -> list[Estrus]:
        """ Find all estrus satisfy the conditions. 

        Please make sure:
        * Keys of the dictionary should be same as attributes.
        * Different conditions will be connected by AND.
        * Sow should be listed as id, birthday, ...
        
        :param equal: query will be `key`=`value`
        :param larger: query will be `key`>`value`
        :param smaller: query will be `key`<`value`
        :param larger_equal: query will be `key`>=`value`
        :param smaller_equal: query will be `key`<=`value`
        :param order_by: `column_name` `ASC|DESC`
        :raises: TypeError, ValueError.
        """

        type_check(equal, "equal", dict)
        type_check(smaller, "smaller", dict)
        type_check(larger, "larger", dict)
        type_check(larger_equal, "larger_equal", dict)
        type_check(smaller_equal, "smaller_equal", dict)
        if order_by is not None:
            type_check(order_by, "order_by", str)

        conditions = []
        for key, value in equal.items():
            conditions.append("{key}='{value}'".format(key=str(key), value=str(value)))
        for key, value in larger.items():
            conditions.append("{key}>'{value}'".format(key=str(key), value=str(value)))
        for key, value in smaller.items():
            conditions.append("{key}<'{value}'".format(key=str(key), value=str(value)))
        for key, value in larger_equal.items():
            conditions.append("{key}>='{value}'".format(key=str(key), value=str(value)))
        for key, value in smaller_equal.items():
            conditions.append("{key}<='{value}'".format(key=str(key), value=str(value)))

        if len(conditions) == 0:
            msg = "Searching condition can not be empty."
            logging.error(msg)
            raise ValueError(msg)

        sql_query = "SELECT * FROM Estrus WHERE {condition}".format(
            condition=" AND ".join(conditions)
        )
        if order_by is not None:
            sql_query = "".join([sql_query, "ORDER BY ", order_by])
        sql_query = "".join([sql_query, ";"])
        results = self.__query(sql_query)
        estrus = []
        for dictionary in results:
            estrus.append(self.dict_to_estrus(dictionary))

        return estrus
        
    def __get_mating_attributes(self, mating: Mating):
        """Get a dictionary of attributes.

        None attributes will remain None in the dict.
        :param mating: an Mating.
        """

        attributes = {
            "sow_id": None,
            "sow_birthday": None,
            "sow_farm": None,
            "estrus_datetime": None,
            "mating_datetime": mating.get_mating_datetime() if (mating.get_mating_datetime() is not None) else None,
            "boar_id": mating.get_boar().get_id(),
            "boar_birthday": mating.get_boar().get_birthday(),
            "boar_farm": mating.get_boar().get_farm()
        }

        if mating.get_estrus() is not None:
            attributes["sow_id"] = mating.get_estrus().get_sow().get_id()
            attributes["sow_birthday"] = mating.get_estrus().get_sow().get_birthday()
            attributes["sow_farm"] = mating.get_estrus().get_sow().get_farm()
            attributes["estrus_datetime"] = mating.get_estrus().get_estrus_datetime()

        return attributes
    
    def update_estrus(self, estrus: Estrus) -> None:
        """ Update attributes of a estrus in the database.

        :param estrus: an unique Estrus instance. attributes except primary \
            keys will be updatad.
        :raises: TypeError, ValueError.
        """

        type_check(estrus, "estrus", Estrus)
        if not estrus.is_unique():
            msg = f"estrus should be unique. Got {estrus}."
            logging.error(msg)
            raise ValueError(msg)

        attributes = self.__get_estrus_attributes(estrus)
        setting = []
        for key, value in attributes.items():
            if value is not None:
                setting.append("{key}='{value}'".format(key=key, value=value))
        condition = f"id='{estrus.get_sow().get_id()}' and "
        condition += f"birthday='{str(estrus.get_sow().get_birthday())}' and "
        condition += f"farm='{estrus.get_sow().get_farm()}' and "
        condition += f"estrus_datetime='{str(estrus.get_estrus_datetime())}'"
        sql_query = "UPDATE Estrus SET {setting} WHERE {condition};".format(
            setting=", ".join(setting),
            condition=condition
        )

        self.__query(sql_query)
    
    def insert_mating(self, mating: Mating):
        """Insert a mating record to the database.

        :param mating: an unique Mating.
        :raises: TypeError, ValueError.
        """

        type_check(mating, "mating", Mating)
        if not mating.is_unique():
            msg = f"mating should be unique. Got {mating}."
            logging.error(msg)
            raise ValueError(msg)
        
        attributes = self.__get_mating_attributes(mating)

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
            self.__query(sql_query)
        except pymysql.err.IntegrityError:
            msg = "Estrus or boar does not exist in the database."
            msg += f"\n estrus: {mating.get_estrus()}."
            msg += f"\n boar: {mating.get_boar()}."
            logging.error(msg)
            raise KeyError(msg)