from factory import ParentError
from factory.dong_ying_factory import DongYingPigFactory
from models.pig_model import PigModel
from reader import ExcelReader
from general import ask

import openpyxl
import pandas as pd
from collections import deque


class DongYingPigReader(ExcelReader):

    fill = openpyxl.styles.PatternFill(fill_type="solid", fgColor="DDDDDD")

    def __init__(self, path: str):

        # df format:
        # [Index, Breed, ID, mark, Birthday, Sire, Dam, naif_id, Chinese_name, ., ., ., Gender,...]
        # to [Breed, ID, Birthday, Sire, Dam, naif_id, Chinese_name, Gender]
        usecols=[1,2,4,5,6,7,8,12]
        names=[
            'Breed',
            'ID',
            'Birthday',
            'Sire',
            'Dam',
            'naif_id',
            'Chinese_name',
            'Gender'
        ]
        dtype={
            'Breed':'object',
            'ID':'object',
            'Birthday':'object',
            'Sire':'object',
            'Dam':'object',
            'naif_id':'object',
            'Chinese_name':'object',
            'Gender':'object'
        }
        super().__init__(path, usecols, names, dtype)

    def create_pigs(self, ignore_parent: bool = False, in_farm: bool = True, nearest: bool = True, update: bool = False):
        '''
        Create pigs instance and generate list of pigs with incorrect format.

        If it is the first commit, please set `ignore_parent` as True since 
        parents are foriegn fields in the database.
        * param in_farm: `True` to only searching in_farm parent.
        * param nearest: `True` to automatically choose the pig with nearest birthday as the parent.
        * param ignore_parent: `False` to not arrange dam and sire of the pig.
        * param update: `True` to auto update when duplicate primary key is found.
        in the database in this commit.

        ## To Do
        * Check pigs with same id but close birthday.
        '''

        # Set output excel
        output = openpyxl.Workbook()
        sheet = output.create_sheet('基本資料')
        count = 0
        flags = [
            DongYingPigFactory.BREED_FLAG,
            DongYingPigFactory.ID_FLAG,
            DongYingPigFactory.BIRTHDAY_FLAG,
            DongYingPigFactory.SIRE_FLAG,
            DongYingPigFactory.DAM_FLAG,
            DongYingPigFactory.NAIF_FLAG,
            DongYingPigFactory.GENDER_FLAG
        ]
        columns = ['a','b','c','d','e','f','h']
        model = PigModel()

        # Control flow
        count = 0
        length = len(self.queue)

        while len(self.queue) != 0:

            # Control flow
            if count == length:
                if length == len(self.queue):
                    break
                else:
                    count = 0
                    length = len(self.queue)
            count += 1
            wait_for_parent = False

            # Set values
            factory = DongYingPigFactory()
            pig = self.queue.popleft()
            not_nan = pig.notna()
            if not_nan.iloc[0]:
                factory.set_breed(str(pig.get('Breed')))
            if not_nan.iloc[1]:
                factory.set_id(str(pig.get('ID')))
            if not_nan.iloc[2]:
                factory.set_birthday(pig.get('Birthday').date())
            if not_nan.iloc[5]:
                factory.set_naif_id(str(pig.get('naif_id')))
            if not_nan.iloc[6]:
                factory.set_chinese_name(str(pig.get('Chinese_name')))
            if not_nan.iloc[7]:
                factory.set_gender(str(pig.get('Gender')))
            factory.set_farm()

            if not ignore_parent:
                try:
                    if not_nan.iloc[3]:
                        factory.set_parent(False, str(pig.get("Sire")), in_farm, nearest)
                    if not_nan.iloc[4]:
                        factory.set_parent(True, str(pig.get("Dam")), in_farm, nearest)
                except ParentError:
                    self.queue.append(pig)
                    wait_for_parent = True

            # If errors happen
            if factory.get_flag() > 0:
                count += 1
                data = pig.to_list()
                data.append(str(factory.error_messages))
                sheet.append(data)
                # Check the flag and highlight incorrect cells
                for i in range(len(flags)):
                    if factory.check_flag(flags[i]):
                        sheet[columns[i] + str(count)].fill = self.fill
                if wait_for_parent:
                    self.queue.pop()
            else:
                # If pig in pigs exists in the database, ask how to do.
                try:
                    if factory.pig.is_unique():
                        model.insert(factory.pig)
                except ValueError:
                    duplicate = model.find_pig(factory.pig)
                    if factory.pig == duplicate:
                        pass
                    else:
                        if not update:
                            if ask(
                                "遇到重複豬隻，請問如何處理？\n讀到的豬：\n{pig}\n已有的豬：\n{other}\nY:標記並略過 N：修改".format(
                                    pig=str(factory.pig),
                                    other=str(duplicate)
                                )
                            ):
                                # Incorrect data. Add to output excel.
                                data = pig.to_list()
                                data.append("與資料庫中的資料重複且不相符")
                                sheet.append(data)
                                count += 1
                            else:
                                model.update(factory.pig)
                        else:
                            #修改豬隻資料
                            model.update(factory.pig)

            factory = None

        output.save('./test/reader/output.xlsx')


class DongYingEstrusAndMatingReader(ExcelReader):
    '''
    ## Description
    The reader to read estrus and mating data provided by Dong-Ying. 
    These data is included in a table, so I only implement one reader to 
    handle this job.

    ## Logic
    The excel only provides mating date. If a sow appears in the table more 
    than one time, the second time it appears may because: 
    1. it is the second mating in a single estrus,
    2. the sow did not get pregnant in last estrus,
    3. it is in the next parity.

    We can easily distinguish these cases by calculating the time delta 
    between the two records. Here I define:
    1. delta = 0 ~ 15 days
    2. delta = 16 ~ 30 days
    3. delta > 30 days
    
    To calculate time delta, the reader will sort the records by mating_date 
    in ascending order, so the earlier record can be inserted into the 
    database first. Before insertion, the reader will check the last estrus 
    of the sow in the database to calculate the time delta. If the delta is 
    in range 1, then this record will only be inserted into the `mating` table.
    Delta in range 2 accompanying with the same parity is seem as an error.

    ## Auto Repair
    Since there are plenty of emtpy columns in history data, so I come up with 
    some repair mechanisms, which are listed below.

    ### Parity
    * If the sow has historical estrus in the database, calculate time delta. 
    If delta > 180 days, then parity = old parity + 1. Else, the parity does 
    not change.
    * If the sow has no historical data, then parity = 1.

    ### Mating time
    * If mating time is empty, fill in 10:00.

    ### 21th_day_test
    * If the sow has another record in the excel and time delta < 40 days, 
    it will be set to `False`. Else `True`.
    * This attribute has not included in the database. So this auto fill in 
    is not implemented. Here is just a note.

    ### Pregnant Status
    * If the `note` column mention "*流產*", then the status will be set to 
    abortion.
    * Else if 21th_day_test is `False` (without auto fill in) or the note 
    is "*未*上*", the status will be set to no.
    * If the sow has another record in the excel and time delta < 40 days, 
    it will be set to no. If 40 <= delta <= 180, the status will be set to 
    abortion. If delta > 180, the status will be set to yes.
    '''

    def __init__(self, path: str):

        # df format:
        # [sow_id, parity, boar_id, mating_date, week_age, mating_time, times, character, 21th_day_test, note_date, note, ...]
        # to [sow_id, parity, boar_id, mating_date, mating_time, 21th_day_test, note]
        usecols=[0, 1, 2, 3, 5, 8, 10],
        names=[
            "sow_id", 
            "parity", 
            "boar_id", 
            "mating_date", 
            "mating_time", 
            "21th_day_test", 
            "note"
        ]
        dtype={
            'sow_id':'object',
            'parity':'int',
            'boar_id':'object',
            'mating_date':'object',
            'mating_time':'object',
            '21th_day_test':'object',
            'note':'object',
        }
        super().__init__(path, usecols, names, dtype)