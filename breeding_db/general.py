""" Define general functions. """

__all__ = [
    "add_with_none", 
    "ask", 
    "ask_multiple", 
    "transform_date", 
    "type_check", 
    "delete_contents"
]

import os
import shutil
import logging
from datetime import date


def add_with_none(*args: int | float | None):
    """Add up args, which may contain None.

    :return: sum of args.
    """

    sum = 0
    for arg in args:
        if arg is None:
            continue
        if not isinstance(arg, (int, float)):
            msg = f"arg should be an int or float. Got {type(arg)}."
            logging.error(msg)
            raise TypeError(msg)
        sum += arg
    return sum


def ask(message: str):
    '''
    Ask yes or no.
    Output format: msg *next line* Y/N: 
    '''

    result = ''
    while result not in ['Y','N']:
        result = input(message+'\nY/N: ')
        result = result.upper()
    return result == 'Y'


def ask_multiple(message: str, choices: list):
    '''
    Ask choices.\\
    If non of above, return None.
    '''

    choice_string = ""
    for i in range(len(choices)):
        choice_string = choice_string + str(i) + ". " + str(choices[i]) + "\n"
    choice_string = choice_string + str(len(choices)) + ". None of above.\nChoose: "

    choice = None
    while choice not in range(len(choices) + 1):
        print(message)
        choice = input(choice_string)
        if choice.isnumeric():
            choice = int(choice)

    if choice == len(choices):
        return None
    return choice


def transform_date(date_string: str | date) -> date:
    ''' 
    Transform ISO string to datetime.date.
    * Raise TypeError and ValueError
    '''

    if isinstance(date_string, date):
        return date_string

    type_check(date_string, "date", str)

    try:
        return date.fromisoformat(date_string)
    except:
        msg = f"{date_string} is not in ISO format."
        logging.error(msg)
        raise ValueError(msg)


def type_check(var, var_name: str, correct_type):
    """
    * param var: the incorrect variable
    * param var_name: name of the variable.
    * param correct_type: correct type.
    """

    if not isinstance(var, correct_type):
        msg = f"{var_name} should be a {correct_type.__name__}. Got {type(var).__name__} instead."
        logging.error(msg)
        raise TypeError(msg)
    
def delete_contents(folder_path):
    """删除指定文件夹下的所有内容。
    
    :param folder_path: 文件夹路径
    """
    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        print(f"文件夹 {folder_path} 不存在")
        return
    
    # 遍历文件夹下的所有文件和子文件夹
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            # 如果是文件，删除文件
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            # 如果是文件夹，删除文件夹及其内容
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"删除 {file_path} 时出错: {e}")