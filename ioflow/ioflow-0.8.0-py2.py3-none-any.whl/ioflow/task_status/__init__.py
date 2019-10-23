import requests

from ioflow.utils import log_call

task_status_registry = {}


def get_task_status_class(config):
    return task_status_registry[config.get('task_status_schema', 'local')]


def get_task_status(config) -> 'BaseTaskStatus':
    task_status_class = get_task_status_class(config)
    return task_status_class(config)


def registry_task_status_class(schema, class_):
    task_status_registry[schema] = class_


class BaseTaskStatus(object):
    def __init__(self, config):
        self.config = config

    def send_status(self, status):
        raise NotImplementedError

    def send_progress(self, progress):
        raise NotImplementedError


class TaskStatus(BaseTaskStatus):
    @log_call
    def send_status(self, status):
        return self.do_send_status(status)

    def do_send_status(self, status):
        raise NotImplementedError

    @log_call
    def send_progress(self, progress):
        return self.do_send_progress(progress)

    def do_send_progress(self, progress):
        raise NotImplementedError


class LocalTaskStatus(TaskStatus):
    def __init__(self, config):
        self.DONE = 10
        self.START = 1
        super().__init__(config)

    def __getattr__(self, name):
        return str(name).lower()

    def do_send_status(self, status):
        # print('[{}] status: {}'.format(self.__class__, status))
        pass

    def do_send_progress(self, progress):
        # print('[{}]: progress: {}'.format(self.__class__, progress))
        pass


registry_task_status_class('local', LocalTaskStatus)


class HttpTaskStatus(TaskStatus):
    DONE = 10
    START = 1

    START_DOWNLOAD_CORPUS = 2
    START_PROCESS_CORPUS = 3
    START_TRAIN = 4
    START_TEST = 5
    START_UPLOAD_MODEL = 6

    CODE_TO_STR = {
        DONE: 'done',
        START: 'start',
        START_DOWNLOAD_CORPUS: '下载语料',
        START_PROCESS_CORPUS: '语料处理',
        START_TRAIN: '训练',
        START_TEST: '测试',
        START_UPLOAD_MODEL: '模型上传'
    }

    def __init__(self, config):
        super().__init__(config)

    def do_send_progress(self, progress):
        data = {'trainProgress': str(progress)}

        self._send_request(data)

    def do_send_status(self, status):
        print('{}:{}'.format(self.__class__, status))

        if status in self.CODE_TO_STR:
            data = {'stepProgress': self.CODE_TO_STR[status]}
        else:
            data = status

        self._send_request(data)

    def _send_request(self, data):
        json_data = {'id': self.config['task_id']}
        json_data.update(data)

        r = requests.post(self.config['progress_report_url'], json=json_data)
        assert r.ok, r.content


registry_task_status_class('http', HttpTaskStatus)


if __name__ == "__main__":
    task_status_class = get_task_status_class({})
    config = {
        "progress_report_url": "http://10.43.13.8:25005/redis",
        "task_id": "121554"
    }

    ts = task_status_class(config)
    ts.send_status(ts.START)
