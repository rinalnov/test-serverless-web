import unittest
from src.usermodel import Usermodel

class UsermodelTest(unittest.TestCase):
    def test_fail_addition(self):
        # Make test fail
        self.assertNotEqual(Usermodel.addition(3, 4), 8)
    
    def test_correct_addition(self):
        # Make test fail
        self.assertEqual(Usermodel.addition(5, 10), 15)

    