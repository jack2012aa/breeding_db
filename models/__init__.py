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