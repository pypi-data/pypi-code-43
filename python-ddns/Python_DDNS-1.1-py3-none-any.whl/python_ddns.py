# pylint: disable=invalid-name, missing-docstring, inconsistent-return-statements
import socket
import sys
from . import cloudflare

# Shamlessly taken from stackoverflow https://stackoverflow.com/a/28950776/11542276
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('1.1.1.1', 1))
        host = s.getsockname()[0]
    finally:
        s.close()
    return host


def quick_test():
    if cloudflare.CONFIG == 0:
        raise FileNotFoundError

def main():
    if sys.argv[1] == "-t":
        quick_test()
        sys.exit()
    check = cloudflare.check_record()
    if check:
        cloudflare.update_record(get_ip(), check)
    else:
        cloudflare.add_record(get_ip())
