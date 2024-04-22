import unittest
from unittest.mock import MagicMock, patch
import Scroots



class TestScroots(unittest.TestCase):

    def test_0(self):
        self.assertRaises(Scroots.sqroots("1 2 3"), ValueError("No real roots"))

    def test_1(self):
        self.assertEqual(Scroots.sqroots("1 2 1"), "-1.0")


class TestScrootNet(unittest.TestCase):

    def setUp(self):
        self.s = MagicMock()
        self.s.sendall = lambda par: self.__dict__.setdefault("res", Scroots(par))
        self.s.recv = lambda args: self.res


    def test_3(self):
        self.assertEqual(ScrootNet.sqroots("1 2 1"), "-1.0")

