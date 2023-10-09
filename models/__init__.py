
class BaseModel():

    database = None

    def __init__(self):
        pass
    '''
        with open("setting.json") as json_file:
            config = json.load(json_file)
        self.database = pymysql.connect(
            host = config["DATABASE_HOST"],
            user = config["USER"],
            password = config["PASSWORD"],
            database = config["DATABASE"]
        )'''

    def close(self):
        pass
        #self.database.close()