"""Transform farm excel to standard form."""
__all__ = [
    "transform_dongying"
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
        retype_dict: dict[str, type]
    ) -> pd.DataFrame:

    for column_name, column_type in retype_dict.items():
        if column_type is date or column_type is datetime:
            dataframe[column_name] = pd.to_datetime(
                dataframe[column_name], errors="coerce")
        elif column_type is int:
            dataframe[column_name] = pd.to_numeric(
                dataframe[column_name], errors="coerce", downcast="integer")
        elif column_type is float:
            dataframe[column_name] = pd.to_numeric(
                dataframe[column_name], errors="coerce", downcast="float")
        else:
            dataframe[column_name] = dataframe[column_name].fillna("").astype(str)

    dataframe = dataframe.rename(columns=rename_dict)
    if not set(rename_dict.values()).issubset(dataframe.columns):
        msg = "Missing key(s) in source excel.\n"
        msg += f"Miss {set(rename_dict.values()) - set(dataframe.columns)}"
        logging.error(msg)
        raise KeyError(msg)
    
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