import socket
import logging
logger = logging.getLogger(__name__)


def get_tcp_banner(ip, port):
    try:
        s = socket.socket()
        s.settimeout(5.0)
        s.connect((ip, int(port)))
        s.send(b'GET /\n\n')
        banner = s.recv(100)
        try:
            banner_dec = banner.decode()
        except:
            banner_dec = repr(banner)[2:-1]
        return banner_dec
    except:
        logger.error("Error while getting TCP banner for %s.", (ip, port,), exc_info=True)
        return ''
    finally:
        try: s.close()
        except: pass


def get_udp_banner(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(5.0)
        s.connect((ip, int(port)))
        s.send(b'GET /\n\n')
        banner = s.recv(100)
        try:
            banner_dec = banner.decode()
        except:
            banner_dec = repr(banner)[2:-1]
        return banner_dec
    except:
        logger.error("Error while getting UDP banner for %s.", (ip, port,), exc_info=True)
        return ''
    finally:
        try: s.close()
        except: pass


def getdomainsbyip(ip):
    try:
        ret = socket.gethostbyaddr(ip)
        return [ret[0]] + ret[1]
    except:
        return []


def getipsbydomain(domain):
    try:
        return socket.gethostbyname_ex(domain)[2]
    except:
        return []