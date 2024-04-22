import unittest
from unittest.mock import MagicMock, patch



class TestScroots(unittest.TestCase):

    def test_0_prog(self):
        self.assertRaises(Scroots.sqroots("1 2 3"), ValueError("No real roots"))

    def test_1_prog(self):
        self.assertEqual(Scroots.sqroots("1 2 1"), "-1.0")

