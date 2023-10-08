from data_structure.pig import Pig, PigSettingException

class FactoryException(BaseException):

    def __init__(self, message):
        super().__init__(message)

class PigFactory:

    pig: Pig
    __review_flag: int = 0
    '''
    Show that which field needs to be reviewed.
    1: breed
    2: id
    3. birthday
    '''
    BREED_FLAG = 1
    ID_FLAG = 2
    BIRTHDAY_FLAG = 4

    def __init__(self):
        self.pig = Pig()

    def turn_on_breed_review_flag(self):

        self.__review_flag = self.__review_flag | self.BREED_FLAG

    def turn_on_id_review_flag(self):

        self.__review_flag = self.__review_flag | self.ID_FLAG

    def turn_on_birthday_flag(self):

        self.__review_flag = self.__review_flag | self.BIRTHDAY_FLAG

    def get_flag(self):
        return self.__review_flag

    def ask_change(self, field: str, original: str, changed: str) -> bool:
        '''Ask the user if changing from original to changed is acceptable.'''

        result = ''
        while result not in ['Y','N']:
            result = input('Is the change of ' + str(field) + ' from ' + str(original) + ' to ' + str(changed) + ' acceptable?\nY/N\n')
            result = result.upper()
        return result == 'Y'

    def get_breed_abbrevation(self, breed: str) -> str:
        '''Return the first letter of breed in upper case as the abbrevation of the breed.'''

        return breed.upper()[0]

    def translate_breed_to_english(self, breed: str) -> str:
        '''Return the English of breed'''

        return Pig.BREED_DICT[breed]
    
    def remove_dash_from_id(self, id: str) -> str:
        '''
        * Remove the dash in an id. 
        * Remove none numeric characters.
        * Add additional zero to the later hind of dash.
        * Ex: 1234-2 -> 123402
        * If more than one dash appear in id, only string before the second string will be considered.
        * Ex: 1234-2-2 -> 123402
        * If any character is in the id, only string between first two characters will be considered.
        * Ex: 20Y1234-2cao -> 123402
        '''

        if '-' not in id:
            return id
        
        front, hind = id.split('-')[0], id.split('-')[1]

        '''Remove English character and string before it.'''
        c_index = -1
        for i in range(len(front)):
            if not front[i].isnumeric():
                c_index = i

        result = front[c_index + 1:]

        n_hind = ''
        for c in hind:
            if c.isnumeric():
                n_hind = ''.join([n_hind,c])
            else:
                break
        
        '''Add additional 0.'''
        if len(n_hind) == 1:
            result = ''.join([result, '0', n_hind])
        else:
            result = result + n_hind
        
        return result

    def remove_nonnumeric(self, s: str) -> str:
        '''
        Remove all nonnumeric characters in s.
        '''

        result = ''
        for c in s:
            if c.isnumeric():
                result = ''.join([result,c])
        return result

class DongYingFactory(PigFactory):
    
    def __init__(self):
        super().__init__()

    def set_breed(self, breed: str):
        '''
        1. Does breed in {L, Y, D}?
        2. Is breed an English word?
        3. Is breed in BREED_DICT?
        '''
    
        if type(breed) != str:
            raise FactoryException('Invalid input type. Require str, receive ' + str(type(breed)))
        
        if breed in Pig.BREED:
            self.pig.set_breed(breed)
            return

        '''Chinese string is recognized as alpha in the isalpha method.'''        
        if breed.encode('UTF-8').isalpha():
            n_breed = self.get_breed_abbrevation(breed)
            if self.ask_change(breed, breed, n_breed):
                self.pig.set_breed(n_breed)
                return
        
        if breed in Pig.BREED_DICT:
            n_breed = Pig.BREED_DICT[breed]
            if self.ask_change("breed", breed, n_breed):
                self.pig.set_breed(n_breed)
                return
            
        self.turn_on_breed_review_flag()
        
    def set_id(self, id: str):
        '''
        * Can be turn into an int -> valid
        * Contain a dash -> Remove the dash
        * Get the number between first two nonnumeric characters (if any)
        '''


        if type(id) != str and type(id) != int:
            raise FactoryException('Invalid input type. Require str, receive ' + str(type(id)))
        
        id = str(id)
        if id.isnumeric():
            try:
                self.pig.set_id(id)
                return
            except PigSettingException as ex:
                print(ex)
                self.turn_on_id_review_flag()
                return
            
        if '-' in id:
            n_id = self.remove_dash_from_id(id)
        else:
            n_id = self.remove_nonnumeric(id)

        if self.ask_change('ID', id, n_id):
            try:
                self.pig.set_id(n_id)
                return
            except PigSettingException as ex:
                print(ex)
                self.turn_on_breed_review_flag()
                return
        self.turn_on_breed_review_flag()
        return
    
    def set_birthday(self, date):
        '''
        :param date: yyyy/mm/dd or a __date__ object.
        '''

        try:
            self.pig.set_birthday(date)
            return
        except PigSettingException as ex:
            print(ex)
            self.turn_on_birthday_flag()
