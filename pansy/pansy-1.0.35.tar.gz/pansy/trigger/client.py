
import errno
import socket
import time
import functools
from threading import Lock
from ..share.log import logger
from ..share import constants


def lock_write(func):
    @functools.wraps(func)
    def func_wrapper(client, *args, **kwargs):
        try:
            client.acquire_write_lock()
            return func(client, *args, **kwargs)
        finally:
            client.release_write_lock()
    return func_wrapper


class Client(object):

    address = None
    ensure = None
    sock = None

    # 加锁来保证线程安全
    write_lock = None

    def __init__(self, address, ensure, lock=True):
        self.address = address
        self.ensure = ensure

        if lock:
            self.write_lock = Lock()

    @lock_write
    def write(self, data):
        """
        发送
        :param data:
        :return:
        """

        while True:
            self._detect_connection_status()

            # 先要保证连接可用
            if self.closed() and not self._connect():
                logger.error('connect fail, address: %s%s',
                             self.address,
                             ', sleep %ss' % constants.RECONNECT_INTERVAL if self.ensure else '')
                if self.ensure:
                    time.sleep(constants.RECONNECT_INTERVAL)
                    continue
                else:
                    return False

            if self._write_to_fd(data):
                # 写入成功
                return True
            else:
                if not self.ensure:
                    return False

    def close(self):
        """
        关闭连接
        :return:
        """
        if self.sock:
            try:
                self.sock.close()
            except:
                pass

            self.sock = None

    def closed(self):
        """
        检查连接
        :return:
        """

        return not self.sock

    def _detect_connection_status(self):
        """
        通过recv的方式，检查连接状态
        :return: 是否连接
        """

        if not self.sock:
            return False

        try:
            # setblocking也是可能抛异常的
            # File "/usr/local/lib/python2.7/socket.py", line 224, in meth
            #     return getattr(self._sock,name)(*args)
            # File "/usr/local/lib/python2.7/socket.py", line 170, in _dummy
            #     raise error(EBADF, 'Bad file descriptor')
            # error: [Errno 9] Bad file descriptor
            self.sock.setblocking(False)

            if not self.sock.recv(1):
                # 返回''，代表连接已经关闭
                self.close()
                return False
            else:
                # 收到了数据，连接正常
                # 理论上不会到达这里，因为trigger是不会收到回应的
                return True
        except socket.error as e:
            if e.errno in (errno.EINTR, errno.EAGAIN):
                # 中断/没有可读数据，连接正常
                return True
            # 其他情况下，都代表错误
            self.close()
            return False
        except KeyboardInterrupt as e:
            raise e
        except:
            self.close()
            return False
        finally:
            if self.sock:
                self.sock.setblocking(True)

    def _write_to_fd(self, data):
        """
        写入
        """

        while data:
            try:
                num_bytes = self.sock.send(data)
            except KeyboardInterrupt as e:
                raise e
            except Exception as e:
                logger.error('socket send fail. e: %s, data: %r', e, data[:100])
                # 关闭连接
                self.close()
                return False

            data = data[num_bytes:]

        return True

    def _connect(self):
        """
        在写入之前调用，保证连接可用
        :return:
        """
        if ':' in self.address[0]:
            # IPV6
            socket_type = socket.AF_INET6
        else:
            socket_type = socket.AF_INET

        self.sock = socket.socket(socket_type, socket.SOCK_STREAM)
        # TCP_NODELAY 打开
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        try:
            self.sock.connect(self.address)
        except KeyboardInterrupt as e:
            self.close()
            raise e
        except Exception as e:
            self.close()
            return False
        else:
            # 连接成功
            return True

    def acquire_write_lock(self):
        if self.write_lock:
            self.write_lock.acquire()

    def release_write_lock(self):
        if self.write_lock:
            self.write_lock.release()

