from factory import ParentError
from factory.dong_ying_factory import DongYingPigFactory
from general import ask
from general import type_check
from models.pig_model import PigModel
from reader import ExcelReader


class DongYingPigReader(ExcelReader):


    def __init__(self, path: str, output_file_name: str):

        type_check(path, "path", str)
        type_check(output_file_name, "output_file_name", str)

        # df format:
        # [Index, Breed, ID, mark, Birthday, Sire, Dam, reg_id, Chinese_name, ., ., ., Gender,...]
        # to [Breed, ID, Birthday, Sire, Dam, reg_id, Chinese_name, Gender]
        usecols=[1, 2, 3, 4, 5, 6, 7, 8, 12]
        names=[
            'Breed',
            'ID',
            "confusing_note",
            'Birthday',
            'Sire',
            'Dam',
            'reg_id',
            'Chinese_name',
            'Gender',
        ]
        dtype={
            'Breed':'object',
            'ID':'object',
            "confusing_note": "object",
            'Birthday':'object',
            'Sire':'object',
            'Dam':'object',
            'reg_id':'object',
            'Chinese_name':'object',
            'Gender':'object',
        }
        super().__init__(
            path=path,
            use_columns=usecols,
            names=names,
            dtype=dtype,
            output_file_name=output_file_name,
            output_page_name="基本資料",
            flag_to_output={
                1: "a",
                2: "b",
                4: "d",
                8: "e",
                16: "f",
                32: "g",
                64: "h"
            }
        )

        self.df.sort_values(by=["birthday"], inplace=True)

    def __check_null(self, field: str, flag: int, default = None):

        if self.__not_nan.get(field):
            return self.__record.get(field)
        elif self.__not_null:
            self.__factory._turn_on_flag(flag)
            self.__factory.error_messages.append("{field} 不能為空值")
        return default

    def create_pigs(
            self,
            ignore_parent: bool = False,
            not_null: bool = True,
            in_farm: bool = True,
            nearest: bool = False,
            update: bool = False
    ):
        
        # Type check
        type_check(ignore_parent, "ignore_parent", bool)
        type_check(not_null, "not_null", bool)
        type_check(in_farm, "in_farm", bool)
        type_check(nearest, "nearest", bool)
        type_check(update, "update", bool)

        self.__not_null = not_null
        model = PigModel()

        for index, self.__record in self.df.iterrows():

            self.__factory = DongYingPigFactory()
            self.__not_nan = self.__record.notna()

            # Check null
            id = self.__check_null("ID", self.__factory.Flags.ID_FLAG.value, "000000")
            breed = self.__check_null("Breed", )
            # Set value
            # Class specific check
            # Check flags
            # Insert