# Some frequently used functions.

import datetime


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
    choice_string = choice_string + str(len(choices)) + ". Non of above.\nChoose: "

    choice = None
    while choice not in range(len(choices) + 1):
        print(message)
        choice = input(choice_string)
        if choice.isnumeric():
            choice = int(choice)

    if choice == len(choices):
        return None
    return choice


def transform_date(date) -> datetime.date:
    ''' 
    Transform ISO string to datetime.date.
    * Raise TypeError and ValueError
    '''

    if isinstance(date, datetime.date):
        return date

    if not isinstance(date, str):
        raise TypeError("Need a string but get a {type_}".format(type_=type(date)))

    try:
        return datetime.date.fromisoformat(date)
    except:
        raise ValueError("date {date} is not in ISO format".format(date=date))