import pandas as pd
import openpyxl
from collections import deque

from factory import Factory
from general import type_check

class ExcelReader:

    fill = openpyxl.styles.PatternFill(fill_type="solid", fgColor="DDDDDD")

    def __init__(
            self, 
            path: str, 
            use_columns: list, 
            names: list, 
            dtype: dict, 
            output_file_name: str,
            output_page_name: str, 
            flag_to_output: dict
    ):
        '''
        * param path: the path of the excel file.
        * param usecolumns: which columns are to read in the excel.
        * param names: the name of these columns used in the dataframe.
        * param dtype: dtype of these columns.
        * param output_file_name: the file name of the excel noting incorrect data.
        * param output_page_name: the page name of the excel noting incorrect data.
        * param flag_to_output: a dictionary maps flag value to output column.
        '''

        type_check(path, "path", str)
        type_check(output_file_name, "output_file_name", str)
        type_check(output_page_name, "output_page_name", str)

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

        # Set output excel.
        self.__output = openpyxl.Workbook()
        self.__sheet = self.__output.create_sheet(output_page_name)
        self.__count = 1
        self.__output_columns = flag_to_output
        self.__output_file_name = output_file_name

    def insert_output(
            self, 
            data: list, 
            factory: Factory, 
    ):
        '''
        Insert error messages in the factory to the sheet and return current count.
        * param data: error data _before_ adding error messages.
        * param factory: error factory.
        '''

        type_check(factory, "factory", Factory)

        data.append(str(factory.error_messages))
        self.__sheet.append(data)
        # Check the flag and highlight incorrect cells
        for flag in factory.Flags:
            if factory.check_flag(flag.value):
                self.__sheet[self.__output_columns[flag.value] + str(self.__count)].fill = self.fill
        
        self.__count += 1

    def end(self):

        self.__output.save("{name}.xlsx".format(name=self.__output_file_name))