'''
Some frequently used functions.
'''

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