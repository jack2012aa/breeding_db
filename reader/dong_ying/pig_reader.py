from datetime import date

from factory import ParentError
from factory.dong_ying_factory import DongYingPigFactory
from general import ask
from general import type_check
from models.pig_model import PigModel
from reader import ExcelReader


class DongYingPigReader(ExcelReader):


    def __init__(self, path: str, output_file_name: str, not_null: bool):

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
            }, 
            not_null=not_null
        )
        self.df.sort_values(by=["Birthday"], inplace=True)
    
    def create_pigs(
            self,
            ignore_parent: bool = False,
            in_farm: bool = True,
            nearest: bool = True,
            update: bool = False,
        ):
        '''
        Create pigs instance and generate list of pigs with incorrect format.

        If it is the first commit, please set `ignore_parent` as True since 
        parents are foriegn fields in the database.
        * param in_farm: `True` to only searching in_farm parent.
        * param nearest: `True` to automatically choose the pig with nearest birthday as the parent.
        * param ignore_parent: `False` to not arrange dam and sire of the pig.
        * param update: `True` to auto update when duplicate primary key is found.
        in the database in this commit.
        '''

        model = PigModel()

        for index, self._record in self.df.iterrows():

            self._factory = DongYingPigFactory()
            self._not_nan = self._record.notna()

            # Check null
            id = str(self._check_null("ID", self._factory.Flags.ID_FLAG.value))
            breed = str(self._check_null("Breed", self._factory.Flags.BREED_FLAG.value))
            birthday = self._check_null("Birthday", self._factory.Flags.BIRTHDAY_FLAG.value)
            if birthday is not None:
                birthday = birthday.date()
            reg_id = str(self._check_null("reg_id", self._factory.Flags.REG_FLAG.value))
            chinese_name = str(self._check_null("Chinese_name", 0))
            gender = str(self._check_null("Gender", self._factory.Flags.GENDER_FLAG.value))
            if not ignore_parent:
                sire = str(self._check_null("Sire", self._factory.Flags.SIRE_FLAG.value))
                dam = str(self._check_null("Dam", self._factory.Flags.DAM_FLAG.value))
            else:
                sire = dam = None

            # Set values
            self._factory.set_id(id)
            self._factory.set_birthday(birthday)
            self._factory.set_farm()
            self._factory.set_breed(breed)
            self._factory.set_reg_id(reg_id)
            self._factory.set_chinese_name(chinese_name)
            self._factory.set_gender(gender)
            self._factory.set_parent(dam=False, parent_id=sire, in_farm=in_farm, nearest=nearest)
            self._factory.set_parent(dam=True, parent_id=dam, in_farm=in_farm, nearest=nearest)

            # Class specific checks
            # If any statement in the confusing note column, reject this pig.
            if self._not_nan.get("confusing_note"):
                self._factory._turn_on_flag(DongYingPigFactory.Flags.ID_FLAG.value)
                self._factory.error_messages.append("不允許有相近耳號")

            # Check the birthday delta between this pig and the last pig with the same id.
            '''---------------------------Not Done-----------------------------'''

            # Check flags
            if self._factory.get_flag() != 0:
                self.insert_output()
                continue

            # Insert
            try:
                if self._factory.pig.is_unique():
                    model.insert(self._factory.pig)
            # Duplicate PK
            except ValueError:
                duplicate = model.find_pig(self._factory.pig)
                if self._factory.pig == duplicate:
                    continue
                else:
                    if not update:
                        if ask(
                            "遇到重複豬隻，請問如何處理？\n讀到的豬：\n{pig}\n已有的豬：\n{other}\nY:標記並略過 N：修改".format(
                                pig=str(self._factory.pig),
                                other=str(duplicate)
                            )
                        ):
                            # Incorrect data. Add to output excel.
                            self._factory.error_messages.append("與資料庫中的資料重複且不相符")
                            self._factory._turn_on_flag(self._factory.Flags.ID_FLAG)
                            self.insert_output()
                        else:
                            model.update(self._factory.pig)
                    else:
                        #修改豬隻資料
                        model.update(self._factory.pig)

            factory = None

        super().end()