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
        input("wait")



if __name__ == '__main__':
    unittest.main()