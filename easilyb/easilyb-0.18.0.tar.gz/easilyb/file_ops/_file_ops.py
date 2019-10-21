import logging
logger = logging.getLogger(__name__)

def read_all(sock):
    sock.settimeout(5.0)
    data = ""
    while True:
        part = sock.recv(4096)
        data += part
        if len(part) < 4096:
            break
    return data