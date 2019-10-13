import json
import socket

from .files import get_file_contents


def read_description(sd_filename):
    sd = get_file_contents(sd_filename)
    my_ip = find_my_ip()
    if my_ip:
        sd = sd.replace("localhost", my_ip)
    return json.loads(sd)


def find_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except:
        ip = None
    finally:
        s.close()
    return ip
