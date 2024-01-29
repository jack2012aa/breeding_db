import openpyxl

from data_structures.estrus import PregnantStatus
from factory.dong_ying_factory import DongYingFarrowingFactory
from models.estrus_model import EstrusModel
from models.farrowing_model import FarrowingModel
from reader import ExcelReader


class DongYingFarrowingReader(ExcelReader):

    def __init__(self, path: str):

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
        super().__init__(path, cols, names, dtype)

    def create_farrowings(self):
        '''
        total_born, born_alive and born_dead will be checked.
        '''

        # Set output excel
        output = openpyxl.Workbook()
        sheet = output.create_sheet("配種資料")
        count = 0

        model = FarrowingModel()

        for index, record in self.df.iterrows():

            is_nan = record.isna()
            factory = DongYingFarrowingFactory()

            id = "fake_id" if is_nan.iloc[0] else record.get("id")
            farrowing_date = "1980-01-01" if is_nan.iloc[1] else record.get("farrowing_date").date()
            factory.set_estrus(id, farrowing_date)

            factory.set_farrowing_date(farrowing_date)

            def set_numeric(func, name, i, chinese, flag):
                if not is_nan.iloc[i]:
                    if isinstance(record.get(name), int):
                        func(int(record.get(name)))
                    else:
                        factory._turn_on_flag(flag)
                        factory.error_messages.append("{chinese}數字格式錯誤".format(chinese=chinese))

            set_numeric(factory.set_n_of_male, "n_of_male", 2, "公小豬", factory.Flags.N_OF_MALE_FLAG.value)
            set_numeric(factory.set_n_of_female, "n_of_female", 3, "母小豬", factory.Flags.N_OF_FEMALE_FLAG.value)
            set_numeric(factory.set_crushing, "crushing", 4, "壓死", factory.Flags.CRUSHING_FLAG.value)
            set_numeric(factory.set_black, "black", 5, "黑胎", factory.Flags.BLACK_FLAG.value)
            set_numeric(factory.set_weak, "weak", 6, "虛弱死", factory.Flags.WEAK_FLAG.value)
            set_numeric(factory.set_malformation, "malformation", 7, "畸形", factory.Flags.MALFORMATION_FLAG.value)
            set_numeric(factory.set_dead, "dead", 8, "死胎", factory.Flags.DEAD_FLAG.value)

            born_alive = 0 if is_nan.iloc[10] else int(record.get("born_alive"))
            born_dead = 0 if is_nan.iloc[11] else int(record.get("born_dead"))
            if born_dead != factory.farrowing.get_born_dead():
                factory._turn_on_flag(factory.Flags.CRUSHING_FLAG.value)
                factory._turn_on_flag(factory.Flags.BLACK_FLAG.value)
                factory._turn_on_flag(factory.Flags.WEAK_FLAG.value)
                factory._turn_on_flag(factory.Flags.MALFORMATION_FLAG.value)
                factory._turn_on_flag(factory.Flags.DEAD_FLAG.value)
                factory.error_messages.append("總死仔數與死亡數不相符")
            if born_alive != factory.farrowing.get_born_alive():
                factory._turn_on_flag(factory.Flags.N_OF_MALE_FLAG.value)
                factory._turn_on_flag(factory.Flags.N_OF_FEMALE_FLAG.value)
                factory.error_messages.append("活仔數與出生公母小豬數不相符")

            set_numeric(factory.set_total_weight, "total_weight", 12, "出生窩重", factory.Flags.TOTAL_WEIGHT_FLAG)
            if not is_nan.iloc[13]:
                factory.set_note(record.get("note"))

            # If the flag is on, throw this data to output file.
            if factory.get_flag() != 0:
                count += 1
                data = record.to_list()
                data.append(str(factory.error_messages))
                sheet.append(data)
                # Check the flag and highlight incorrect cells
                columns = {
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
                for flag in factory.Flags:
                    if factory.check_flag(flag.value):
                        sheet[columns[flag.value] + str(count)].fill = self.fill
                continue

            model.insert(factory.farrowing)
            EstrusModel().update_pregnant(factory.farrowing.get_estrus(), PregnantStatus.YES)

        output.save('./test/reader/dong_ying/output3.xlsx')