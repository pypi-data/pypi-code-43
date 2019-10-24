from contextlib import closing
from random import randint


class NetworkUtils():

    @staticmethod
    def is_port_in_use(port):
        import socket
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            return s.connect_ex(('localhost', port)) == 0

    @staticmethod
    def get_random_port():
        while True:

            port_num = randint(10000, 60000)
            if not NetworkUtils.is_port_in_use(port_num):
                break
        return port_num