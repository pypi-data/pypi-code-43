import logging
from p4runtime.server import P4RuntimeServer


def main():

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    p4rt_server = P4RuntimeServer()
    p4rt_server.serve()


if __name__ == '__main__':
    main()