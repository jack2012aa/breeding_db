import unittest

from tools.csv_reader import DongYingCsvReader
from models.pig_model import PigModel

class ReaderTest(unittest.TestCase):

    def setUp(self):
        self.reader = DongYingCsvReader("./test/test_basic_data.xlsx")
        self.model = PigModel()

    def tearDown(self):
        self.reader = None
        self.model.query("SET foreign_key_checks = 0;")
        self.model.delete_all()
        self.model.query("SET foreign_key_checks = 1;")
        self.model = None

    def test_reader(self):
        print(self.reader.df.dtypes)
        print(self.reader.df.shape)

    def test_create_pigs(self):
        
        # Test ignore parents
        self.reader.create_pigs(True)
        self.assertEqual(self.model.query("SELECT COUNT(*) FROM Pigs;")[0]["COUNT(*)"], 285)
        self.reader.create_pigs(ignore_parent=False, update=True)
        input("wait")

if __name__ == '__main__':
    unittest.main()