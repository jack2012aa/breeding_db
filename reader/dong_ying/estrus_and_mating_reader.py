from data_structures.estrus import Estrus
from data_structures.estrus import PregnantStatus
from data_structures.estrus import TestResult
from factory.dong_ying_factory import DongYingEstrusFactory
from factory.dong_ying_factory import DongYingMatingFactory
from general import type_check
from models.estrus_model import EstrusModel
from models.mating_model import MatingModel
from reader import ExcelReader


import re
from datetime import datetime


class DongYingEstrusAndMatingReader(ExcelReader):
    '''
    ## Description
    The reader to read estrus and mating data provided by Dong-Ying. 
    These data is included in a table, so I only implement one reader to 
    handle this job.

    ## Logic

    ### Parity check
    Every estrus should be record before next one is read. This is confirm 
    by checking parity delta and time delta (delta = current - last):
    1. parity delta < 0 -> Must be an error.
    2. parity delta = 0 and time delta > 50 -> existing unrecord estrus.
    3. parity delta > 1 -> existing unrecord estrus.

    ### Time delta check
    We have to know what happens between two estrus. One method is to guess 
    by time delta: 
    1. time delta < 0 -> Must be an error. 
    2. 0 <= time delta < 3 -> Double mating.

    ### Pregnant status check
    * If the `note` column mention "*流產*", then the status will be set to 
    abortion.
    * Else if 21th_day_test is `False`  or the note is "*未*上*", the status 
    will be set to no.
    * Else it will be set to unknown.
    '''

    def __init__(
            self, 
            path: str,
            output_file_name: str,
            not_null: bool,
            double_mating_days_roof: int = 3,
            next_estrus_days_roof: int = 50,
            repair_parity: bool = False,
            repair_21th_day_test: bool = False,
            repair_pregnant_status: bool = False
    ):
        '''
        : param double_mate_days_roof: the maximum possible days of double mates in an estrus.
        : param next_estrus_dats_roof: the maximum possible days between two estrus without pregnant.
        '''

        type_check(double_mating_days_roof, "double_mate_date_roof", int)
        type_check(repair_parity, "repair_parity", bool)
        type_check(repair_21th_day_test, "repair_21th_day_test", bool)
        type_check(repair_pregnant_status, "repair_pregnant_status", bool)

        # df format:
        # [sow_id, parity, boar_id, mating_date, week_age, mating_time, times, character, 21th_day_test, note_date, note, ...]
        # to [sow_id, parity, boar_id, mating_date, mating_time, 21th_day_test, note]
        usecols = [0, 1, 2, 3, 5, 8, 9, 11]
        names = [
            "sow_id",
            "parity",
            "boar_id",
            "mating_date",
            "mating_time",
            "21th_day_test",
            "60th_day_test",
            "note"
        ]
        dtype = {
            "sow_id": "object",
            # Parity may not be an integer in the excel.
            # Type should be checked later.
            "parity": "object",
            "boar_id": "object",
            "mating_date": "object",
            "mating_time": "object",
            "21th_day_test": "object",
            "60th_day_test": "object", 
            "note": "object",
        }
        super().__init__(
            path=path,
            use_columns=usecols,
            names=names,
            dtype=dtype,
            output_file_name=output_file_name, 
            output_page_name="發情與配種資料",
            flag_to_output={1:"A", 2:"D", 8:"B", 16: "F", 32: "G"},
            not_null=not_null
        )

        self.__double_mate_date_roof = double_mating_days_roof
        self.__next_estrus_days_roof = next_estrus_days_roof
        self.__repair_parity = repair_parity
        self.__repair_21th_day_test = repair_21th_day_test
        self.__repair_pregnant_status = repair_pregnant_status

        self.df.sort_values(by=["mating_date", "mating_time"], inplace=True)

    def create_estrus_and_mating(self, default_mating_time: str = "16:00:00"):
        '''Please see the description of the class.'''

        type_check(default_mating_time, "default_mating_time", str)

        estrus_model = EstrusModel()
        mating_model = MatingModel()

        for index, self._record in self.df.iterrows():

            self._not_nan = self._record.notna()
            self._factory = DongYingEstrusFactory()

            # Check null
            # If sow_id or mating_date is empty, use a fake value so the factory know it is wrong.
            sow_id = str(self._check_null("sow_id", self._factory.Flags.SOW_FLAG.value, "fake_id"))
            mating_date = str(self._check_null("mating_date", self._factory.Flags.ESTRUS_DATE_FLAG.value, "1980-01-01").date())
            time = str(self._check_null("mating_time", self._factory.Flags.ESTRUS_DATE_FLAG.value, default_mating_time))
            parity = str(self._check_null("parity", self._factory.Flags.PARITY_FLAG.value))
            if parity.isnumeric():
                parity = int(parity)
            elif parity == "None":
                parity = None
            else:
                self._factory._turn_on_flag(self._factory.Flags.PARITY_FLAG.value)
                self._factory.error_messages.append("胎次必須為整數")
                parity = None
            _21th_day = self._check_null("21th_day_test", self._factory.Flags._21TH_DAY_TEST_FLAG.value)
            _60th_day = self._check_null("60th_day_test", self._factory.Flags._60TH_DAY_TEST_FLAG.value)

            # Set values
            self._factory.set_sow(sow_id, mating_date)
            self._factory.set_estrus_datetime(mating_date, time)
            self._factory.set_parity(parity)
            self._factory.set_pregnant(PregnantStatus.UNKNOWN)
            self._factory.set_21th_day_test(str(_21th_day))
            self._factory.set_60th_day_test(str(_60th_day))

            # Class specific checks
            # Calculate time delta
            birthday = self._factory.estrus.get_sow().get_birthday() if self._factory.estrus.is_unique() else "1968-01-01"
            sow_id = self._factory.estrus.get_sow().get_id() if self._factory.estrus.is_unique() else "fake-id"

            old_records = estrus_model.find_multiple(
                equal={"id": sow_id, "birthday": birthday, "farm": "Dong-Ying"},
                smaller={"estrus_datetime": str(self._factory.estrus.get_estrus_datetime())},
                order_by="estrus_datetime ASC"
            )
            if len(old_records) == 0:
                time_delta = -1
                last = Estrus()
                parity_delta = parity
            else:
                dt = datetime.strptime(" ".join([mating_date, time]), "%Y-%m-%d %H:%M:%S")
                last: Estrus = old_records.pop()
                time_delta = (dt - last.get_estrus_datetime()).days
                parity_delta = parity - last.get_parity() if last.get_parity() is not None and parity is not None else parity

            if parity is not None:
                if parity_delta < 0:
                    self._factory._turn_on_flag(self._factory.Flags.PARITY_FLAG.value)
                    self._factory.error_messages.append("胎次不可以比資料庫中的資料低。資料庫中最後一筆紀錄的胎次為{pairty}".format(
                        parity=str(last.get_parity())
                    ))
                elif parity_delta == 0 and time_delta > self.__next_estrus_days_roof:
                    self._factory._turn_on_flag(self._factory.Flags.ESTRUS_DATE_FLAG.value)
                    self._factory.error_messages.append("與上次發情（{date}）間隔太長，請紀錄所有發情/配種".format(
                        date=str(last.get_estrus_datetime())
                    ))
                elif parity_delta > 1:
                    self._factory._turn_on_flag(self._factory.Flags.PARITY_FLAG.value)
                    self._factory.error_messages.append("資料庫並未有前一胎次的發情/配種紀錄")

            if time_delta < 0 and last.is_unique():
                self._factory._turn_on_flag(self._factory.Flags.ESTRUS_DATE_FLAG.value)
                self._factory.error_messages.append("發情/配種日期不能比資料庫的前一筆資料更早")

            # Check pregnant status
            note = "" if not self._not_nan.get("note") else str(self._record.get("note"))
            if self._factory.estrus.get_21th_day_test() == TestResult.NOT_PREGNANT \
                or self._factory.estrus.get_60th_day_test() == TestResult.NOT_PREGNANT\
                or (re.search(r"未.*上", note) is not None):
                self._factory.set_pregnant(PregnantStatus.NO)
            elif re.search(r"流產", note) is not None:
                self._factory.set_pregnant(PregnantStatus.ABORTION)

            # Check flags
            if self._factory.get_flag() != 0:
                self._set_output_columns({1:"A", 2:"D", 8:"B", 16: "F", 32: "G"})
                self.insert_output()
                continue
            # Insert
            # Check time delta
            elif 0 <= time_delta <= self.__double_mate_date_roof:
                estrus = last
            else:
                # estrus must be unique due to the fake id and mating date
                estrus_model.insert(self._factory.estrus)
                estrus = self._factory.estrus

            # Check null
            self._factory = DongYingMatingFactory()
            boar_id = str(self._check_null("boar_id", self._factory.Flags.BOAR_FLAG.value, "fake_id"))

            # Set values
            self._factory.set_estrus(estrus)
            self._factory.set_mating_datetime(mating_date, time)
            self._factory.set_boar(boar_id, mating_date)

            # Check flags
            if self._factory.get_flag() != 0:
                self._set_output_columns({1:"A", 2:"D", 4:"C"})
                self.insert_output()
                continue

            mating_model.insert(self._factory.mating)

        super().end()