import openpyxl

from data_structures.estrus import PregnantStatus
from factory.dong_ying_factory import DongYingFarrowingFactory
from models.estrus_model import EstrusModel
from models.farrowing_model import FarrowingModel
from reader import ExcelReader


class DongYingFarrowingReader(ExcelReader):

    def __init__(
            self,
            path: str,
            output_file_name: str, 
            not_null: bool
    ):

        cols = [0, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 20]
        names = [
            "id", 
            "farrowing_date", 
            "n_of_male", 
            "n_of_female", 
            "crushing", 
            "black", 
            "weak", 
            "malformation", 
            "dead", 
            "total_born", 
            "born_alive", 
            "born_dead", 
            "total_weight", 
            "note"
        ]
        dtype = {key: value for key, value in zip(names, ["object"] * len(names))}
        output_columns = {
            1: "A", 
            2: "B", 
            4: "E", 
            8: "F", 
            16: "G", 
            32: "H", 
            64: "I", 
            128: "C",
            256: "D", 
            512: "M"
        }
        super().__init__(
            path=path,
            use_columns=cols,
            names=names, 
            dtype=dtype,
            output_file_name=output_file_name, 
            output_page_name="分娩資料", 
            flag_to_output=output_columns, 
            not_null=not_null
        )

    def create_farrowings(self):
        ''' total_born, born_alive and born_dead will be checked.'''


        model = FarrowingModel()

        for index, self._record in self.df.iterrows():

            is_nan = self._record.isna()
            self._factory = DongYingFarrowingFactory()

            id = "fake_id" if is_nan.iloc[0] else self._record.get("id")
            farrowing_date = "1980-01-01" if is_nan.iloc[1] else self._record.get("farrowing_date").date()
            self._factory.set_estrus(id, farrowing_date)

            self._factory.set_farrowing_date(farrowing_date)

            def set_numeric(func, name, i, chinese, flag):
                if not is_nan.get(name):
                    if isinstance(self._record.get(name), int):
                        func(int(self._record.get(name)))
                    else:
                        self._factory._turn_on_flag(flag)
                        self._factory.error_messages.append("{chinese}數字格式錯誤".format(chinese=chinese))
                elif self._not_null:
                    self._factory._turn_on_flag(flag)
                    self._factory.error_messages.append("{field}不能為空".format(field=chinese))

            set_numeric(self._factory.set_n_of_male, "n_of_male", 2, "公小豬", self._factory.Flags.N_OF_MALE_FLAG.value)
            set_numeric(self._factory.set_n_of_female, "n_of_female", 3, "母小豬", self._factory.Flags.N_OF_FEMALE_FLAG.value)
            set_numeric(self._factory.set_crushing, "crushing", 4, "壓死", self._factory.Flags.CRUSHING_FLAG.value)
            set_numeric(self._factory.set_black, "black", 5, "黑胎", self._factory.Flags.BLACK_FLAG.value)
            set_numeric(self._factory.set_weak, "weak", 6, "虛弱死", self._factory.Flags.WEAK_FLAG.value)
            set_numeric(self._factory.set_malformation, "malformation", 7, "畸形", self._factory.Flags.MALFORMATION_FLAG.value)
            set_numeric(self._factory.set_dead, "dead", 8, "死胎", self._factory.Flags.DEAD_FLAG.value)

            born_alive = 0 if is_nan.iloc[10] else int(self._record.get("born_alive"))
            born_dead = 0 if is_nan.iloc[11] else int(self._record.get("born_dead"))
            if born_dead != self._factory.farrowing.get_born_dead():
                self._factory._turn_on_flag(self._factory.Flags.CRUSHING_FLAG.value)
                self._factory._turn_on_flag(self._factory.Flags.BLACK_FLAG.value)
                self._factory._turn_on_flag(self._factory.Flags.WEAK_FLAG.value)
                self._factory._turn_on_flag(self._factory.Flags.MALFORMATION_FLAG.value)
                self._factory._turn_on_flag(self._factory.Flags.DEAD_FLAG.value)
                self._factory.error_messages.append("總死仔數與死亡數不相符")
            if born_alive != self._factory.farrowing.get_born_alive():
                self._factory._turn_on_flag(self._factory.Flags.N_OF_MALE_FLAG.value)
                self._factory._turn_on_flag(self._factory.Flags.N_OF_FEMALE_FLAG.value)
                self._factory.error_messages.append("活仔數與出生公母小豬數不相符")

            set_numeric(self._factory.set_total_weight, "total_weight", 12, "出生窩重", self._factory.Flags.TOTAL_WEIGHT_FLAG.value)
            if not is_nan.iloc[13]:
                self._factory.set_note(self._record.get("note"))

            # If the flag is on, throw this data to output file.
            if self._factory.get_flag() != 0:
                self.insert_output()
                continue

            model.insert(self._factory.farrowing)
            EstrusModel().update_pregnant(self._factory.farrowing.get_estrus(), PregnantStatus.YES)

        self.end()