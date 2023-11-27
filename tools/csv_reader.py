import pandas as pd

class CsvReader:
    
    def __init__(self, path: str):
        df = pd.read_excel(path)
        pigs = []

class DongYingCsvReader(CsvReader):
    '''
    * df format: [Index, Breed, ID, mark, Birthday, Sire, Dam, naif_id, Chinese_name, ., ., ., Gender,...]
    '''

    def __init__(self, path: str):
        super().__init__(path)

    def create_pigs(self):
        '''Create pigs instance and generate list of pigs with incorrect format.'''