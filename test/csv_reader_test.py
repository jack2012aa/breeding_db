import unittest
from tools.csv_reader import CsvReader

class ReaderTest(unittest.TestCase):

    def setUp(self):
        self.reader = CsvReader()

    def tearDown(self):
        self.pig = None

    def test_set_id(self):
        pass