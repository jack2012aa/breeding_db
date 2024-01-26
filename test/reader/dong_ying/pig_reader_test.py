import unittest

from reader.dong_ying_reader import DongYingPigReader
from models.pig_model import PigModel

class ReaderTest(unittest.TestCase):

    def setUp(self):
        self.model = PigModel()

    def tearDown(self):
        self.model.delete_all("Pigs")
        self.model = None

    # def test_reader(self):
    #     print(self.reader.queue)

    def test_create_pigs(self):
        
        # First set parents.
        reader = DongYingPigReader("./test/reader/dong_ying/parents.xlsx", "parents_output")
        reader.create_pigs(ignore_parent=True)
        self.assertEqual(self.model.query("SELECT COUNT(*) FROM Pigs;")[0]["COUNT(*)"], 187)

        # Then read other pigs.
        reader = DongYingPigReader("./test/reader/dong_ying/pig.xlsx", "pigs_output")
        reader.create_pigs(ignore_parent=False, update=True)
        input("STOP")
        self.assertEqual(self.model.query(
            "SELECT COUNT(*) FROM Pigs where (dam_id is not NULL) or (sire_id is not NULL);"
            )[0]["COUNT(*)"], 18
        )

if __name__ == '__main__':
    unittest.main()