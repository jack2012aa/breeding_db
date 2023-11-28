import pandas as pd
import openpyxl
from .pig_factory import DongYingFactory
from datetime import date

class CsvReader:
    
    def __init__(self):
        self.df = None
        self.pigs = []
        self.review = None

class DongYingCsvReader(CsvReader):
    '''
    '''

    def __init__(self, path: str):

        super().__init__()
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

    fill = openpyxl.styles.PatternFill(fill_type="solid", fgColor="DDDDDD")

    def create_pigs(self):
        '''Create pigs instance and generate list of pigs with incorrect format.'''

        # Set output excel
        output = openpyxl.Workbook()
        sheet = output.create_sheet('基本資料')
        count = 0

        for index, pig in self.df.iterrows():

            # Set values
            factory = DongYingFactory()
            factory.set_breed(str(pig.get('Breed')))
            factory.set_id(str(pig.get('ID')))
            factory.set_birthday(pig.get('Birthday').date())
            factory.set_parent('sire',str(pig.get('Sire')))
            factory.set_parent('dam',str(pig.get('Dam')))
            factory.set_naif_id(str(pig.get('naif_id')))
            factory.set_gender(str(pig.get('Gender')))
        
            # If errors happen
            if factory.get_flag() > 0:
                count += 1
                data = pig.to_list()
                data.append(str(factory.error_messages))
                sheet.append(data)
                # Check the flag and highlight incorrect cells
                flags = [factory.BREED_FLAG, factory.ID_FLAG, factory.BIRTHDAY_FLAG, factory.SIRE_FLAG,factory.DAM_FLAG,factory.NAIF_FLAG,factory.GENDER_FLAG]
                columns = ['a','b','c','d','e','f','h']
                for i in range(len(flags)):
                    if factory.check_flag(flags[i]):
                        sheet[columns[i] + str(count)].fill = self.fill
                
            else:
                self.pigs.append(factory.pig)
            
            factory = None
        # If pig in pigs exists in the database, ask how to do.
        output.save('./test/output.xlsx')