"""
"""

from __future__ import annotations

import socket
import urllib.request
from concurrent.futures.thread import ThreadPoolExecutor

from healer.config import CONFIG


class NetworkSupport:
    """
    Network operations support
    """

    localhost_address = "127.0.0.1"

    @staticmethod
    def private_address() -> str:
        section = 'network/support'
        host = str(CONFIG[section]['private_address_host'])
        port = int(CONFIG[section]['private_address_port'])
        probe_point = (host, port)
        socket_probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # need not be reachable
            socket_probe.connect(probe_point)
            address = socket_probe.getsockname()[0]
        except:
            address = NetworkSupport.localhost_address
        finally:
            socket_probe.close()
        return address

    @staticmethod
    def public_address() -> str:
        section = 'network/support'
        timeout = float(CONFIG[section]['public_address_timeout'])
        host_list = CONFIG.get_list(section, 'public_address_host_list')
        with ThreadPoolExecutor(max_workers=1) as executor:
            for host in host_list:
                task = lambda : urllib.request.urlopen(
                   url=host, timeout=timeout,
                ).read().decode('utf-8').strip()
                future = executor.submit(task)
                try:
                    return future.result(timeout=timeout)
                except:
                    continue
        return NetworkSupport.localhost_address

    @staticmethod
    def host_name() -> str:
        return socket.gethostname()
