import pandas as pd
import openpyxl
from collections import deque

class ExcelReader:

    fill = openpyxl.styles.PatternFill(fill_type="solid", fgColor="DDDDDD")

    def __init__(self, path: str, use_columns: list, names: list, dtype: dict):
        '''
        * param path: the path of the excel file.
        * param usecolumns: which columns are to read in the excel.
        * param names: the name of these columns used in the dataframe.
        * param dtype: dtype of these columns.
        '''

        print("Reading...")
        self.df = pd.read_excel(
            path,
            usecols=use_columns,
            names=names,
            dtype=dtype
        )
        # Clean empty rows.
        self.df.dropna(how="all", inplace=True)
        self.queue = deque()
        for index, row in self.df.iterrows():
            self.queue.append(row)
        print("Success")
