from saturn import start_server
import sys


def get_argv(index, default=None):
    try:
        return sys.argv[index]
    except IndexError:
        return default

host = get_argv(1, "0.0.0.0")
port = get_argv(2, 8080)

start_server(host, port)