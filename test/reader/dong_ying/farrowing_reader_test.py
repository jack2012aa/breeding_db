import unittest

from reader.dong_ying.estrus_and_mating_reader import DongYingEstrusAndMatingReader
from reader.dong_ying.pig_reader import DongYingPigReader
from reader.dong_ying.dong_ying_reader import DongYingFarrowingReader
from models.estrus_model import EstrusModel

class ReaderTest(unittest.TestCase):

    def setUp(self):
        self.reader = DongYingFarrowingReader("./test/reader/dong_ying/farrowing.xlsx")
        self.model = EstrusModel()

    def tearDown(self):
        self.reader = None
        self.model.delete_all("Pigs")
        self.model.delete_all("Estrus")
        self.model.delete_all("Matings")
        self.model.delete_all("Farrowings")
        self.model = None

    def test_reader(self):
        print(self.reader.df.head(10))

    def test_correctly_read(self):

        reader = DongYingPigReader("./test/reader/dong_ying/pig.xlsx")
        reader.create_pigs(ignore_parent=True, update=True)
        reader = DongYingEstrusAndMatingReader("./test/reader/dong_ying/mating.xlsx")
        reader.create_estrus_and_mating()
        self.reader.create_farrowings()
        
        input("STOP")


if __name__ == '__main__':
    unittest.main()