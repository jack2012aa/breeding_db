import pandas as pd
from .pig_factory import DongYingFactory
from datetime import date

class CsvReader:
    
    def __init__(self):
        self.df
        self.pigs = []

class DongYingCsvReader(CsvReader):
    '''
    '''

    def __init__(self, path: str):

        print("Reading...")
        ''' df format:

            [Index, Breed, ID, mark, Birthday, Sire, Dam, naif_id, Chinese_name, ., ., ., Gender,...]
            to [Breed, ID, Birthday, Sire, Dam, naif_id, Chinese_name, Gender]
        '''
        self.df = pd.read_excel(
            path,
            usecols=[1,2,4,5,6,7,8,12],
            names=['Breed','ID','Birthday','Sire','Dam','naif_id','Chinese_name','Gender'],
            dtype={'Breed':'object','ID':'object','Birthday':'object','Sire':'object','Dam':'object','naif_id':'object','Chinese_name':'object','Gender':'object'}
        )
        self.df.dropna(how = 'all', inplace = True)
        print("Success")


    def create_pigs(self):
        '''Create pigs instance and generate list of pigs with incorrect format.'''

        for index, pig in self.df.iterrows():

            factory = DongYingFactory()

            # Set values
            try:
                factory.set_breed(pig.get('Breed'))
                factory.set_id(pig.get('ID'))
                factory.set_gender(pig.get('Gender'))
                factory.set_birthday(pig.get('Birthday').date())
                factory.set_parent('sire',pig.get('Sire'))
                factory.set_parent('dam',pig.get('Dam'))
                factory.set_naif_id(pig.get('naif_id'))
                print(factory.pig)
                factory = None
            except:
                print(index)