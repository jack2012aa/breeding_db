import unittest

from reader.dong_ying_reader import DongYingPigReader
from models.pig_model import PigModel

class ReaderTest(unittest.TestCase):

    def setUp(self):
        self.reader = DongYingPigReader("./test/reader/dong_ying_pig_data.xlsx")
        self.model = PigModel()

    def tearDown(self):
        self.reader = None
        self.model.delete_all("Pigs")
        self.model = None

    def test_reader(self):
        print(self.reader.df.dtypes)
        print(self.reader.df.shape)

    def test_create_pigs(self):
        
        # Test ignore parents
        self.reader.create_pigs(True)
        self.assertEqual(self.model.query("SELECT COUNT(*) FROM Pigs;")[0]["COUNT(*)"], 285)
        self.reader = DongYingPigReader("./test/reader/dong_ying_pig_data.xlsx")
        self.reader.create_pigs(ignore_parent=False, update=True)
        self.assertEqual(self.model.query(
            "SELECT COUNT(*) FROM Pigs where (dam_id is not NULL) or (sire_id is not NULL);"
            )[0]["COUNT(*)"], 51
        )

if __name__ == '__main__':
    unittest.main()