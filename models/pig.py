from data_structures.pig import Pig
from . import BaseModel


class PigModel(BaseModel):

    def exist(self, pig: Pig) -> bool:

        return True
    
    def find_pig(self, pig: Pig) -> Pig:

        pig = Pig()
        pig.set_id('123456')
        pig.set_birthday('2020-02-03')
        return pig