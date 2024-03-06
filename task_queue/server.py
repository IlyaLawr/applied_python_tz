from  collections import deque
import threading
import argparse
import socket
import pickle
import os


class Task:
    def __init__(self, queue: bytes, length: bytes, data: bytes, id: int):
        self.queue = queue
        self.length = length
        self.data = data
        self.id = id


class TaskQueueServer:
    def __init__(self, ip: str, port: int, path: str, timeout: int):
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.bind((ip, port))
        self._timeout = timeout

        self._path = path
        self._tasks_queues = {} # Хранилище очередей с заданиями.
        self._tasks_in_processing = {} # Хранилище задании взятых в обработку.


    def _add_task(self, queue: bytes, length: bytes, data: bytes) -> bytes:
        '''Принимает имя очереди, длину задания и содержимое задания. Добавляет задание в очередь,
           возвращает уникальный идентификатор задания. Если такой очереди нет, то создает ее и добавляет задание.'''
        id_task = self._create_id(queue) if queue in self._tasks_queues else 0
        if id_task:
            self._tasks_queues[queue].append(Task(queue, length, data, id_task))
        else:
            self._tasks_queues[queue] = deque((Task(queue, length, data, id_task), ))
        return str(id_task).encode('utf-8')


    def _get_task(self, queue: bytes) -> bytes:
        '''Принимает имя очереди, возвращает уникальный идентификатор задания, длину задания и содержимое задания.'''
        if queue not in self._tasks_queues or not self._tasks_queues[queue]:
            return b'NONE'

        task = self._tasks_queues[queue].popleft()
        self._tasks_in_processing[(queue, task.id)] = (task, threading.Timer(self._timeout, self._return_to_queue, args=(queue, task.id)))
        self._tasks_in_processing[(queue, task.id)][1].start()
        return b' '.join([str(task.id).encode('utf-8'), task.length, task.data])


    def _ack_task(self, queue: bytes, id: bytes) -> bytes:
        '''Принимает очередь и идентификатор задания, возвращает подтверждение выполнения.'''
        id = int(id)
        if (queue, id) in self._tasks_in_processing:
            self._tasks_in_processing[(queue, id)][1].cancel()
            del self._tasks_in_processing[(queue, id)]
            return b'YES'
        else:
            return b'NO'


    def _in_task(self, queue: bytes, id: bytes) -> bytes:
        '''Принимает очередь и идентификатор задания, возвращает подтверждение наличия задания в очереди.'''
        id = int(id)
        if (queue, id) in self._tasks_in_processing \
           or (queue in self._tasks_queues and [task for task in self._tasks_queues[queue] if task.id == int(id)]):
           return b'YES'
        return b'NO'


    def _return_to_queue(self, queue: bytes, id: int) -> None:
        '''Принимает очередь и идентификатор задания, возвращает не выполненное задание обратно в очередь.'''
        if not self._tasks_queues[queue] or (self._tasks_queues[queue] and self._tasks_queues[queue][-1].id < id):
            self._tasks_queues[queue].append(self._tasks_in_processing[(queue, id)][0])
        else:
            for task in self._tasks_queues[queue]:
                if task.id > id:
                    self._tasks_queues[queue].insert(self._tasks_queues[queue].index(task), self._tasks_in_processing[(queue, id)][0])
                    break
        del self._tasks_in_processing[(queue, id)]


    def _create_id(self, queue: bytes) -> int:
        if queue in self._tasks_queues and self._tasks_queues[queue]:
            return max(self._tasks_queues[queue], key=lambda task: task.id).id + 1
        elif queue in self._tasks_queues and not self._tasks_queues[queue]:
            queue_ids = tuple((task_id for queue_task, task_id in self._tasks_in_processing if queue_task == queue))
            return max(queue_ids) + 1 if queue_ids else 0
        return 0


    def _save(self) -> bytes:
        try:
            with open(f'{self._path}_tasks_queues.pickle', 'wb') as f1, open(f'{self._path}_tasks_in_processing.pickle', 'wb') as f2:
                pickle.dump(self._tasks_queues, f1)
                pickle.dump(self._tasks_in_processing, f2)
            return b'OK'
        except:
            return b'SAVE ERROR'


    def _loading(self) -> bool:
        try:
            with open(f'{self._path}_tasks_queues.pickle', 'rb') as f1, open(f'{self._path}_tasks_in_processing.pickle', 'rb') as f2:
                self._tasks_queues = pickle.load(f1)
                self._tasks_in_processing = pickle.load(f2)
                self._deleting_saves()
            return True
        except:
            return False


    def _deleting_saves(self) -> None:
        os.remove(f'{self._path}_tasks_queues.pickle')
        os.remove(f'{self._path}_tasks_in_processing.pickle')


    def _checking_save(self) -> None:
        if os.path.exists(f'{self._path}_tasks_queues.pickle'):
            if not self._loading():
                print('Сохраненные ранее данные не удалось загрузить, состояние очереди инициировано вновь.')
                self._deleting_saves()
            else:
                print('Имеются ранее сохраненные данные, состояние очереди успешно загружено с диска.')


    def _command_routing(self, command_data: bytes) -> bytes:
        functions = {b'ADD': self._add_task, b'GET': self._get_task, b'ACK': self._ack_task, b'IN': self._in_task, b'SAVE': self._save}
        command, *data = command_data.split(b' ')

        if command not in functions:
            return b'ERROR'
        elif len(data) > 2:
            return functions[command](data[0], data[1], b' '.join(data[2:]))
        elif len(data) == 2:
            return functions[command](data[0], data[1])
        elif len(data) == 1:
            return functions[command](data[0])
        else:
            return functions[command]()


    def run(self):
        self._checking_save()
        self._server.listen(1)
        while True:
            connection, client_address = self._server.accept()
            data = connection.recv(1000000)
            connection.send(self._command_routing(data))
            connection.close()


def parse_args():
    parser = argparse.ArgumentParser(description='This is a simple task queue server with custom protocol')
    parser.add_argument(
        '-p',
        action="store",
        dest="port",
        type=int,
        default=5555,
        help='Server port')
    parser.add_argument(
        '-i',
        action="store",
        dest="ip",
        type=str,
        default='127.0.0.1',
        help='Server ip adress')
    parser.add_argument(
        '-c',
        action="store",
        dest="path",
        type=str,
        default='./',
        help='Server checkpoints dir')
    parser.add_argument(
        '-t',
        action="store",
        dest="timeout",
        type=int,
        default=5,
        help='Task maximum GET timeout in seconds')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    server = TaskQueueServer(**args.__dict__)
    server.run()
