"""Read data from excel, create instances, insert them into db and create 
report csv file.
"""
import os
import logging

import pandas as pd

from breeding_db.general import ask, ask_multiple, type_check
from breeding_db.models import Model
from breeding_db.data_structures import Pig, Estrus, Mating


class ExcelReader():
    
    def __init__(self, path: str) -> None:
        """Read data from excel and insert data into database.

        :param path: path to the database settings.
        """
        type_check(path, "path", str)
        if not os.path.isfile(path):
            msg = f"Path {path} does not exist."
            logging.error(msg)
            raise FileNotFoundError(msg)
        self.model = Model(path)

    def __create_pig(self) -> Pig:
        pass
    
    def __create_estrus(self) -> Estrus:
        pass

    def __create_mating(self) -> Mating:
        pass

    def __remove_dash_from_id(self, id: str) -> str:
        """ Remove the dash and none numeric characters in an id, and add a 
        leading zero to the later hind of dash if the length of later hind is 
        smaller than 2.

        If more than one dash exist, only string before the second dash is kept.

        If any character is in the id, only string between first two characters 
        is kept.

        ## Example 
        * 1234-2 -> 123402
        * 1234-2-2 -> 123402
        * 20Y1234-2cao -> 123402
        * 20Y1234-12 -> 123412
        * 1234-2cao -> 123402

        :param id: a pig id.
        :raises: TypeError
        """

        type_check(id, "id", str)

        # Deal with the dash
        if '-' in id:
            front, hind = id.split('-')[0:2]
            # Add additional 0
            try:
                hind = hind + "tail"
                int(hind[0:2])
                hind = hind[0:2]
            except:
                hind = '0' + hind[0]
            id = front + hind

        # Find the index of every nonnumeric characters and slice the string between them.
        nonnumeric = []
        for i in range(len(id)):
            if not id[i].isnumeric():
                nonnumeric.append(i)
        if len(nonnumeric) > 0:
            slices = []
            for i in nonnumeric:
                slices.append(id[:i])
                id = id[i:]
            slices.append(id)
            # The longest digits is the most possible to be the id.
            id = max(slices, key=len, default="")

        return self.__remove_nonnumeric(id)

    def __remove_nonnumeric(self, s: str) -> str:
        ''' Remove all nonnumeric characters in s.'''

        result = ''
        for c in s:
            if c.isnumeric():
                result = ''.join([result,c])
        return result
    
    def __seperate_year_breed_id(
            self, id: str
        ) -> tuple[str | None, str | None, str]:
        """Seperate id in format {birth_year}{breed}{id}.
        
        If the id does not contain birth year and breed info, (None, None, id) 
        will be returned.

        If more than one breed character found in id, the first one will be 
        used.

        :param id: an id, should be in format {birth_year}{breed}{id}.
        :raises: TypeError, ValueError.
        """

        type_check(id, "id", str)
        year = None
        breed = None
        for possible_breed in Pig.BREED:
            if id.find(possible_breed) != -1:
                year, id = id.split(possible_breed)
                breed = possible_breed
                break

        if year is not None and len(year) == 2:
            year = f"20{year}"

        return (year, breed, self.__remove_dash_from_id(id))

    def read_and_insert_pigs(
        self, 
        farm: str,
        input_path: str = None, 
        dataframe: pd.DataFrame = None,
        output_path: str = os.path.curdir, 
        output_filename: str = "output.csv",
        allow_none: bool = False
    ) -> None:
        """Read pigs data in the source excel or dataframe, insert them into 
        database and create a report csv containing error data.

        Choose reading from excel or dataframe by pathing corresponding 
        parameter.

        If read from excel, "基本資料" sheet will be used.

        The source excel or dataframe must have below columns:
        1. 品種
        2. 耳號
        3. 生日
        4. 父畜
        5. 母畜
        6. 登錄號
        7. 中文名
        8. 性別

        :param farm: current farm.
        :param input_path: path of the source csv, including filename.
        :param dataframe: the source dataframe.
        :param output_path: path to save the report.
        :param output_filename: name of the report.
        :param allow_none: allow empty non-primary key. 
        :raises: ValueError, FileNotFoundError, TypeError, KeyError.
        """

        # Type check.
        if input_path is None and dataframe is None:
            msg = "You must choose to read from an excel file or a dataframe."
            logging.error(msg)
            raise ValueError(msg)
        
        if input_path is not None:
            type_check(input_path, "input_path", str)
            if not os.path.isfile(input_path):
                msg = f"File {input_path} does not exist."
                logging.error(msg)
                raise FileNotFoundError(msg)
            dataframe = pd.read_excel(io=input_path, sheet_name="基本資料")

        if dataframe is not None:
            type_check(dataframe, "dataframe", pd.DataFrame)
        
        type_check(farm, "farm", str)
        type_check(output_path, "output_path", str)
        type_check(output_filename, "output_filename", str)

        # Standardize the dataframe.
        dataframe.dropna(how = 'all', inplace = True)
        dataframe = dataframe.rename(columns={
            "品種": "Breed", 
            "耳號": "ID", 
            "生日": "Birthday", 
            "父畜": "Sire", 
            "母畜": "Dam", 
            "登錄號": "reg_id", 
            "中文名": "Chinese_name", 
            "性別": "Gender"
        })
        required_columns = [
            "Breed", 
            "ID", 
            "Birthday", 
            "Sire", 
            "Dam", 
            "reg_id", 
            "Chinese_name", 
            "Gender"
        ]
        if not set(required_columns).issubset(dataframe.columns):
            msg = "Missing key(s) in source excel or DataFrame."
            logging.error(msg)
            raise KeyError(msg)
        dataframe = dataframe.astype("object")
        dataframe.sort_values(by="Birthday", inplace=True, na_position="first")

        # Create pigs.
        report_pigs = []
        for _, data_row in dataframe.iterrows():
            error_messages = []
            pig = Pig()

            # Set id.
            id = data_row.get("ID")
            if pd.isna(id):
                error_messages.append("耳號不可為空")
            else:
                try:
                    id = str(id)
                    new_id = self.__remove_dash_from_id(id)
                    if new_id == id:
                        pig.set_id(id)
                    elif ask(f"是否可以將耳號 {id} 修改為 {new_id}？Y:是，N:否"):
                        pig.set_id(new_id)
                    else:
                        error_messages.append("耳號修改格式錯誤")
                except ValueError:
                    error_messages.append("耳號長度過長")
                except TypeError:
                    error_messages.append("耳號格式錯誤")

            # Set farm
            pig.set_farm(farm)

            # Set birthday
            date = data_row.get("Birthday")
            try:
                if pd.isna(date):
                    raise SyntaxError()
                pig.set_birthday(date)
            except ValueError:
                error_messages.append("生日日期格式錯誤")
            except SyntaxError:
                error_messages.append("生日不可為空")

            # Set gender
            gender = str(data_row.get("Gender"))
            try:
                if not allow_none and pd.isna(gender):
                    raise SyntaxError()
                elif allow_none and pd.isna(gender):
                    raise ZeroDivisionError()
                pig.set_gender(gender)
            except KeyError:
                error_messages.append("性別格式錯誤")
            except SyntaxError:
                error_messages.append("性別不可為空")
            except ZeroDivisionError:
                pass # Skip

            # Set breed
            breed: str = data_row.get("Breed")
            try:
                if not allow_none and pd.isna(breed):
                    raise SyntaxError()
                elif allow_none and pd.isna(breed):
                    raise ZeroDivisionError()
                breed.capitalize()
                pig.set_breed(breed)
            except ValueError:
                error_messages.append("品種未定義")
            except SyntaxError:
                error_messages.append("品種不可為空")
            except ZeroDivisionError:
                pass # Skip

            # Set reg id
            reg_id = data_row.get("reg_id")
            if pd.notna(reg_id) and reg_id != "無登":
                try:
                    reg_id = str(reg_id)
                    if len(self.model.find_pigs(equal={"reg_id":reg_id})) > 0:
                        raise KeyError()
                    pig.set_reg_id(reg_id)
                except ValueError:
                    error_messages.append("登錄號格式錯誤")
                except KeyError:
                    error_messages.append("登錄號重複")
                except TypeError:
                    error_messages.append("登錄號格式錯誤")

            # Set Chinese name
            chinese_name = data_row.get("Chinese_name")
            if not pd.isna(chinese_name):
                try:
                    pig.set_chinese_name(chinese_name)
                except ValueError:
                    error_messages.append("中文名長度過長")

            # Set sire
            sire = Pig()
            sire_id = data_row.get("Sire")
            try:
                if not allow_none and pd.isna(sire_id):
                    raise SyntaxError()
                elif allow_none and pd.isna(sire_id):
                    raise ZeroDivisionError() #Skip
                sire_breed = sire_id[0].capitalize()
                sire.set_breed(sire_breed)
                sire_id = self.__remove_dash_from_id(sire_id)
                sire.set_id(sire_id)
                smaller = {} if pig.get_birthday() is None else {"birthday": pig.get_birthday()}
                found = self.model.find_pigs(
                    equal={
                        "id": sire.get_id(), 
                        "breed": sire.get_breed(), 
                        "gender": "M"
                    }, 
                    smaller=smaller
                )
                if len(found) == 0:
                    raise KeyError
                if len(found) == 1:
                    pig.set_sire(found[0])
                else:
                    choice = ask_multiple("找到多隻可能的父畜，請選擇其中之一", found)
                    if choice is None:
                        raise KeyError()
                    pig.set_sire(found[choice])
            except SyntaxError:
                error_messages.append("父畜不能為空")
            except ValueError:
                error_messages.append("父畜品種未定義或耳號格式錯誤")
            except KeyError:
                error_messages.append("資料庫中沒有父畜的資料")
            except ZeroDivisionError:
                pass

            # Set dam
            dam = Pig()
            dam_id = data_row.get("Dam")
            try:
                if not allow_none and pd.isna(dam_id):
                    raise SyntaxError()
                elif allow_none and pd.isna(dam_id):
                    raise ZeroDivisionError() #Skip
                dam_breed = dam_id[0].capitalize()
                dam.set_breed(dam_breed)
                dam_id = self.__remove_dash_from_id(dam_id)
                dam.set_id(dam_id)
                smaller = {} if pig.get_birthday() is None else {"birthday": pig.get_birthday()}
                found = self.model.find_pigs(
                    equal={
                        "id": dam.get_id(), 
                        "breed": dam.get_breed(), 
                        "gender": "F"
                    }, 
                    smaller=smaller
                )
                if len(found) == 0:
                    raise KeyError
                if len(found) == 1:
                    pig.set_dam(found[0])
                else:
                    choice = ask_multiple("找到多隻可能的母畜，請選擇其中之一", found)
                    if choice is None:
                        raise KeyError()
                    pig.set_dam(found[choice])
            except SyntaxError:
                error_messages.append("母畜不能為空")
            except ValueError:
                error_messages.append("母畜品種未定義或耳號格式錯誤")
            except KeyError:
                error_messages.append("資料庫中沒有母畜的資料")
            except ZeroDivisionError:
                pass

            # If error then put into report.
            if len(error_messages) > 0:
                data_dict = data_row.to_dict()
                data_dict["錯誤訊息"] = " ".join(error_messages)
                report_pigs.append(data_dict)
                continue

            # Check duplicate.
            found = self.model.find_pig(pig)
            if found is None:
                self.model.insert_pig(pig)
            if found == pig:
                continue
            msg = "遇到重複豬隻，是否更新資料？Y：更新，N：不更新"
            msg += f"\n讀到的豬：{pig}"
            msg += f"\n已有的豬：{found}"
            if not ask(msg):
                data_dict = data_row.to_dict()
                data_dict["錯誤訊息"] = "豬隻已存在於資料庫且與資料庫中數據不相符"
                report_pigs.append(data_dict)
                continue
            self.model.update_pig(pig)

        report_dataframe = pd.DataFrame(report_pigs)
        report_dataframe.rename(columns={
            "Breed": "品種", 
            "ID": "耳號", 
            "Birthday": "生日", 
            "Sire": "父畜", 
            "Dam": "母畜", 
            "reg_id": "登錄號", 
            "Chinese_name": "中文名", 
            "Gender": "性別"
        })
        report_dataframe.to_csv(os.path.join(output_path, output_filename))

    def read_and_insert_estrus(
        self, 
        farm: str,
        input_path: str = None, 
        dataframe: pd.DataFrame = None,
        output_path: str = os.path.curdir, 
        output_filename: str = "output.csv",
        allow_none: bool = False
    ) -> None:
        """Read estrus data in the source excel or dataframe, insert them into 
        database and create a report csv containing error data.

        Choose reading from excel or dataframe by pathing corresponding 
        parameter

        If read from excel, "配種資料" sheet will be used.

        The source excel or dataframe must have below columns:
        1. 生日年品種耳號
        2. 胎次
        3. 配種日期
        4. 配種時間

        Estrus datetime and parity is checked.

        :param farm: current farm.
        :param input_path: path of the source csv, including filename.
        :param dataframe: the source dataframe.
        :param output_path: path to save the report.
        :param output_filename: name of the report.
        :param allow_none: allow empty non-primary key. 
        :raises: ValueError, FileNotFoundError, TypeError, KeyError.
        """
        # Type check.
        if input_path is None and dataframe is None:
            msg = "You must choose to read from an excel file or a dataframe."
            logging.error(msg)
            raise ValueError(msg)
        
        if input_path is not None:
            type_check(input_path, "input_path", str)
            if not os.path.isfile(input_path):
                msg = f"File {input_path} does not exist."
                logging.error(msg)
                raise FileNotFoundError(msg)
            dataframe = pd.read_excel(io=input_path, sheet_name="基本資料")

        if dataframe is not None:
            type_check(dataframe, "dataframe", pd.DataFrame)
        
        type_check(farm, "farm", str)
        type_check(output_path, "output_path", str)
        type_check(output_filename, "output_filename", str)

        # Standardize the dataframe.
        dataframe.dropna(how="all", inplace=True)
        dataframe = dataframe.rename(columns={
            "生日年品種耳號": "ID", 
            "胎次": "Parity", 
            "配種日期": "Estrus_date",
            "配種時間": "Estrus_time"
        })
        required_columns = [
            "ID", 
            "Parity", 
            "Estrus_date", 
            "Estrus_time"
        ]
        if not set(required_columns).issubset(dataframe.columns):
            msg = "Missing key(s) in source excel or DataFrame."
            logging.error(msg)
            raise KeyError(msg)
        dataframe = dataframe.astype("object")
        dataframe.sort_values(by="Estrus_date", inplace=True, na_position="first")

        # Create estrus.
        report_estrus = []
        for _, data_row in dataframe.iterrows():
            error_messages = []
            estrus = Estrus()

            # Set pig.
            id = data_row.get("ID")
            try:
                if pd.isna(id):
                    raise SyntaxError()
                id = str(id)
                # id in excel may contain birth_year, breed and id.
                birth_year, breed, id = self.__seperate_year_breed_id(id)
                equal = {"id": id, "farm": farm, "gender": "F"}
                larger = {}
                smaller = {}
                if birth_year is not None and breed is not None:
                    larger["birthday"] = f"{birth_year}-01-01"
                    smaller["birthday"] = f"{birth_year}-12-31"
                    equal["breed"] = breed
                pigs = self.model.find_pigs(
                    equal=equal, 
                    smaller_equal=smaller,
                    larger_equal=larger, 
                    order_by="birthday DESC"
                )
                if len(pigs) == 0:
                    raise KeyError()
                estrus.set_sow(pigs[0])
            except SyntaxError:
                error_messages.append("耳號不可為空")
            except ValueError:
                error_messages.append("耳號格式錯誤")
            except TypeError:
                error_messages.append("耳號格式錯誤")
            except KeyError:
                error_messages.append("資料庫中無母豬資料")

    def read_and_insert_matings(
        self, 
        input_path: str = None, 
        dataframe: pd.DataFrame = None,
        output_path: str = os.path.curdir,
        output_filename: str = "output.csv"
    ):
        pass

