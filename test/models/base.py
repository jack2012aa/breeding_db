import unittest
from models import BaseModel

class ModelTest(unittest.TestCase):

    def setUp(self):
        self.model = BaseModel()

    def tearDown(self):
        self.model = None

    def test_connection(self):
        self.model.query("SHOW TABLES;")

if __name__ == '__main__':
    unittest.main()