import subprocess
import unittest
import socket
import time
import sys
import os


class ServerBaseTest(unittest.TestCase):
    def setUp(self):
        self.server = subprocess.Popen(['python', 'task_queue\\server.py'])
        # Даем серверу время на запуск.
        time.sleep(0.5)


    def tearDown(self):
        self.server.terminate()
        self.server.wait()


    def send(self, command):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 5555))
        s.send(command)
        data = s.recv(1000000)
        s.close()
        return data


    def test_base_scenario(self):
        task_id = self.send(b'ADD 1 5 12345')
        self.assertEqual(b'YES', self.send(b'IN 1 ' + task_id))

        self.assertEqual(task_id + b' 5 12345', self.send(b'GET 1'))
        self.assertEqual(b'YES', self.send(b'IN 1 ' + task_id))
        self.assertEqual(b'YES', self.send(b'ACK 1 ' + task_id))
        self.assertEqual(b'NO', self.send(b'ACK 1 ' + task_id))
        self.assertEqual(b'NO', self.send(b'IN 1 ' + task_id))


    def test_two_tasks(self):
        first_task_id = self.send(b'ADD 1 5 12345')
        second_task_id = self.send(b'ADD 1 5 12345')
        self.assertEqual(b'YES', self.send(b'IN 1 ' + first_task_id))
        self.assertEqual(b'YES', self.send(b'IN 1 ' + second_task_id))

        self.assertEqual(first_task_id + b' 5 12345', self.send(b'GET 1'))
        self.assertEqual(b'YES', self.send(b'IN 1 ' + first_task_id))
        self.assertEqual(b'YES', self.send(b'IN 1 ' + second_task_id))
        self.assertEqual(second_task_id + b' 5 12345', self.send(b'GET 1'))

        self.assertEqual(b'YES', self.send(b'ACK 1 ' + second_task_id))
        self.assertEqual(b'NO', self.send(b'ACK 1 ' + second_task_id))


    def test_long_input(self):
        data = '12345' * 1000
        data = '{} {}'.format(len(data), data)
        data = data.encode('utf')
        task_id = self.send(b'ADD 1 ' + data)
        self.assertEqual(b'YES', self.send(b'IN 1 ' + task_id))
        self.assertEqual(task_id + b' ' + data, self.send(b'GET 1'))


    def test_wrong_command(self):
        self.assertEqual(b'ERROR', self.send(b'ADDD 1 5 12345'))


class ServerAdditionalTest(unittest.TestCase):
    def setUp(self):
        self.server = subprocess.Popen(['python', 'task_queue\\server.py'])
        # Даем серверу время на запуск.
        time.sleep(0.5)


    def tearDown(self):
        self.server.terminate()
        self.server.wait()


    def send(self, command):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 5555))
        s.send(command)
        data = s.recv(1000000)
        s.close()
        return data


    def test_timeout(self):
        task_id_1 = self.send(b'ADD queue_1 6 qwerty')
        task_id_2 = self.send(b'ADD queue_1 10 X_qwerty_X')
        self.assertEqual(task_id_1 + b' 6 qwerty', self.send(b'GET queue_1'))
        task_id_3 = self.send(b'ADD queue_1 3 X_Y')
        time.sleep(6)
        self.assertEqual(task_id_1 + b' 6 qwerty', self.send(b'GET queue_1'))
        time.sleep(2)
        self.assertEqual(task_id_2 + b' 10 X_qwerty_X', self.send(b'GET queue_1'))
        time.sleep(6)
        self.assertEqual(task_id_1 + b' 6 qwerty', self.send(b'GET queue_1'))
        self.assertEqual(task_id_2 + b' 10 X_qwerty_X', self.send(b'GET queue_1'))
        self.assertEqual(b'YES', self.send(b'ACK queue_1 ' + task_id_1))
        task_id_4 = self.send(b'ADD queue_1 1 !')
        self.assertEqual(task_id_3 + b' 3 X_Y', self.send(b'GET queue_1'))
        self.assertEqual(b'YES', self.send(b'ACK queue_1 ' + task_id_3))
        self.assertEqual(task_id_4 + b' 1 !', self.send(b'GET queue_1'))
        time.sleep(6)
        self.assertEqual(task_id_2 + b' 10 X_qwerty_X', self.send(b'GET queue_1'))
        self.assertEqual(task_id_4 + b' 1 !', self.send(b'GET queue_1'))
        self.assertEqual(b'NONE', self.send(b'GET queue_1'))
        self.assertEqual(b'YES', self.send(b'ACK queue_1 ' + task_id_2))
        self.assertEqual(b'YES', self.send(b'ACK queue_1 ' + task_id_4))


    def test_save(self):
        for i in range(3):
            for j in range(3):
                self.send(f'ADD {i} {j} {str(i) * j}'.encode('utf-8'))

        self.assertEqual(b'0 0 ', self.send(b'GET 2'))
        self.assertEqual(b'YES', self.send(b'ACK 2 0'))
        self.assertEqual(b'OK', self.send(b'SAVE'))

        self.tearDown() # Сворачиваем сервер после сохранения.
        time.sleep(2) # Визуально проверяем что файлы создаются:)
        self.setUp() # Запускаем вновь.

        self.assertEqual(b'0 0 ', self.send(b'GET 0'))
        self.assertEqual(b'0 0 ', self.send(b'GET 1'))
        self.assertEqual(b'1 1 2', self.send(b'GET 2'))
        self.assertEqual(b'1 1 0', self.send(b'GET 0'))
        time.sleep(6)
        self.assertEqual(b'0 0 ', self.send(b'GET 0'))


if __name__ == '__main__':
    unittest.main()
