import logging

from breeding_db.general import ask_multiple
from breeding_db.reader import *
from breeding_db.transformer import *

logging.basicConfig(
    filename="db.log", 
    encoding="utf-8",
    level=logging.INFO, 
    format="%(asctime)s, %(levelname)s, %(filename)s, %(funcName)s, %(message)s", 
    datefmt="%Y-%m-%d %H:%M:%S"
)

work = ask_multiple("請問要使用哪個功能？", [
    "轉換資料表", 
    "讀取資料表"
])

farm = ask_multiple("請問所在牧場？", [
    "東盈", 
    "正綱"
])
farm_name = {0: "Dong-Ying", 1: "Chen-Gang"}[farm]

input_path = input("請輸入目標文件完整目錄，文件夾請使用正斜線(/)：")
output_path = input("請輸入欲儲存輸出文件的目錄，文件夾請使用正斜線(/)：")
output_filename = input("請輸入欲輸出文件之名稱，轉換資料表將輸出xlsx，讀取資料表將輸出csv：")

try:
    if work == 0 and farm == 0:
        transform_dongying(
            input_path=input_path, 
            output_path=output_path, 
            output_filename=output_filename
        )
    elif work == 0 and farm == 1:
        transform_chengang(
            input_path=input_path, 
            output_path=output_path, 
            output_filename=output_filename
        )
    elif work == 1:
        read = ask_multiple("請問是要讀取下列何者？", ["基本資料", "發情資料", "配種資料", "分娩資料", "離乳資料", "小豬出生資料"])
        allow_none = ask("是否允許空值？")
        reader =ExcelReader("test/helper/database_settings.json")
        if read == 0:
            reader.read_and_insert_pigs(
                farm=farm_name, 
                input_path=input_path, 
                output_path=output_path, 
                output_filename=output_filename,
                allow_none=allow_none
            )
        elif read == 1:
            reader.read_and_insert_estrus(
                farm=farm_name, 
                input_path=input_path, 
                output_path=output_path, 
                output_filename=output_filename,
                allow_none=allow_none
            )
        elif read == 2:
            reader.read_and_insert_matings(
                farm=farm_name, 
                input_path=input_path, 
                output_path=output_path, 
                output_filename=output_filename,
                allow_none=allow_none
            )
        elif read == 3:
            reader.read_and_insert_farrowings(
                farm=farm_name, 
                input_path=input_path, 
                output_path=output_path, 
                output_filename=output_filename,
                allow_none=allow_none
            )
        elif read == 4:
            reader.read_and_insert_weanings(
                farm=farm_name, 
                input_path=input_path, 
                output_path=output_path, 
                output_filename=output_filename,
                allow_none=allow_none
            )
        elif read == 5:
            reader.read_and_insert_individuals(
                farm=farm_name, 
                input_path=input_path, 
                output_path=output_path, 
                output_filename=output_filename,
                allow_none=allow_none
            )
    input("工作完成，按下隨機鍵後退出")
except Exception as e:
    print(e)
    input("發生錯誤，按下隨機鍵後退出")