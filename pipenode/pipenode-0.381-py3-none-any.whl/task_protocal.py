import json
import zlib
import copy
from .tasks import Task


class TaskProtocal(Task):
    __slots__ = ['_info', '_tid', '_runtype', '_runtask']

    def __init__(self, task):
        assert isinstance(task, (Task, dict)
                          ), "task should be a instance of Task or dict"
        if isinstance(task, Task):
            _data = task.get_raw_data()
            super(TaskProtocal, self).__init__(_data)
            self.set_from(task.get_from())
            self.set_to(task.get_to())
            self.set_confirm_handle(task.get_confirm_handle())
            self._info = json.loads(_data.decode('utf-8'))
            self._tid = self.get_tid()
            self._runtype = self.get_runtype()
            self._runtask = self.get_runtask()
        else:
            super(TaskProtocal, self).__init__(
                json.dumps(task).encode('utf-8'))
            self._info = task
            self._tid = self.get_tid()
            self._runtype = self.get_runtype()
            self._runtask = self.get_runtask()
        assert 'i' in self._info and 'tid' in self._info, "Task Protocal illegal"

    def get_data(self):
        return copy.deepcopy(self._info['data'])

    def get_tid(self):
        return self._info['tid']

    def get_direction(self):
        return self._info.get('direction')

    def get_runtype(self):
        return self._info.get('data').get('_type')

    def get_runtask(self):
        return self._info.get('data').get('_task')

    def get_step(self):
        return self._info['i']

    def set_path(self, task_dct, i='0', key='back'):
        new_tp = self.new_task(task_dct, i=i)
        new_tp.set_to(key)
        return new_tp

    def new_task(self, data, direction=None, tid=None, i=None, name=None, next_step=False):
        assert isinstance(data, dict), "data isn't a dict"
        if 'extra' in self._info['data']:
            dct = data.setdefault("extra", {})
            dct.update(self._info['data']['extra'])
        if i == '0':
            i = 0
        else:
            i = 0 if tid else self._info['i'] + \
                              1 if next_step else self._info['i']
        dct = {
            'tid': tid if tid else self._info['tid'],
            'i': i,
            'data': data
        }
        tp = TaskProtocal(dct)
        tp.set_confirm_handle(self.get_confirm_handle())
        return tp

