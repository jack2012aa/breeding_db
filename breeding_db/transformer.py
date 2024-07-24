"""Transform farm excel to standard form."""
__all__ = [
    "transform_dongying", 
    "transform_chengang", 
    "transform_dongting_pigs"
]

import os
import logging
from datetime import datetime, date

import pandas as pd

from breeding_db.general import type_check


def check_path(input_path: str, output_path: str):

    if not os.path.isfile(input_path):
        msg = f"File '{input_path}' not found."
        logging.error(msg)
        raise FileNotFoundError(msg)
    
    if not os.path.isdir(output_path):
        msg = f"Path {output_path} doesn't exist."
        logging.error(msg)
        raise IsADirectoryError(msg)


def change_column_name_and_type(
        dataframe: pd.DataFrame, 
        rename_dict: dict[str, str], 
        retype_dict: dict[str, type], 
        how: str = "coerce"
    ) -> pd.DataFrame:

    if not set(rename_dict.keys()).issubset(dataframe.columns):
        msg = "Missing key(s) in source excel.\n"
        msg += f"Miss {set(rename_dict.keys()) - set(dataframe.columns)}"
        logging.error(msg)
        raise KeyError(msg)

    for column_name, column_type in retype_dict.items():
        if column_type is date or column_type is datetime:
            dataframe[column_name] = pd.to_datetime(
                dataframe[column_name], errors=how)
        elif column_type is int:
            dataframe[column_name] = pd.to_numeric(
                dataframe[column_name], errors=how, downcast="integer")
        elif column_type is float:
            dataframe[column_name] = pd.to_numeric(
                dataframe[column_name], errors=how, downcast="float")
        else:
            dataframe[column_name] = dataframe[column_name].fillna("").astype(str)

    dataframe = dataframe.rename(columns=rename_dict)
    return dataframe


def transform_dongying(
        input_path: str, 
        output_path: str, 
        output_filename: str, 
    ):
    """Transform 東盈配種組表格 to Estrus, Mating, and Farrowing excel file.
    
    :param input_path: the path of input excel, including the file name.
    :param output_path: the path of output excel, excluding the file name.
    :param output_filename: the name of the output excel.
    :raises TypeError: if intput_path or output_path is not a string.
    :raises FileNotFoundError: if input_path doesn't exist.
    :raises IsADirectoryError: if output_path doesn't exist.
    """

    type_check(input_path, "input_path", str)
    type_check(output_path, "output_path", str)
    type_check(output_filename, "output_filename", str)

    check_path(input_path, output_path)
    
    dataframe = pd.read_excel(input_path, "LY母豬")
    dataframe.dropna(how = 'all', inplace = True)
    rename_dict = {
        "狀態": "status1", 
        "配種日期": "estrus_date",
        "母畜品種": "sow_breed", 
        "母豬耳號": "sow_id", 
        "父畜品種": "boar_breed",
        "予配公豬": "boar_id",
        "胎齡": "parity", 
        "事發狀況": "status2", 
        "狀況日期": "farrowing_date", 
        "♂": "n_of_male", 
        "♀": "n_of_female", 
        "BD": "born_dead"
    }
    retype_dict = {
        "狀態": str, 
        "配種日期": date,
        "母畜品種": str, 
        "母豬耳號": str, 
        "父畜品種": str,
        "予配公豬": str,
        "胎齡": int, 
        "事發狀況": str, 
        "狀況日期": date, 
        "♂": int, 
        "♀": int, 
        "BD": int
    }
    dataframe = change_column_name_and_type(dataframe, rename_dict, retype_dict)

    estrus_dict = {
        "生日年品種耳號": [], 
        "胎次": [], 
        "發情日期": [], 
        "發情時間": [], 
        "21天測孕": [], 
        "60天測孕": []
    }
    mating_dict = {
        "生日年品種耳號": [],
        "與配公豬": [],
        "配種日期": [],
        "配種時間": []
    }
    farrowing_dict = {
        "生日年品種耳號": [], 
        "分娩日期": [],
        "(公) 小豬": [], 
        "(母) 小豬": [], 
        "壓": [],
        "黑": [],
        "弱": [], 
        "畸": [], 
        "死": [], 
        "胎號": []
    }
    
    for _, data in dataframe.iterrows():

        if pd.isna(data.get("sow_breed")) or pd.isna(data.get("sow_id")):
            sow_breed_id = ""
        elif data.get("sow_breed") == "" or data.get("sow_id") == "":
            sow_breed_id = ""
        else:
            sow_breed_id = data.get("sow_breed") + data.get("sow_id")

        parity = data.get("parity")

        if pd.isna(data.get("estrus_date")):
            estrus_date = None
        else:
            estrus_date = data.get("estrus_date").date()

        test_21 = ""
        test_60 = ""

        if "死亡" in data.get("status1"):
            # Useless data.
            continue

        if "流產" in data.get("status1"):
            test_60 = "x"

        if "未配上" in data.get("status2"):
            test_21 = "x"

        if "重發" in data.get("status2"):
            test_21 = "x"

        if sow_breed_id == "":
            continue
        estrus_dict["生日年品種耳號"].append(sow_breed_id)
        estrus_dict["發情日期"].append(estrus_date)
        estrus_dict["發情時間"].append("10:00:00")
        estrus_dict["胎次"].append(parity)
        estrus_dict["21天測孕"].append(test_21)
        estrus_dict["60天測孕"].append(test_60)

        if pd.isna(data.get("boar_id")) or pd.isna(data.get("boar_breed")):
            boar_breed_id = ""
        elif data.get("boar_id") == "" or data.get("boar_breed") == "":
            boar_breed_id = ""
        else:
            boar_breed_id = data.get("boar_breed") + data.get("boar_id")
        mating_dict["生日年品種耳號"].append(sow_breed_id)
        mating_dict["與配公豬"].append(boar_breed_id)
        mating_dict["配種日期"].append(estrus_date)
        mating_dict["配種時間"].append("10:00:00")

        if test_21 == "x" or test_60 == "x":
            continue
        
        if not pd.isna(data.get("farrowing_date")):
            farrowing_date = data.get("farrowing_date").date()
        else:
            farrowing_date = None
            
        n_of_male = data.get("n_of_male")
        n_of_female = data.get("n_of_female")
        dead = data.get("born_dead")
        if pd.isna(n_of_male):
            n_of_male = 0
        if pd.isna(n_of_female):
            n_of_female = 0
        if pd.isna(dead):
            dead = 0
        farrowing_dict["生日年品種耳號"].append(sow_breed_id)
        farrowing_dict["分娩日期"].append(farrowing_date)
        farrowing_dict["胎號"].append(None)
        farrowing_dict["(公) 小豬"].append(n_of_male)
        farrowing_dict["(母) 小豬"].append(n_of_female)
        farrowing_dict["死"].append(dead)
        farrowing_dict["壓"].append(0)
        farrowing_dict["弱"].append(0)
        farrowing_dict["畸"].append(0)
        farrowing_dict["黑"].append(0)

    estrus_frame = pd.DataFrame(estrus_dict)
    mating_frame = pd.DataFrame(mating_dict)
    farrowing_frame = pd.DataFrame(farrowing_dict)

    with pd.ExcelWriter(os.path.join(output_path, output_filename)) as writer:
        estrus_frame.fillna("").to_excel(writer, "發情資料", index=False)
        mating_frame.fillna("").to_excel(writer, "配種資料", index=False)
        farrowing_frame.fillna("").to_excel(writer, "分娩資料", index=False)


def transform_chengang(
        input_path: str, 
        output_path: str, 
        output_filename: str, 
    ):
    """Transform 正綱_批次分娩紀錄 to Estrus, Mating, Farrowing and Weaning excel file.
    
    :param input_path: the path of input excel, including the file name.
    :param output_path: the path of output excel, excluding the file name.
    :param output_filename: the name of the output excel.
    :raises TypeError: if intput_path or output_path is not a string.
    :raises FileNotFoundError: if input_path doesn't exist.
    :raises IsADirectoryError: if output_path doesn't exist.
    """

    type_check(input_path, "input_path", str)
    type_check(output_path, "output_path", str)
    type_check(output_filename, "output_filename", str)

    check_path(input_path, output_path)

    sheets = pd.ExcelFile(input_path).sheet_names
    sheets = [sheet for sheet in sheets if sheet.lower() != "template"]
    
    left_rename_dict = {
        "耳號": "sow_id", 
        "胎次": "parity",
        "配種日": "estrus_date", 
        "生產日": "farrowing_date", 
        "活仔": "born_alive", 
        "黑仔": "black", 
        "死仔": "dead",
        "畸形": "malformation", 
        "弱仔": "weak", 
        "壓死": "crushed", 
        "活母": "n_of_female", 
        "公豬耳號": "boar_id", 
        "離乳日": "weaning_date",
        "哺數": "total_nursed_piglets",
        "頭數": "total_weaning_piglets"
    }
    left_retype_dict = {
        "耳號": str, 
        "胎次": int,
        "配種日": date, 
        "生產日": date, 
        "活仔": int, 
        "死仔": str, 
        "黑仔": str, 
        "畸形": str, 
        "弱仔": str, 
        "壓死": str, 
        "活母": int, 
        "公豬耳號": str, 
        "離乳日": date, 
        "哺數": int, 
        "頭數": int
    }

    estrus_dict = {
        "生日年品種耳號": [], 
        "胎次": [], 
        "發情日期": [], 
        "發情時間": [], 
        "21天測孕": [], 
        "60天測孕": []
    }
    mating_dict = {
        "生日年品種耳號": [],
        "與配公豬": [],
        "配種日期": [],
        "配種時間": []
    }
    farrowing_dict = {
        "生日年品種耳號": [], 
        "分娩日期": [],
        "(公) 小豬": [], 
        "(母) 小豬": [], 
        "壓": [],
        "黑": [],
        "弱": [], 
        "畸": [], 
        "死": [], 
        "胎號": []
    }       
    weaning_dict = {
        "生日年品種耳號": [], 
        "離乳日期": [], 
        "哺乳數": [],
        "離乳數": []
    } 


    for sheet in sheets:
        # Seperate left and right of the sheet.
        dataframe = pd.read_excel(input_path, sheet, header=2)
        dataframe = dataframe.iloc[:, :23].dropna(how="all")
        end = dataframe[dataframe.iloc[:, 0] == '合計'].index[0]
        dataframe = dataframe.iloc[:end]

        dataframe = change_column_name_and_type(
            dataframe, left_rename_dict, left_retype_dict, "ignore")

        def get_valid_int(num: str) -> int:
            
            if num == "":
                return 0
            
            result = ""
            for c in num:
                if not c.isalpha():
                    result += c
            return int(float(result))

        def manufect_data(data):

            sow_id = data.get("sow_id")
            if pd.isna(data.get("estrus_date")):
                estrus_date = None
            else:
                estrus_date = data.get("estrus_date").date()

            if pd.isna(data.get("farrowing_date")):
                farrowing_date = None
            else:
                farrowing_date = data.get("farrowing_date").date()

            if estrus_date is not None and farrowing_date is not None:
                if estrus_date > farrowing_date:
                    # Minus one year.
                    estrus_date = date(
                        estrus_date.year - 1, estrus_date.month, estrus_date.day)

            estrus_dict["生日年品種耳號"].append(sow_id)
            estrus_dict["發情日期"].append(estrus_date)
            estrus_dict["發情時間"].append("10:00:00")
            estrus_dict["胎次"].append(data.get("parity"))
            estrus_dict["21天測孕"].append(None)
            estrus_dict["60天測孕"].append(None)

            mating_dict["生日年品種耳號"].append(sow_id)
            mating_dict["與配公豬"].append(data.get("boar_id"))
            mating_dict["配種日期"].append(estrus_date)
            mating_dict["配種時間"].append("10:00:00")

            farrowing_dict["生日年品種耳號"].append(sow_id)
            farrowing_dict["分娩日期"].append(farrowing_date)
            farrowing_dict["壓"].append(get_valid_int(data.get("crushed")))
            farrowing_dict["黑"].append(get_valid_int(data.get("black")))
            farrowing_dict["死"].append(get_valid_int(data.get("dead")))
            farrowing_dict["畸"].append(get_valid_int(data.get("malformation")))
            farrowing_dict["弱"].append(get_valid_int(data.get("weak")))
            farrowing_dict["胎號"].append(None)
            farrowing_dict["(公) 小豬"].append(data.get("born_alive") - data.get("n_of_female"))
            farrowing_dict["(母) 小豬"].append(data.get("n_of_female"))

            if pd.isna(data.get("weaning_date")):
                weaning_date = None
            else:
                weaning_date = data.get("weaning_date").date()
            weaning_dict["生日年品種耳號"].append(sow_id)
            weaning_dict["離乳日期"].append(weaning_date)
            weaning_dict["離乳數"].append(data.get("total_weaning_piglets"))
            # Fillin when reading right datarame.
            weaning_dict["哺乳數"].append(data.get("total_nursed_piglets"))

        for _, data in dataframe.iterrows():
            manufect_data(data)

    estrus_frame = pd.DataFrame(estrus_dict)
    mating_frame = pd.DataFrame(mating_dict)
    farrowing_frame = pd.DataFrame(farrowing_dict)
    weaning_frame = pd.DataFrame(weaning_dict)

    with pd.ExcelWriter(os.path.join(output_path, output_filename)) as writer:
        estrus_frame.fillna("").to_excel(writer, "發情資料", index=False)
        mating_frame.fillna("").to_excel(writer, "配種資料", index=False)
        farrowing_frame.fillna("").to_excel(writer, "分娩資料", index=False)
        weaning_frame.fillna("").to_excel(writer, "離乳資料", index=False)


def transform_dongting_pigs(
        input_path: str, 
        output_path: str, 
        output_filename: str, 
    ):
    """Transform 東盈母豬胎號 to Pig excel file.
    
    :param input_path: the path of input excel, including the file name.
    :param output_path: the path of output excel, excluding the file name.
    :param output_filename: the name of the output excel.
    :raises TypeError: if intput_path or output_path is not a string.
    :raises FileNotFoundError: if input_path doesn't exist.
    :raises IsADirectoryError: if output_path doesn't exist.
    """

    type_check(input_path, "input_path", str)
    type_check(output_path, "output_path", str)
    type_check(output_filename, "output_filename", str)

    check_path(input_path, output_path)
    
    dataframe = pd.read_excel(input_path).iloc[:, :13]
    dataframe.dropna(how = 'all', inplace = True)
    rename_dict = {
        "品種": "breed",
        "胎號": "litter_id", 
        "生日": "birthday", 
        "父畜": "sire", 
        "母畜": "dam", 
        "公": "n_of_male", 
        "母": "n_of_female", 
        "胎次": "litter"
    }
    retype_dict = {
        "品種": str,
        "胎號": str, 
        "生日": date, 
        "父畜": str, 
        "母畜": str, 
        "公": int, 
        "母": int, 
        "胎次": int
    }
    dataframe = change_column_name_and_type(
        dataframe, rename_dict, retype_dict)

    pig_dict = {
        "品種": [], 
        "耳號": [], 
        "生日": [],
        "父畜": [],
        "母畜": [],
        "性別": [], 
        "出生胎次": [], 
        "登錄號": [], 
        "中文名": []
    }   

    for _, data in dataframe.iterrows():
        breed = data.get("breed")
        if pd.isna(data.get("litter_id")):
            continue
        litter_id = data.get("litter_id")
        if not pd.isna(data.get("birthday")):
            birthday = data.get("birthday").date()
        else:
            birthday = None
        dam = data.get("dam")
        sire = data.get("sire")
        litter = data.get("litter")
        if pd.isna(data.get("n_of_male")):
            n_of_male = 0
        else:
            n_of_male = int(data.get("n_of_male"))
        if pd.isna(data.get("n_of_female")):
            n_of_female = 0
        else:
            n_of_female = int(data.get("n_of_female"))

        for i in range(n_of_male):
            pig_dict["出生胎次"].append(litter)
            pig_dict["品種"].append(breed)
            pig_dict["性別"].append(1)
            pig_dict["母畜"].append(dam)
            pig_dict["父畜"].append(sire)
            pig_dict["生日"].append(birthday)
            pig_dict["耳號"].append(f"{litter_id}-{i + 1}")
            pig_dict["登錄號"].append(None)
            pig_dict["中文名"].append(None)
        for i in range(n_of_female):
            pig_dict["出生胎次"].append(litter)
            pig_dict["品種"].append(breed)
            pig_dict["性別"].append(2)
            pig_dict["母畜"].append(dam)
            pig_dict["父畜"].append(sire)
            pig_dict["生日"].append(birthday)
            pig_dict["耳號"].append(f"{litter_id}-{i + n_of_male + 1}")
            pig_dict["登錄號"].append(None)
            pig_dict["中文名"].append(None)

    pig_frame = pd.DataFrame(pig_dict)

    with pd.ExcelWriter(os.path.join(output_path, output_filename)) as writer:
        pig_frame.fillna("").to_excel(writer, "基本資料", index=False)