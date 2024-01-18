import pymysql
import json

class BaseModel():
    '''
    A base class that can connect to mysql database and do query.
    
    Since let other classes, even its children, knowing how to connect to the database is dangerous, 
    every query should be execute by the `query` method.
    '''


    def __init__(self):

        with open("setting.json") as json_file:
            self.__config = json.load(json_file)
        
    def query(self, sql_query: str) -> tuple:
        '''* Raise TypeError'''

        if not isinstance(sql_query, str):
            raise TypeError("sql_query should be a string. Get {type_}.".format(type_=str(type(sql_query))))
        
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
                raise error
            
    def delete_all(self, table: str):
        '''Delete all data in the table. Should only be used in debugging.'''

        if not isinstance(table, str):
            raise TypeError()
        
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

    def find_multiple(
            self, 
            table: str = {},
            equal: dict = {}, 
            larger: dict = {}, 
            smaller: dict = {},
            larger_equal: dict = {},
            smaller_equal: dict = {},
            order_by: str = None
        ) -> list:
        '''
        Find all objects satisfy the conditions. 
        Keys of the dictionary should be same as attributes.
        * Different conditions will be connected by AND.
        * Sire and Dam should be listed as sire_id, sire_birthday, ...
        * param table: the name of table want to search
        * param equal: query will be `key`=`value`
        * param larger: query will be `key`>`value`
        * param smaller: query will be `key`<`value`
        * param order_by: `column_name` `ASC|DESC`
        * Raise TypeError, ValueError
        '''

        if not isinstance(table, str):
            raise TypeError("table should be a str. Get {type_}.".format(type_=str(type(table))))
        if not isinstance(equal, dict):
            raise TypeError("equal should be a dict. Get {type_}.".format(type_=str(type(equal))))
        if not isinstance(smaller, dict):
            raise TypeError("smaller should be a dict. Get {type_}.".format(type_=str(type(smaller))))
        if not isinstance(larger, dict):
            raise TypeError("larger should be a dict. Get {type_}.".format(type_=str(type(larger))))        
        if not isinstance(larger_equal, dict):
            raise TypeError("larger_equal should be a dict. Get {type_}.".format(type_=str(type(larger_equal))))        
        if not isinstance(smaller_equal, dict):
            raise TypeError("smaller_equal should be a dict. Get {type_}.".format(type_=str(type(smaller_equal))))        
        if not isinstance(order_by, (str, type(None))):
            raise TypeError("order_by should be a dict. Get {type_}.".format(type_=str(type(order_by))))        

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
            raise ValueError("Searching condition can not be empty.")

        sql_query = "SELECT * FROM {table} WHERE {condition}".format(
            table=table,
            condition=" AND ".join(conditions)
        )
        if order_by is not None:
            sql_query = "".join([sql_query, "ORDER BY ", order_by])
        sql_query = "".join([sql_query, ";"])
        results = self.query(sql_query)
        return results