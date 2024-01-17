import pandas as pd
from collections import deque

class ExcelReader:

    def __init__(self, path: str, usecolumns: list, names: list, dtype: dict):
        '''
        * param path: the path of the excel file.
        * param usecolumns: which columns are to read in the excel.
        * param names: the name of these columns used in the dataframe.
        * param dtype: dtype of these columns.
        '''

        print("Reading...")
        df = pd.read_excel(
            path,
            usecols=usecolumns,
            names=names,
            dtype=dtype
        )
        # Clean empty rows.
        df.dropna(how = 'all', inplace = True)
        self.queue = deque()
        for index, row in df.iterrows():
            self.queue.append(row)
        print("Success")
