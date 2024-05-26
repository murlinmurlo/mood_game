import unittest
import unittest.mock as mock
import mood.client as client
from io import StringIO


class TestClientCommands(unittest.TestCase):
    def test_5_say_all(self):
        with (
                mock.patch('sys.stdin', StringIO("sayall Hello world!")),
                mock.patch('socket.socket', autospec=True) as socket_mock,
                mock.patch('mood.client.msg_reciever', return_value=True)
             ):
            client.start_client("test")
            sendall_call = socket_mock.mock_calls[4].args[0]
            self.assertEqual(sendall_call, b'sayall Hello world!\n')

    def test_7_move_monsters_off(self):
        with (
                mock.patch('sys.stdin', StringIO("movemonsters off")),
                mock.patch('socket.socket', autospec=True) as socket_mock,
                mock.patch('mood.client.msg_reciever', return_value=True)
             ):
            client.start_client("test")
            sendall_call = socket_mock.mock_calls[4].args[0]
            self.assertEqual(sendall_call, b'movemonsters off\n')

    def test_6_move_monsters_on(self):
        with (
                mock.patch('sys.stdin', StringIO("movemonsters on")),
                mock.patch('socket.socket', autospec=True) as socket_mock,
                mock.patch('mood.client.msg_reciever', return_value=True)
             ):
            client.start_client("test")
            sendall_call = socket_mock.mock_calls[4].args[0]
            self.assertEqual(sendall_call, b'movemonsters on\n')

    def test_8_set_locale(self):
        with (
                mock.patch('sys.stdin', StringIO("locale ru_RU.UTF-8")),
                mock.patch('socket.socket', autospec=True) as socket_mock,
                mock.patch('mood.client.msg_reciever', return_value=True)
             ):
            client.start_client("test")
            sendall_call = socket_mock.mock_calls[4].args[0]
            self.assertEqual(sendall_call, b'locale ru_RU.UTF-8\n')
'''
    def test_9_open_documentation(self):
        with (
                mock.patch('sys.stdin', StringIO("documentation")),
                mock.patch('webbrowser.open', autospec=True) as webbrowser_mock
             ):
            client.start_client("test")
            webbrowser_mock.assert_called_with(client.doc_path)
'''

class TestClientCommandParsing(unittest.TestCase):
    def test_0_move_up(self):
        with (
                mock.patch('sys.stdin', StringIO("up")),
                mock.patch('socket.socket', autospec=True) as socket_mock,
                mock.patch('mood.client.msg_reciever', return_value=True)
             ):
            client.start_client("test")
            sendall_call = socket_mock.mock_calls[4].args[0]
            self.assertEqual(sendall_call, b'move 0 -1\n')

    def test_1_move_down(self):
        with (
                mock.patch('sys.stdin', StringIO("down")),
                mock.patch('socket.socket', autospec=True) as socket_mock,
                mock.patch('mood.client.msg_reciever', return_value=True)
             ):
            client.start_client("test")
            sendall_call = socket_mock.mock_calls[4].args[0]
            self.assertEqual(sendall_call, b'move 0 1\n')

    def test_2_attack_default(self):
        command = "addmon kitty coords 0 1 hello eww hp 10\ndown\nattack kitty"
        with (
                mock.patch('sys.stdin', StringIO(command)),
                mock.patch('socket.socket', autospec=True) as socket_mock,
                mock.patch('mood.client.msg_reciever', return_value=True)
             ):
            client.start_client("test")
            sendall_call = socket_mock.mock_calls[6].args[0]
            self.assertEqual(sendall_call, b'attack kitty sword\n')

    def test_3_attack_axe(self):
        command = "addmon kitty coords 0 1 hello eww hp 10\ndown\nattack kitty with axe"
        with (
                mock.patch('sys.stdin', StringIO(command)),
                mock.patch('socket.socket', autospec=True) as socket_mock,
                mock.patch('mood.client.msg_reciever', return_value=True)
             ):
            client.start_client("test")
            sendall_call = socket_mock.mock_calls[6].args[0]
            self.assertEqual(sendall_call, b'attack kitty axe\n')

    def test_4_attack_wrong_weapon(self):
        command = "addmon kiss coords 0 1 hello eww hp 10\ndown\nattack kitty with alibarda"
        with (
                mock.patch('sys.stdin', StringIO(command)),
                mock.patch('builtins.print', autospec=True) as output_mock,
                mock.patch('socket.socket', autospec=True),
                mock.patch('mood.client.msg_reciever', return_value=True)
             ):
            client.start_client("test")
            output_call = output_mock.mock_calls[0].args[0]
            self.assertEqual(output_call, 'Unknown weapon\n~ ')



