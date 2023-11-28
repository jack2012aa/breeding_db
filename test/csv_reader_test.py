import unittest
from tools.csv_reader import DongYingCsvReader

class ReaderTest(unittest.TestCase):

    def setUp(self):
        self.reader = DongYingCsvReader("./test/test_basic_data.xlsx")

    def tearDown(self):
        self.reader = None

    def test_reader(self):
        print(self.reader.df.dtypes)
        print(self.reader.df.shape)

    def test_create_pigs(self):
        self.reader.create_pigs()

if __name__ == '__main__':
    unittest.main()