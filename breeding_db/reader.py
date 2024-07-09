"""Read data from excel, create instances, insert them into db and create 
report csv file.
"""
import os
import logging
from datetime import timedelta

import pandas as pd

from breeding_db.general import ask, ask_multiple, type_check
from breeding_db.models import Model
from breeding_db.data_structures import Farrowing
from breeding_db.data_structures import Pig, Estrus, Mating, PregnantStatus


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
        type_check(allow_none, "allow_none", bool)

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
        report_dataframe = report_dataframe.rename(columns={
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
            dataframe = pd.read_excel(
                io=input_path, 
                sheet_name="配種資料"
            )

        if dataframe is not None:
            type_check(dataframe, "dataframe", pd.DataFrame)
        
        type_check(farm, "farm", str)
        type_check(output_path, "output_path", str)
        type_check(output_filename, "output_filename", str)
        type_check(allow_none, "allow_none", bool)

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
                # Use the youngest sow.
                estrus.set_sow(pigs[0])
            except SyntaxError:
                error_messages.append("耳號不可為空")
            except TypeError:
                error_messages.append("耳號格式錯誤")
            except ValueError as e:
                # Distinguish differen ValueError by content.
                if "birthday" in e:
                    error_messages.append("配種日期比資料中的母豬生日早")
                else:
                    # Should not happen since the pig came from database.
                    raise e
            except KeyError:
                error_messages.append("資料庫中無母豬資料")

            # Set estrus datetime.
            date = data_row.get("Estrus_date")
            time = data_row.get("Estrus_time")
            try:
                if pd.isna(date):
                    raise SyntaxError()
                date = pd.to_datetime(date)
                if pd.isna(time):
                    estrus_datetime = f"{date.strftime('%Y-%m-%d')} 10:00:00"
                else:
                    estrus_datetime = f"{date.strftime('%Y-%m-%d')} "
                    estrus_datetime += f"{time.strftime('%H:%M:%S')}"
                estrus.set_estrus_datetime(estrus_datetime)
            except SyntaxError:
                error_messages.append("配種日期不能為空")
            except TypeError:
                error_messages.append("配種日期或配種時間格式錯誤")
            except ValueError as e:
                # Distinguish differen ValueError by content.
                if "birthday" in e.args[0]:
                    error_messages.append("配種日期比資料中的母豬生日早")
                else:
                    error_messages.append("配種日期或配種時間格式錯誤")

            # Set parity.
            parity = data_row.get("Parity")
            try:
                if not allow_none and pd.isna(parity):
                    raise SyntaxError()
                if allow_none and pd.isna(parity):
                    raise ZeroDivisionError()
                # Check parity.
                # Need to find estrus record through primary key.
                # Since missing primary key isn't allowed, just skip this step.
                parity = int(parity)
                if estrus.get_sow() is None:
                    raise ZeroDivisionError()
                if estrus.get_estrus_datetime() is None:
                    raise ZeroDivisionError()
                found = self.model.find_estrus(
                    equal={
                        "id": estrus.get_sow().get_id(), 
                        "birthday": estrus.get_sow().get_birthday(), 
                        "farm": estrus.get_sow().get_farm()
                    }, 
                    smaller={"estrus_datetime": estrus.get_estrus_datetime()}, 
                    order_by="parity DESC"
                )
                if len(found) > 0 and parity < found[0].get_parity():
                    error_messages.append("發情日期比前一胎次發情紀錄的發情日期早")
                    raise ZeroDivisionError()
                found = self.model.find_estrus(
                    equal={
                        "id": estrus.get_sow().get_id(), 
                        "birthday": estrus.get_sow().get_birthday(), 
                        "farm": estrus.get_sow().get_farm()
                    }, 
                    larger={"estrus_datetime": estrus.get_estrus_datetime()}, 
                    order_by="parity ASC"
                )
                if len(found) > 0 and parity > found[0].get_parity():
                    error_messages.append("發情日期比後一胎次發情紀錄的發情日期晚")
                    raise ZeroDivisionError()
                found = self.model.find_estrus(
                    equal={
                        "id": estrus.get_sow().get_id(), 
                        "birthday": estrus.get_sow().get_birthday(), 
                        "farm": estrus.get_sow().get_farm(), 
                        "parity": parity
                    }, 
                    order_by="estrus_datetime DESC"
                )
                if len(found) > 0:
                    dt = estrus.get_estrus_datetime().date() # Shorter
                    found_dt = found[0].get_estrus_datetime().date() # Shorter
                    if dt < found_dt - timedelta(3) or dt > found_dt + timedelta(3):
                        error_messages.append("已經有同一胎次資料且日期距離過長")
                        raise ZeroDivisionError()
                estrus.set_parity(parity)
            except SyntaxError:
                error_messages.append("胎次不可為空")
            except ZeroDivisionError:
                pass # Skip
            except TypeError:
                error_messages.append("胎次格式錯誤")
            except ValueError:
                error_messages.append("胎次超出範圍(1~12)")

            # Set pregnant.
            estrus.set_pregnant(PregnantStatus.UNKNOWN)

            # If error then put into report.
            if len(error_messages) > 0:
                data_dict = data_row.to_dict()
                data_dict["錯誤訊息"] = " ".join(error_messages)
                report_estrus.append(data_dict)
                continue

            # Check duplicate.
            found = self.model.find_estrus(equal={
                "id": estrus.get_sow().get_id(), 
                "birthday": estrus.get_sow().get_birthday(),
                "farm": estrus.get_sow().get_farm(), 
                "estrus_datetime": estrus.get_estrus_datetime()
            })
            if len(found) == 0:
                self.model.insert_estrus(estrus)
                continue
            if found[0] == estrus:
                continue
            dt = estrus.get_estrus_datetime().date() # Shorter
            found_dt = found[0].get_estrus_datetime().date() # Shorter
            if dt - timedelta(3) <= found_dt <= dt:
                # New mating data.
                continue
            msg = "遇到重複發情紀錄，是否更新資料？Y：更新，N：不更新"
            msg += f"\n讀到的發情紀錄：{estrus}"
            msg += f"\n已有的發情紀錄：{found[0]}"
            if not ask(msg):
                data_dict = data_row.to_dict()
                data_dict["錯誤訊息"] = "發情紀錄已存在於資料庫且與資料庫中數據不相符"
                report_estrus.append(data_dict)
                continue
            self.model.update_estrus(estrus)
        
        report_dataframe = pd.DataFrame(report_estrus)
        report_dataframe = report_dataframe.rename(columns={
            "ID": "生日年品種耳號", 
            "Parity": "胎次", 
            "Estrus_date": "配種日期",
            "Estrus_time": "配種時間"
        })
        report_dataframe.to_csv(os.path.join(output_path, output_filename))

    def read_and_insert_matings(
        self, 
        farm: str,
        input_path: str = None, 
        dataframe: pd.DataFrame = None,
        output_path: str = os.path.curdir, 
        output_filename: str = "output.csv",
    ) -> None:
        """Read data from excel or dataframe and insert Mating objects into 
        database.

        Choose to read data from excel or dataframe by passing in 
        corresponding arguments.

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
            dataframe = pd.read_excel(
                io=input_path, 
                sheet_name="配種資料"
            )

        if dataframe is not None:
            type_check(dataframe, "dataframe", pd.DataFrame)
        
        type_check(farm, "farm", str)
        type_check(output_path, "output_path", str)
        type_check(output_filename, "output_filename", str)

        # Standardize the dataframe.
        dataframe.dropna(how="all", inplace=True)
        rename_dict = {
            "生日年品種耳號": "SOW_ID", 
            "胎次": "Parity", 
            "配種日期": "Estrus_date",
            "配種時間": "Estrus_time", 
            "與配公豬": "BOAR_ID", 
            "21天測孕": "21th_day_test", 
            "60天測孕": "60th_day_test"
        }
        dataframe = dataframe.rename(columns=rename_dict)
        if not set(rename_dict.values()).issubset(dataframe.columns):
            msg = "Missing key(s) in source excel or DataFrame."
            logging.error(msg)
            raise KeyError(msg)
        dataframe = dataframe.astype("object")

        # Create matings.
        report_matings = []
        for _, data_row in dataframe.iterrows():
            error_messages = []
            mating = Mating()

            # Set estrus.
            estrus = Estrus()
            sow_id = data_row.get("SOW_ID")
            try:
                if pd.isna(sow_id):
                    raise SyntaxError()
                sow_id = str(sow_id)
                # dam_id in excel may contain birth_year, breed and id.
                birth_year, breed, sow_id = self.__seperate_year_breed_id(sow_id)
                equal = {"id": sow_id, "farm": farm, "gender": "F"}
                larger = {}
                smaller = {}
                if birth_year is not None and breed is not None:
                    larger["birthday"] = f"{birth_year}-01-01"
                    smaller["birthday"] = f"{birth_year}-12-31"
                    equal["breed"] = breed
                found = self.model.find_pigs(
                    equal=equal, 
                    smaller_equal=smaller,
                    larger_equal=larger, 
                    order_by="birthday DESC"
                )
                if len(found) == 0:
                    raise KeyError()
                # Use the youngest sow.
                estrus.set_sow(found[0])
            except SyntaxError:
                error_messages.append("母豬耳號不可為空")
            except TypeError:
                error_messages.append("耳號格式錯誤")
            except ValueError as e:
                # Distinguish differen ValueError by content.
                if "birthday" in e:
                    error_messages.append("配種日期比資料中的母豬生日早")
                else:
                    # Should not happen since the pig came from database.
                    raise e
            except KeyError:
                error_messages.append("資料庫中無母豬資料")

            # Set estrus datetime.
            date = data_row.get("Estrus_date")
            time = data_row.get("Estrus_time")
            try:
                if pd.isna(date):
                    raise SyntaxError()
                date = pd.to_datetime(date)
                if pd.isna(time):
                    estrus_datetime = f"{date.strftime('%Y-%m-%d')} 10:00:00"
                else:
                    estrus_datetime = f"{date.strftime('%Y-%m-%d')} "
                    estrus_datetime += f"{time.strftime('%H:%M:%S')}"
                estrus.set_estrus_datetime(estrus_datetime)
            except SyntaxError:
                error_messages.append("配種日期不能為空")
            except TypeError:
                error_messages.append("配種日期或配種時間格式錯誤")
            except ValueError as e:
                # Distinguish differen ValueError by content.
                if "birthday" in e.args[0]:
                    error_messages.append("配種日期比資料中的母豬生日早")
                else:
                    error_messages.append("配種日期或配種時間格式錯誤")

            if estrus.is_unique():
                equal = {
                    "id": estrus.get_sow().get_id(), 
                    "farm": estrus.get_sow().get_farm(), 
                    "birthday": estrus.get_sow().get_birthday()
                }
                smaller_equal = {
                    "estrus_datetime": estrus.get_estrus_datetime()
                }
                larger_equal = {
                    "estrus_datetime": estrus.get_estrus_datetime() - timedelta(3)
                }
                found = self.model.find_estrus(
                    equal=equal, 
                    smaller_equal=smaller_equal, 
                    larger_equal=larger_equal, 
                    order_by="estrus_datetime DESC"
                )
                if len(found) > 0:
                    try:
                        mating.set_estrus(found[0])
                    except ValueError as e:
                        if "gap between" in e:
                            error_messages.append("配種日期與發情日期間距太長")
                        elif "than estrus datetime" in e:
                            error_messages.append("配種日期早於發情日期")
                        elif "Boar birthday" in e:
                            error_messages.append("公豬生日晚於發情日期")
                        else:
                            error_messages.append("未知錯誤")
                    estrus = found[0]
                else:
                    error_messages.append("資料庫中沒有發情資料")

            # Set boar.
            boar_id = data_row.get("BOAR_ID")
            try:
                if pd.isna(boar_id):
                    raise SyntaxError()
                birth_year, breed, boar_id = self.__seperate_year_breed_id(boar_id)
                equal = {"id": boar_id, "farm": farm, "gender": "M"}
                larger = {}
                smaller = {}
                if birth_year is not None and breed is not None:
                    larger["birthday"] = f"{birth_year}-01-01"
                    smaller["birthday"] = f"{birth_year}-12-31"
                    equal["breed"] = breed
                found = self.model.find_pigs(
                    equal=equal, 
                    smaller_equal=smaller, 
                    larger_equal=larger
                )
                if len(found) == 0:
                    raise KeyError()
                if len(found) == 1:
                    mating.set_boar(found[0])
                    raise ZeroDivisionError()
                chosen = ask_multiple("找到多頭公豬，選擇下列何者？", found)
                if chosen is None:
                    raise KeyError()
                mating.set_boar(found[chosen])
            except SyntaxError:
                error_messages.append("公豬耳號不能為空")
            except KeyError:
                error_messages.append("資料庫無公豬資料")
            except TypeError:
                error_messages.append("公豬耳號格式錯誤")
            except ValueError as e:
                if "estrus date" in e.args[0]:
                    error_messages.append("公豬生日晚於母豬發情日期")
                elif "mating date" in e.args[0]:
                    error_messages.append("公豬生日晚於配種日期")
            except ZeroDivisionError:
                pass

            # Set mating dateteime.
            date = data_row.get("Estrus_date")
            time = data_row.get("Estrus_time")
            try:
                if pd.isna(date):
                    raise SyntaxError()
                date = pd.to_datetime(date)
                if pd.isna(time):
                    mating_datetime = f"{date.strftime('%Y-%m-%d')} 10:00:00"
                else:
                    mating_datetime = f"{date.strftime('%Y-%m-%d')} "
                    mating_datetime += f"{time.strftime('%H:%M:%S')}"
                mating.set_mating_datetime(mating_datetime)
            except SyntaxError:
                error_messages.append("配種日期不能為空")
            except TypeError:
                error_messages.append("配種日期或配種時間格式錯誤")
            except ValueError as e:
                if "gap between" in e.args[0]:
                    error_messages.append("配種日期與發情日其間隔過長")
                elif "than estrus datetime" in e.args[0]:
                    error_messages.append("發情日期晚於配種日期")
                elif "Boar birthday" in e.args[0]:
                    error_messages.append("公豬生日晚於配種日期")
                else:
                    error_messages.append("未知錯誤")

            # Update estrus pregnant status.
            test_21 = data_row.get("21th_day_test")
            test_60 = data_row.get("60th_day_test")
            if str(test_21).lower() == "x":
                estrus.set_pregnant(PregnantStatus.NO)
                self.model.update_estrus(estrus)
            if str(test_60).lower() == "x":
                estrus.set_pregnant(PregnantStatus.ABORTION)
                self.model.update_estrus(estrus)

            if len(error_messages) > 0:
                data_dict = data_row.to_dict()
                data_dict["錯誤訊息"] = " ".join(error_messages)
                report_matings.append(data_dict)
                continue
            
            # Check duplicate.
            found = self.model.find_matings(equal={
                "sow_id": mating.get_estrus().get_sow().get_id(), 
                "sow_birthday": mating.get_estrus().get_sow().get_birthday(), 
                "sow_farm": mating.get_estrus().get_sow().get_farm(), 
                "estrus_datetime": mating.get_estrus().get_estrus_datetime(), 
                "mating_datetime": mating.get_mating_datetime()
            })

            if len(found) == 0:
                self.model.insert_mating(mating)
                continue
            if found[0] == mating:
                continue

            msg = "遇到重複配種紀錄，是否更新資料？Y：更新，N：不更新"
            msg += f"\n讀到的配種紀錄：{mating}"
            msg += f"\n已有的配種紀錄：{found[0]}"
            if not ask(msg):
                data_dict = data_row.to_dict()
                data_dict["錯誤訊息"] = "配種紀錄已存在於資料庫且與資料庫中數據不相符"
                report_matings.append(data_dict)
                continue
            self.model.update_mating(mating)

        report_dataframe = pd.DataFrame(report_matings)
        report_dataframe = report_dataframe.rename(columns={
            "SOW_ID": "生日年品種耳號", 
            "Parity": "胎次", 
            "Estrus_date": "配種日期",
            "Estrus_time": "配種時間", 
            "BOAR_ID": "與配公豬", 
            "21th_day_test": "21天測孕", 
            "60th_day_test": "60天測孕"
        })
        report_dataframe.to_csv(os.path.join(output_path, output_filename))

    def read_and_insert_farrowings(
        self, 
        farm: str,
        input_path: str = None, 
        dataframe: pd.DataFrame = None,
        output_path: str = os.path.curdir, 
        output_filename: str = "output.csv",
        allow_none: bool = False
    ) -> None:
        """Read data from excel or dataframe and insert Farrowing objects 
        into database.

        Choose to read data from excel or dataframe by passing in 
        corresponding arguments.

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
            dataframe = pd.read_excel(
                io=input_path, 
                sheet_name="分娩資料"
            )

        if dataframe is not None:
            type_check(dataframe, "dataframe", pd.DataFrame)
        
        type_check(farm, "farm", str)
        type_check(output_path, "output_path", str)
        type_check(output_filename, "output_filename", str)
        type_check(allow_none, "allow_none", bool)
        
        # Standardize the dataframe.
        dataframe.dropna(how = 'all', inplace = True)
        rename_dict = {
            "生日年品種耳號": "birthyear_breed_id", 
            "分娩日期": "farrowing_date", 
            "(公) 小豬": "n_of_male", 
            "(母) 小豬": "n_of_female", 
            "壓": "crushed", 
            "黑": "black", 
            "弱": "weak", 
            "畸": "malformation", 
            "死": "dead", 
            "出生窩重": "total_weight", 
            "備註": "note"
        }
        dataframe = dataframe.rename(columns=rename_dict)
        if not set(rename_dict.values()).issubset(dataframe.columns):
            msg = "Missing key(s) in source excel or DataFrame."
            logging.error(msg)
            raise KeyError(msg)
        dataframe = dataframe.astype("object")
        
        # Create farrowings.
        report_farrowings = []
        for _, data_row in dataframe.iterrows():
            error_messages = []
            farrowing = Farrowing()
            
            # Set farrowing date first to do qeury in the finding estrus step.
            farrowing_date = data_row.get("farrowing_date")
            try:
                if pd.isna(farrowing_date):
                    raise SyntaxError()
                # pd.Timestamp is a child class of datetime.date 
                # It will confuse general.transform_date(), so do the 
                # transformation here.
                farrowing_date = farrowing_date.date()
                farrowing.set_farrowing_date(farrowing_date)
            except SyntaxError:
                error_messages.append("分娩日期不能為空")
            except TypeError:
                error_messages.append("分娩日期格式錯誤")
            except ValueError as e:
                if "than 140" in e.args[0]:
                    error_messages.append("分娩日期與發情日期間隔過長")
                elif "than 100" in e.args[0]:
                    error_messages.append("分娩日期與發情日期間隔過短")
                else:
                    error_messages.append("分娩日期格式錯誤")

            # Set estrus.
            birthyear_breed_id = data_row.get("birthyear_breed_id")
            try:
                if pd.isna(birthyear_breed_id):
                    raise SyntaxError()
                year, breed, id = self.__seperate_year_breed_id(birthyear_breed_id)
                equal = {"id": id, "farm": farm}
                larger_equal = {}
                smaller_equal = {}
                if year is not None:
                    larger_equal["birthday"] = f"{year}-01-01"
                    smaller_equal["birthday"] = f"{year}-12-31"
                if not pd.isna(farrowing_date):
                    smaller_equal["estrus_datetime"] = f"{farrowing_date} 10:00:00"
                found = self.model.find_estrus(
                    equal=equal, 
                    smaller_equal=smaller_equal, 
                    larger_equal=larger_equal, 
                    order_by="estrus_datetime DESC"
                )
                if len(found) == 0:
                    raise KeyError()
                farrowing.set_estrus(found[0])
            except SyntaxError:
                error_messages.append("耳號不能為空")
            except KeyError:
                error_messages.append("資料庫中無所屬發情資料")

            except ValueError as e:
                if "than 140" in e.args[0]:
                    error_messages.append("分娩日期與發情日期間隔過長")
                elif "than 100" in e.args[0]:
                    error_messages.append("分娩日期與發情日期間隔過短")
                else:
                    error_messages.append("未知錯誤")

            # Set numeric attributes.
            def set_numeric(arg_name, arg_chinese, setting_func):
                arg = data_row.get(arg_name)
                try:
                    if allow_none and pd.isna(arg):
                        raise ZeroDivisionError()
                    if not allow_none and pd.isna(arg):
                        raise SyntaxError()
                    setting_func(int(arg))
                except ZeroDivisionError:
                    pass
                except SyntaxError:
                    error_messages.append(f"{arg_chinese}不能為空")
                except TypeError:
                    error_messages.append(f"{arg_chinese}格式錯誤")
                except ValueError as e:
                    if "invalid literal" in e.args[0]:
                        error_messages.append(f"{arg_chinese}格式錯誤")
                    elif "total born" in e.args[0]:
                        error_messages.append("總出生數超出上限(30)")
                    elif "than 0" in e.args[0]:
                        error_messages.append(f"{arg_chinese}不能低於0")
                    else:
                        error_messages.append("未知錯誤")
            
            set_numeric("crushed", "壓", farrowing.set_crushed)
            set_numeric("black", "黑", farrowing.set_black)
            set_numeric("weak", "弱", farrowing.set_weak)
            set_numeric("malformation", "畸", farrowing.set_malformation)
            set_numeric("dead", "死", farrowing.set_dead)
            set_numeric("n_of_male", "(公)小豬", farrowing.set_n_of_male)
            set_numeric("n_of_female", "(母)小豬", farrowing.set_n_of_female)
            set_numeric("total_weight", "出生窩重", farrowing.set_total_weight)

            note = data_row.get("note")
            try:
                if not pd.isna(note):
                    farrowing.set_note(note)
            except TypeError:
                error_messages.append("備註格式錯誤")

            if len(error_messages) > 0:
                data_dict = data_row.to_dict()
                data_dict["錯誤訊息"] = " ".join(error_messages)
                report_farrowings.append(data_dict)
                continue

            # Update estrus pregnant status.
            estrus = found[0]
            if farrowing.get_born_alive() > 0:
                estrus.set_pregnant(PregnantStatus.YES)
                self.model.update_estrus(estrus)
            
            # Check duplicate
            found = self.model.find_farrowings(equal={
                "id": farrowing.get_estrus().get_sow().get_id(), 
                "farm": farrowing.get_estrus().get_sow().get_farm(), 
                "birthday": farrowing.get_estrus().get_sow().get_birthday(), 
                "estrus_datetime": farrowing.get_estrus().get_estrus_datetime()
            })

            if len(found) == 0:
                self.model.insert_farrowing(farrowing)
                continue
            if found[0] == farrowing:
                continue

            msg = "遇到重複分娩紀錄，是否更新資料？Y：更新，N：不更新"
            msg += f"\n讀到的分娩紀錄：{farrowing}"
            msg += f"\n已有的分娩紀錄：{found[0]}"
            if not ask(msg):
                data_dict = data_row.to_dict()
                data_dict["錯誤訊息"] = "分娩紀錄已存在於資料庫且與資料庫中數據不相符"
                report_farrowings.append(data_dict)
                continue
            self.model.update_farrowing(farrowing)

        report_dataframe = pd.DataFrame(report_farrowings)
        report_dataframe = report_dataframe.rename(columns={
            value: key for key, value in rename_dict.items()
        })
        report_dataframe.to_csv(os.path.join(output_path, output_filename))