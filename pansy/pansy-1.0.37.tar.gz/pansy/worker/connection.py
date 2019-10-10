import socket
import errno
import select
import time

from ..share import constants
from ..share.log import logger
from ..share.task import Task


class Connection:
    worker = None
    client = None
    # 是否已连接，因为需要判断连接状态
    connected = None

    # 待发送buf
    send_buf = None

    # 接收到buf
    recv_buf = None

    task_list = None

    _connect_expire_time = None

    def __init__(self, worker):
        self.worker = worker
        self.connected = False
        self.send_buf = bytearray()
        self.recv_buf = bytearray()
        self.task_list = []

    def fetch_task_list(self):
        task_list = self.task_list
        self.task_list = []
        return task_list

    def close(self):
        if self.client:
            try:
                self.client.close()
            except:
                logger.error('exc occur.', exc_info=True)
            finally:
                self.client = None
            self.connected = False

    def update(self):
        """
        定时操作
        :return:
        """

        if not self.client:
            if ':' in self.worker.app.host:
                # IPV6
                socket_type = socket.AF_INET6
            else:
                socket_type = socket.AF_INET

            self.client = socket.socket(socket_type, socket.SOCK_STREAM)
            self.client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.client.setblocking(False)
            # 连接过期时间
            self._connect_expire_time = time.time() + self.worker.app.conn_timeout
            ret = self.client.connect_ex((self.worker.app.host, self.worker.app.port))
            if ret == 0:
                # 说明连接直接成功了
                self.connected = True
                logger.debug('connected')
            else:
                # 115：当链接设置为非阻塞时，目标没有及时应答，返回此错误，socket可以继续使用
                if errno.errorcode[ret] == errno.EINPROGRESS or ret == 115:
                    # 说明正在连接中
                    # 等待select去处理
                    logger.debug('connecting')
                else:
                    # 创建连接失败
                    self.client = None
                    logger.debug('connect fail. ret: %s', ret)

        else:
            # 如果已经创建socket了，那么就要判断是否已经连接成功的状态了
            if not self.connected:
                self._detect_connect_result()

            if self.connected:
                wlist = [self.client] if self.send_buf else []

                ready_to_read, ready_to_write, in_error = select.select([self.client], wlist, [self.client], 0)

                if ready_to_read:
                    self._try_to_recv()

                if ready_to_write:
                    self._try_to_send()

                if in_error:
                    self.close()

        if self.recv_buf:
            self.task_list.extend(self._parse_recv_buf())

    def write(self, data):
        self.send_buf.extend(data)

    def send_now(self):
        """
        立即发送数据
        :return:
        """
        self._try_to_send()

    def _detect_connect_result(self):
        """
        检测连接结果
        :return:
        """

        if time.time() > self._connect_expire_time:
            # 超时了
            logger.debug('connect timeout')
            self.close()
            return

        # 使用select
        # timeout要传0，代表立即返回
        ready_to_read, ready_to_write, in_error = select.select([], [self.client], [self.client], 0)
        if in_error:
            logger.debug('connect fail')
            self.close()
        elif ready_to_write:
            if self.client.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR) == 0:
                # 说明连接成功
                self.connected = True
                logger.debug('connected delay')
                self._on_connected()
            else:
                logger.debug('connect fail')
                self.close()

    def _parse_recv_buf(self):
        task_list = []
        offset = 0
        while offset < len(self.recv_buf):
            task = Task()
            ret = task.unpack(bytes(self.recv_buf[offset:]))
            if ret < 0:
                # 说明buf有问题
                self.recv_buf = bytearray()
                break
            elif ret == 0:
                # 没有接收完
                break
            else:
                offset += ret
                task_list.append(task)

        self.recv_buf = self.recv_buf[offset:]

        return task_list

    def _on_connected(self):
        self._ask_for_task()

    def _ask_for_task(self):
        task = Task()
        task.cmd = constants.CMD_WORKER_ASK_FOR_TASK
        task.room_id = self.worker.room_id

        self.write(task.pack())
        self.send_now()

    def _try_to_recv(self):
        while self.connected:
            try:
                chunk = self.client.recv(self.worker.app.config['RECV_CHUNK_SIZE'])
                if not chunk:
                    self.close()
                    break

                self.recv_buf.extend(chunk)

            except socket.error as e:
                if e.errno in (errno.EINTR, errno.EAGAIN):
                    # 中断 或者 没有可读数据(非阻塞模式)
                    break
                else:
                    # Connection reset by peer 的原因说明:
                    # 网上说是对端非正常关闭连接，比如对端程序异常退出之类
                    # 我重现的方法是: C向S发送数据，如果S有回应，而C没有读取，C就调用close或者被析构的话
                    logger.error('exc occur.', exc_info=True)
                    self.close()
                    break
            except KeyboardInterrupt as e:
                # 中断
                raise e
            except:
                logger.error('exc occur.', exc_info=True)
                # 其他都直接关闭
                self.close()
                break

    def _try_to_send(self):
        """
        尝试发送，因为考虑到实时性，应该尽快发送出去
        :return:
        """

        while self.connected and self.send_buf:
            try:
                ret = self.client.send(self.send_buf)
                if ret < 0:
                    # 说明报错
                    break
                else:
                    self.send_buf = self.send_buf[ret:]
            except:
                logger.error('exc occur.', exc_info=True)
                break
