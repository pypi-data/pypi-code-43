
from ..share.task import Task
from .client import Client
from ..share import constants


class Trigger(object):

    box_class = None
    client = None

    def __init__(self, box_class, host, port, ensure=True):
        self.box_class = box_class
        self.client = Client((host, port), ensure)

    def write_to_worker(self, room_id, data):
        """
        透传到worker进行处理
        """

        task = Task()
        task.cmd = constants.CMD_WRITE_TO_WORKER
        task.room_id = room_id

        if isinstance(data, self.box_class):
            # 打包
            data = data.pack()
        elif isinstance(data, dict):
            data = self.box_class(data).pack()
            
        task.body = data

        return self._write(task.pack())

    def _write(self, data):
        return self.client.write(data)

    def __repr__(self):
        return '<%s address: %s>' % (
            type(self).__name__, self.client.address
        )
