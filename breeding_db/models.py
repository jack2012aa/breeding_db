import json
import logging

import pymysql

from breeding_db.general import type_check
from breeding_db.data_structures import Farrowing, Weaning
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

    def __generate_qeury_string(
        self,
        table_name: str, 
        equal: dict = {},
        larger: dict = {},
        smaller: dict = {},
        larger_equal: dict = {},
        smaller_equal: dict = {},
        order_by: str = None
    ) -> str:
        """Generate a sql query string look like:
        `SELECT * FROM {table_name} WHERE {conditions};`

        :param table_name: table's name in the database.
        :param equal: query will be `key`=`value`
        :param larger: query will be `key`>`value`
        :param smaller: query will be `key`<`value`
        :param larger_equal: query will be `key`>=`value`
        :param smaller_equal: query will be `key`<=`value`
        :param order_by: `column_name` `ASC|DESC`
        :raises ValueError: if all conditions are empty
        :raises TypeError: if passing in any parameter with incorrect type.
        :return: a sql query string.
        """
        
        type_check(table_name, "table_name", str)
        type_check(equal, "equal", dict)
        type_check(larger, "larger", dict)
        type_check(larger_equal, "larger_equal", dict)
        type_check(smaller, "smaller", dict)
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

        sql_query = f"SELECT * FROM {table_name} WHERE {' AND '.join(conditions)}"
        if order_by is not None:
            sql_query = "".join([sql_query, " ORDER BY ", order_by])
        sql_query = "".join([sql_query, ";"])
        return sql_query
    
    def __generate_insert_string(
        self, 
        attributes: dict, 
        table_name: str
    ) -> str:
        """Generate sql used for new insertion.

        :param attributes: attributes of inserted object.
        :param table_name: name of the table in the database.
        :return: sql string.
        """

        type_check(attributes, "attributes", dict)
        type_check(table_name, "table_name", str)

        # Pick non-empty attributes.
        columns = []
        values = []
        for key, item in attributes.items():
            if item is not None:
                columns.append(key)
                values.append(f"'{str(item)}'")
        insert_string = f"INSERT INTO {table_name} "
        insert_string += f"({', '.join(columns)}) VALUES ({', '.join(values)});"
        return insert_string

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
            "litter": pig.get_litter(),
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
        if pig_dict.get("litter") is not None:
            pig.set_litter(pig_dict.get("litter"))
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

        sql_query = self.__generate_qeury_string(
            table_name="Pigs", 
            equal=equal, 
            larger=larger, 
            smaller=smaller, 
            larger_equal=larger_equal, 
            smaller_equal=smaller_equal, 
            order_by=order_by
        )
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
        """Transform a dictionary from query to an unique estrus instance.

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
        sql_query = self.__generate_qeury_string(
            table_name="Estrus", 
            equal=equal, 
            larger=larger, 
            smaller=smaller, 
            larger_equal=larger_equal, 
            smaller_equal=smaller_equal, 
            order_by=order_by
        )

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
            "mating_datetime": mating.get_mating_datetime(),
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
        """ Update attributes of an estrus in the database.

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
        
    def dict_to_mating(self, mating_dict: dict) -> Mating | None:
        """Transform a dictionary from query to an unique Mating instance.

        If the mating is not unique, None will be returned. \

        :param mating_dict: a dictionary contains attributes of Mating.
        :return: a Mating object or None if mating is not unique.
        """

        type_check(mating_dict, "mating_dict", dict)

        mating = Mating()
        estrus = Estrus()
        sow = Pig()
        if mating_dict.get("sow_id") is not None:
            sow.set_id(mating_dict.get("sow_id"))
        if mating_dict.get("sow_farm") is not None:
            sow.set_farm(mating_dict.get("sow_farm"))
        if mating_dict.get("sow_birthday") is not None:
            sow.set_birthday(mating_dict.get("sow_birthday"))
        if sow.is_unique():
            estrus.set_sow(sow)
        if mating_dict.get("estrus_datetime") is not None:
            estrus.set_estrus_datetime(mating_dict.get("estrus_datetime"))
        if estrus.is_unique():
            mating.set_estrus(estrus)
        boar = Pig()
        if mating_dict.get("boar_id") is not None:
            boar.set_id(mating_dict.get("boar_id"))
        if mating_dict.get("boar_farm") is not None:
            boar.set_farm(mating_dict.get("boar_farm"))
        if mating_dict.get("boar_birthday") is not None:
            boar.set_birthday(mating_dict.get("boar_birthday"))
        if boar.is_unique():
            mating.set_boar(boar)
        if mating_dict.get("mating_datetime") is not None:
            mating.set_mating_datetime(mating_dict.get("mating_datetime"))
        
        if not mating.is_unique():
            return None
        return mating

    def find_matings(
            self,
            equal: dict = {},
            larger: dict = {},
            smaller: dict = {},
            larger_equal: dict = {},
            smaller_equal: dict = {},
            order_by: str = None
        ) -> list[Mating]:
        """ Find all matings satisfy the conditions. 

        Please make sure:
        * Keys of the dictionary should be same as attributes.
        * Different conditions will be connected by AND.
        * Sow should be listed as sow_id, sow_birthday, ...
        * Boar should be listed as boar_id, boar_birthday, ...
        
        :param equal: query will be `key`=`value`
        :param larger: query will be `key`>`value`
        :param smaller: query will be `key`<`value`
        :param larger_equal: query will be `key`>=`value`
        :param smaller_equal: query will be `key`<=`value`
        :param order_by: `column_name` `ASC|DESC`
        :raises: TypeError, ValueError.
        """

        sql_query = self.__generate_qeury_string(
            table_name="Matings", 
            equal=equal, 
            larger=larger, 
            smaller=smaller, 
            larger_equal=larger_equal, 
            smaller_equal=smaller_equal, 
            order_by=order_by
        )
        results = self.__query(sql_query)
        matings = []
        for dictionary in results:
            matings.append(self.dict_to_mating(dictionary))

        return matings
    
    def update_mating(self, mating: Mating) -> None:
        """ Update attributes of a Mating in the database.

        :param estrus: an unique Mating instance. attributes except primary \
            keys will be updatad.
        :raises: TypeError, ValueError.
        """

        type_check(mating, "mating", Mating)
        if not mating.is_unique():
            msg = f"mating should be unique. Got {mating}."
            logging.error(msg)
            raise ValueError(msg)

        attributes = self.__get_mating_attributes(mating)
        setting = []
        for key, value in attributes.items():
            if value is not None:
                setting.append("{key}='{value}'".format(key=key, value=value))
        condition = f"sow_id='{mating.get_estrus().get_sow().get_id()}' and "
        condition += f"sow_birthday='{str(mating.get_estrus().get_sow().get_birthday())}' and "
        condition += f"sow_farm='{mating.get_estrus().get_sow().get_farm()}' and "
        condition += f"estrus_datetime='{str(mating.get_estrus().get_estrus_datetime())}' and "
        condition += f"mating_datetime='{str(mating.get_mating_datetime())}'"
        sql_query = "UPDATE Matings SET {setting} WHERE {condition};".format(
            setting=", ".join(setting),
            condition=condition
        )

        self.__query(sql_query)


    def dict_to_farrowing(self, farrowing_dict: dict) -> Farrowing:
        """Transform a dictionary from query to an unique Farrowing instance.

        If the Farrowing is not unique, None will be returned. \

        :param farrowing_dict: a dictionary contains attributes of Farrowing.
        :raises TypeError: if farrowing_dict contains incorrect parameters type.
        :raises ValueError: if pass in incorrect parameter in farrowing_dict.
        :return: a Farrowing object or None if farrowing is not unique.
        """

        type_check(farrowing_dict, "farrowing_dict", dict)

        sow = Pig()
        estrus = Estrus()
        farrowing = Farrowing()

        # Create sow.
        if farrowing_dict.get("id") is not None:
            sow.set_id(farrowing_dict.get("id"))
        if farrowing_dict.get("birthday") is not None:
            sow.set_birthday(farrowing_dict.get("birthday"))
        if farrowing_dict.get("farm") is not None:
            sow.set_farm(farrowing_dict.get("farm"))
        if sow.is_unique():
            estrus.set_sow(sow)

        # Create estrus.
        if farrowing_dict.get("estrus_datetime") is not None:
            estrus.set_estrus_datetime(farrowing_dict.get("estrus_datetime"))
        if estrus.is_unique():
            farrowing.set_estrus(estrus)

        # Create farrowing.
        if farrowing_dict.get("farrowing_date") is not None:
            farrowing.set_farrowing_date(farrowing_dict.get("farrowing_date"))
        if farrowing_dict.get("crushed") is not None:
            farrowing.set_crushed(farrowing_dict.get("crushed"))
        if farrowing_dict.get("black") is not None:
            farrowing.set_black(farrowing_dict.get("black"))
        if farrowing_dict.get("weak") is not None:
            farrowing.set_weak(farrowing_dict.get("weak"))
        if farrowing_dict.get("malformation") is not None:
            farrowing.set_malformation(farrowing_dict.get("malformation"))
        if farrowing_dict.get("dead") is not None:
            farrowing.set_dead(farrowing_dict.get("dead"))
        if farrowing_dict.get("total_weight") is not None:
            farrowing.set_total_weight(farrowing_dict.get("total_weight"))
        if farrowing_dict.get("n_of_male") is not None:
            farrowing.set_n_of_male(farrowing_dict.get("n_of_male"))
        if farrowing_dict.get("n_of_female") is not None:
            farrowing.set_n_of_female(farrowing_dict.get("n_of_female"))
        if farrowing_dict.get("note") is not None:
            farrowing.set_note(farrowing_dict.get("note"))

        if not farrowing.is_unique():
            return None
        return farrowing
    
    def __get_farrowing_attributes(self, farrowing: Farrowing):
        """Get a dictionary of attributes.

        None attributes will remain None in the dict.
        :param farrowing: an Farrowing.
        """

        attributes = {
            "id": None,
            "birthday": None,
            "farm": None,
            "estrus_datetime": None,
            "farrowing_date": farrowing.get_farrowing_date(), 
            "crushed": farrowing.get_crushed(),
            "black": farrowing.get_black(),
            "weak": farrowing.get_weak(),
            "malformation": farrowing.get_malformation(),
            "dead": farrowing.get_dead(),
            "total_weight": farrowing.get_total_weight(),
            "n_of_male": farrowing.get_n_of_male(),
            "n_of_female": farrowing.get_n_of_female(), 
            "note": farrowing.get_note()
        }

        if farrowing.get_estrus() is not None:
            attributes["id"] = farrowing.get_estrus().get_sow().get_id()
            attributes["birthday"] = farrowing.get_estrus().get_sow().get_birthday()
            attributes["farm"] = farrowing.get_estrus().get_sow().get_farm()
            attributes["estrus_datetime"] = farrowing.get_estrus().get_estrus_datetime()

        return attributes

    def insert_farrowing(self, farrowing: Farrowing) -> None:
        """Insert a farrowing record to the database.

        :param farrowing: an unqiue Farrowing.
        """

        type_check(farrowing, "farrowing", Farrowing)
        
        if not farrowing.is_unique():
            msg = f"farrowing should be unique. Got {farrowing}."
            logging.error(msg)
            raise ValueError(msg)
        
        attributes = self.__get_farrowing_attributes(farrowing)

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
            self.__query(sql_query)
        except pymysql.err.IntegrityError:
            msg = "Estrus does not exist in the database."
            msg += f"\n Get {farrowing.get_estrus()}"
            raise KeyError(msg)
        
    def find_farrowings(
        self,
        equal: dict = {},
        larger: dict = {},
        smaller: dict = {},
        larger_equal: dict = {},
        smaller_equal: dict = {},
        order_by: str = None
    ) -> list[Farrowing]:
        """ Find all farrowings satisfy the conditions. 

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
        sql_query = self.__generate_qeury_string(
            table_name="Farrowings", 
            equal=equal, 
            larger=larger, 
            smaller=smaller, 
            larger_equal=larger_equal, 
            smaller_equal=smaller_equal, 
            order_by=order_by
        )

        results = self.__query(sql_query)
        estrus = []
        for dictionary in results:
            estrus.append(self.dict_to_farrowing(dictionary))

        return estrus
    
    def update_farrowing(self, farrowing: Farrowing) -> None:
        """ Update attributes of a farrowing in the database.

        :param farrowing: an unique Farrowing instance. Attributes except \
            primary keys will be updatad.
        :raises: TypeError, ValueError.
        """

        type_check(farrowing, "farrowing", Farrowing)
        if not farrowing.is_unique():
            msg = f"farrowing should be unique. Got {farrowing}."
            logging.error(msg)
            raise ValueError(msg)

        attributes = self.__get_farrowing_attributes(farrowing)
        setting = []
        for key, value in attributes.items():
            if value is not None:
                setting.append("{key}='{value}'".format(key=key, value=value))
        condition = f"id='{farrowing.get_estrus().get_sow().get_id()}' and "
        condition += f"birthday='{str(farrowing.get_estrus().get_sow().get_birthday())}' and "
        condition += f"farm='{farrowing.get_estrus().get_sow().get_farm()}' and "
        condition += f"estrus_datetime='{str(farrowing.get_estrus().get_estrus_datetime())}'"
        sql_query = "UPDATE Farrowings SET {setting} WHERE {condition};".format(
            setting=", ".join(setting),
            condition=condition
        )

        self.__query(sql_query)

    def dict_to_weaning(self, weaning_dict: dict) -> Weaning:
        """Transform a dictionary from query to an unique Weaning instance.

        If the Weaning is not unique, None will be returned. \

        :param weaning_dict: a dictionary contains attributes of Weaning.
        :raises TypeError: if weaning_dict contains incorrect parameters type.
        :raises ValueError: if pass in incorrect parameter in weaning_dict.
        :return: a Farrowing object or None if weaning is not unique.
        """

        type_check(weaning_dict, "weaning_dict", dict)

        sow = Pig(
            id=weaning_dict.get("id"), 
            farm=weaning_dict.get("farm"), 
            birthday=weaning_dict.get("birthday")
        )
        if not sow.is_unique():
            return None
        
        estrus = Estrus(
            sow=sow, 
            estrus_datetime=weaning_dict.get("estrus_datetime")
        )
        if not estrus.is_unique():
            return None
        
        farrowing = Farrowing(
            estrus=estrus, 
            farrowing_date=weaning_dict.get("farrowing_date")
        )
        if not farrowing.is_unique():
            return None
        
        weaning = Weaning(
            farrowing=farrowing, 
            weaning_date=weaning_dict.get("weaning_date"), 
            total_nursed_piglets=weaning_dict.get("total_nursed_piglets"), 
            total_weaning_piglets=weaning_dict.get("total_weaning_piglets"), 
            total_weaning_weight=weaning_dict.get("total_weaning_weight")    
        )
        return weaning
    
    def __get_weaning_attributes(self, weaning: Weaning) -> dict:
        """Get the attributes dictionary of weaning.

        :param weaning: a Weaning object.
        :raises TypeError: if weaning is not a Weaning.
        :return: a attributes dictionary of weaning.
        """

        type_check(weaning, "weaning", Weaning)

        weaning_dict = {
            "id": None, 
            "farm": None, 
            "birthday": None, 
            "estrus_datetime": None, 
            "farrowing_date": None, 
            "weaning_date": weaning.get_weaning_date(), 
            "total_nursed_piglets": weaning.get_total_nursed_piglets(), 
            "total_weaning_piglets": weaning.get_total_weaning_piglets(), 
            "total_weaning_weight": weaning.get_total_weaning_weight()
        }

        if weaning.is_unique():
            weaning_dict["id"] = weaning.get_farrowing().get_estrus().get_sow().get_id()
            weaning_dict["birthday"] = weaning.get_farrowing().get_estrus().get_sow().get_birthday()
            weaning_dict["farm"] = weaning.get_farrowing().get_estrus().get_sow().get_farm()
            weaning_dict["estrus_datetime"] = weaning.get_farrowing().get_estrus().get_estrus_datetime()
            weaning_dict["farrowing_date"] = weaning.get_farrowing().get_farrowing_date()
        
        return weaning_dict
    
    def insert_weaning(self, weaning: Weaning) -> None:
        """Insert a new weaning data into database.

        :param weaning: an unique Weaning object.
        :raises ValueError: if weaning is not unique.
        :raises KeyError: if weaning.__farrowing not exist in the database.
        """
        
        type_check(weaning, "weaning", Weaning)

        if not weaning.is_unique():
            msg = f"weaning should be unique. Got {weaning}."
            logging.error(msg)
            raise ValueError(msg)
        
        attributes = self.__get_weaning_attributes(weaning)
        sql_query = self.__generate_insert_string(attributes, "Weanings")

        try:
            self.__query(sql_query)
        except pymysql.err.IntegrityError:
            msg = "Farrowing does not exist in the database."
            msg += f"\n Get {weaning.get_farrowing()}"
            raise KeyError(msg)
        
    def find_weanings(
        self,
        equal: dict = {},
        larger: dict = {},
        smaller: dict = {},
        larger_equal: dict = {},
        smaller_equal: dict = {},
        order_by: str = None
    ) -> list[Weaning]:
        """ Find all weanings satisfy the conditions. 

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

        sql_query = self.__generate_qeury_string(
            table_name="Weanings", 
            equal=equal, 
            larger=larger, 
            smaller=smaller, 
            larger_equal=larger_equal, 
            smaller_equal=smaller_equal, 
            order_by=order_by
        )

        results = self.__query(sql_query)
        estrus = []
        for dictionary in results:
            estrus.append(self.dict_to_weaning(dictionary))

        return estrus
    
    def update_weaning(self, weaning: Weaning) -> None:
        """ Update attributes of a Weaning in the database.

        :param weaing: an unique Weaning instance. Attributes except \
            primary keys will be updatad.
        :raises: TypeError, ValueError.
        """

        type_check(weaning, "weaning", Weaning)
        if not weaning.is_unique():
            msg = f"weaning should be unique. Got {weaning}."
            logging.error(msg)
            raise ValueError(msg)
        
        attributes = self.__get_weaning_attributes(weaning)
        setting = []
        for key, value in attributes.items():
            if value is not None:
                setting.append("{key}='{value}'".format(key=key, value=value))
        id = weaning.get_farrowing().get_estrus().get_sow().get_id()
        birthday = weaning.get_farrowing().get_estrus().get_sow().get_birthday()
        farm = weaning.get_farrowing().get_estrus().get_sow().get_farm()
        estrus_datetime = weaning.get_farrowing().get_estrus().get_estrus_datetime()
        farrowing_date = weaning.get_farrowing().get_farrowing_date()
        condition = f"id='{id}' and birthday='{str(birthday)}' and farm='{farm}' "
        condition += f"and estrus_datetime='{str(estrus_datetime)}' and "
        condition += f"farrowing_date='{str(farrowing_date)}'"
        sql_query = "UPDATE Weanings SET {setting} WHERE {condition};".format(
            setting=", ".join(setting),
            condition=condition
        )

        self.__query(sql_query)