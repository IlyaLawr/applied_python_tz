import socket
import argparse
import pickle


class Task:
    def __init__(self, queue: bytes, length: bytes, data: bytes, id: int):
        self.queue = queue
        self.length = length
        self.data = bytearray(data)

        self.id = id
        self._in_processing = False
        self.complete = False


class TaskQueueServer:
    def __init__(self, ip: str, port: int, path: str, timeout: int):
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.bind((ip, port))
        self._timeout = timeout

        self._path = path
        self._tasks_queues = {}


    def _add_task(self, queue: bytes, length: bytes, data: bytes) -> bytes:
        '''Принимает имя очереди, длину задания и содержимое задания. Добавляет задание в очередь,
           возвращает уникальный идентификатор задания. Если такой очереди нет, то создает ее и добавляет задание.
        '''
        pass


    def _get_task(self, queue: bytes) -> bytes:
        '''Принимает имя очереди, возвращает уникальный идентификатор задания, длину задания и содержимое задания.
        '''
        if queue not in self._tasks_queues or not self._tasks_queues[queue]:
            return b'NONE'


    def _ack_task(self, queue: bytes, id: bytes) -> bytes:
        '''Принимает очередь и идентификатор задания, возвращает подтверждение выполнения.
        '''
        if id not in self._tasks_queues[queue]:
            return b'NO'


    def _in_task(self, queue: bytes, id: bytes) -> bytes:
        '''Принимает очередь и идентификатор задания, возвращает подтверждение наличия задания в очереди.
        '''
        if id not in self._tasks_queues[queue]:
            return b'NO'


    def _save(self) -> None:
        '''Сохраняет текущее состояние очереди на диск.
        '''
        with open(f'{self._path}_tasks_queues.pickle', 'wb') as f:
            pickle.dump(self._tasks_queues, f)


    def run(self):
        self._server.listen()
        conn, address = self._server.accept()


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
        default=300,
        help='Task maximum GET timeout in seconds')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    server = TaskQueueServer(**args.__dict__)
    server.run()
