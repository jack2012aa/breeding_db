from .pig import Pig

class DongYing_factory:
    
    my_pig:Pig

    def __init__(self):
        self.my_pig = Pig("1234")