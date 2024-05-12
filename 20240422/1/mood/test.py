from unittest import main, TestCase
import moodserver
import multiprocessing
import socket
import time
from asyncio import run
import cowsay


class Test_Server(TestCase):
    def send_recv(s, data):
        s.send(data.encode())
        return s.recv(1024).decode()

    @classmethod
    def setUpClass(cls):
        cls.proc = multiprocessing.Process(target=moodserver.run_serve)
        cls.proc.start()

        time.sleep(2)

    def setUp(self):
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _socket.connect(("localhost", 1338))
        self.s = _socket

    
    def test_1(self):
        self.s.send("milk\n".encode())
        buff = Test_Server.send_recv(self.s, "addmon default hello hi coords 1 1 hp 15\n")
    
        self.assertEqual(buff, "Added monster default to (1, 1) saying hi.")

    def test_2(self):
        self.s.send("milk\n".encode())
        buff = Test_Server.send_recv(self.s, "up\n")
        self.assertEqual(buff, 'Moved to (0, 1)')
        buff = Test_Server.send_recv(self.s, "right\n")
        ans = 'Moved to (1, 1)' + cowsay.cowsay("hi") 
        self.assertEqual(buff, ans)
    
    def test_3(self):
        self.s.send("milk\n".encode())
        Test_Server.send_recv(self.s, "addmon default hello hi coords 0 0 hp 15\n")
        buff = Test_Server.send_recv(self.s, "attack default 10\n")
        self.assertEqual(buff, 'Attacked default, damage 10 hp\ndefault now has 5 hp')



    def tearDown(self):
        self.s.close()

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
