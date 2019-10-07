from pyglet.clock import Clock
import signal
import setproctitle

from ..share import constants
from ..share.log import logger
from ..share.utils import safe_call
from .connection import Connection
from ..share.task import Task
from ..proto.pansy_pb2 import RspToUsers, CloseUsers


class Worker:
    app = None
    room_id = None

    enable = True

    conn = None
    clock = None

    # 监听对象
    listener = None

    def __init__(self, app, room_id):
        self.app = app
        self.room_id = room_id
        self.listener = self.app.listener_class(self)

    def run(self):
        setproctitle.setproctitle(self.app.make_proc_name('worker:%s' % self.room_id))
        self._handle_signals()

        self.conn = Connection(self)
        self.clock = Clock()
        self.clock.set_fps_limit(self.app.fps)

        self.on_start()

        # 房间必须有效才进行循环
        while self.enable:
            try:
                # 获取网络消息放在之前dt更准一些
                dt = self.clock.tick()
                self.update(dt)
                # logger.debug('fps: %s', clock.get_fps())
            except KeyboardInterrupt:
                break
            except:
                logger.error('exc occur.', exc_info=True)

        self.on_stop()

    def update(self, dt):
        """
        :param dt: 经过时间
        :return:
        """
        self.conn.update()
        task_list = self.conn.fetch_task_list()
        self.on_update(dt, task_list)
        # 立即发送
        self.conn.send_now()

    def on_update(self, dt, task_list):
        """
        必须继承实现
        :param dt: 等待时间
        :param task_list: 消息列表
        :return:
        """
        safe_call(self.listener.on_update, dt, task_list)

    def on_start(self):
        """
        当worker启动后
        可继承实现
        :return:
        """
        safe_call(self.listener.on_start)

    def on_stop(self):
        """
        当worker停止前
        可继承实现
        :return:
        """
        safe_call(self.listener.on_stop)

    def write_to_users(self, data_list):
        """
        格式为
        [(uids, box), (uids, box), (uids, box) ...]
        :param data_list:
        :return:
        """

        msg = RspToUsers()

        for uids, data in data_list:
            if isinstance(data, self.app.box_class):
                data = data.pack()
            elif isinstance(data, dict):
                data = self.app.box_class(data).pack()

            row = msg.rows.add()
            row.buf = data
            row.uids.extend(uids)

        task = Task()
        task.cmd = constants.CMD_WRITE_TO_USERS
        task.body = msg.SerializeToString()

        return self.conn.write(task.pack())

    def close_users(self, uids):
        msg = CloseUsers()
        msg.uids.extend(uids)

        task = Task()
        task.cmd = constants.CMD_CLOSE_USERS
        task.body = msg.SerializeToString()

        return self.conn.write(task.pack())

    def _handle_signals(self):
        def safe_stop_handler(signum, frame):
            self.enable = False

        # 忽略掉
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        # 安全停止
        signal.signal(signal.SIGTERM, safe_stop_handler)


