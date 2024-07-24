import unittest

from breeding_db.transformer import *
from breeding_db.general import delete_contents

class MyTestCase(unittest.TestCase): 

    def setUp(self):
        pass

    def tearDown(self):
        delete_contents("test/helper/garbage")

    def test_transform_dongying(self):

        transform_dongying(
            input_path="test/helper/dongying.xlsx", 
            output_path="test/helper/garbage", 
            output_filename="output.xlsx"
        )

    def test_transform_chengang(self):

        transform_chengang(
            input_path="test/helper/chengang.xlsx", 
            output_path="test/helper/garbage", 
            output_filename="output.xlsx"
        )

    def test_transform_dongying_pigs(self):

        transform_dongting_pigs(
            input_path="test/helper/dongying_pigs.xlsx", 
            output_path="test/helper/garbage", 
            output_filename="output.xlsx"
        )
        input("wait")


if __name__ == '__main__':
    unittest.main()