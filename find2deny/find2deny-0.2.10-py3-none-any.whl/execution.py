from abc import ABC, abstractmethod

from .log_parser import LogEntry
import re
import logging


class AbstractIpBlockExecution(ABC):
    @abstractmethod
    def begin_execute(self):
        pass

    @abstractmethod
    def block(self,log: LogEntry):
        pass

    @abstractmethod
    def end_execute(self):
        pass


class FileBasedUWFBlock(AbstractIpBlockExecution):
    """
        write generated uwf firewall rules into a file.
        block also all IPs in same Netmask of the IP
    """

    def __init__(self, destinate_path: str, insert_line: str or int = 5):
        self.__destinate_path = destinate_path
        self.__blocked_item = []
        self.__insert_line = insert_line

    def begin_execute(self):
        self.__blocked_item = []
        pass

    def block(self, log: LogEntry, cause: str = None):
        cause = cause.replace('\n', ' ') if cause is not None else ' '
        # Block network of IP
        for n in re.split(",\\s*", log.network):
            ufw_block_cmd = f"ufw insert {self.__insert_line} deny from {n.strip()} to any # {cause}"
            logging.debug("use command %s", ufw_block_cmd)
            self.__blocked_item.append(f"{ufw_block_cmd}\n")
        # block IP
        ufw_block_cmd = f"ufw insert {self.__insert_line} deny from {log.ip_str} to any # {cause}"
        logging.debug("use command %s", ufw_block_cmd)
        self.__blocked_item.append(f"{ufw_block_cmd}\n")
        pass

    def end_execute(self):
        with open(self.__destinate_path, 'w') as f:
            f.write("#!/bin/bash\n")
            f.writelines(self.__blocked_item)
        logging.info("Block %d IPs", len(self.__blocked_item))
        pass


class FileBasedUWFBSingleBlock(AbstractIpBlockExecution):
    """
        write generated uwf firewall rules into a file.
        block only the IP which causes problem
    """

    def __init__(self, destinate_path: str, insert_line: str or int = 5):
        self.__destinate_path = destinate_path
        self.__blocked_item = []
        self.__insert_line = insert_line

    def begin_execute(self):
        self.__blocked_item = []
        pass

    def block(self, log: LogEntry, cause: str = None):
        cause = cause.replace('\n', ' ') if (cause is not None) else ' '
        # block IP
        ufw_block_cmd = f"ufw insert {self.__insert_line} deny from {log.ip_str} to any # {cause}"
        logging.debug("use command %s", ufw_block_cmd)
        self.__blocked_item.append(f"{ufw_block_cmd}\n")
        pass

    def end_execute(self):
        with open(self.__destinate_path, 'w') as f:
            f.write("#!/bin/bash\n")
            f.writelines(self.__blocked_item)
        logging.info("Block %d IPs", len(self.__blocked_item))
        pass