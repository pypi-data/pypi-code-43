""" Define Task interface. """
import uuid
import time
import json
import logging


class Task:
    """ Task is produced by brokers and refer to an handler registed
    by a consumer.

    If an exception occure during the task processing, task result is set to
    {"exception": str(exception)}
    """

    def __init__(self, task_id, name, params, created_at, finished_at, result):
        self.task_id = task_id
        self.name = name
        self.params = params
        self.created_at = created_at
        self.finished_at = finished_at
        self.result = result

    @classmethod
    def new(cls, name, params):
        """ Get a task instance. """
        task_id = str(uuid.uuid4())
        created_at = int(time.time())
        return cls(task_id, name, params, created_at, None, None)

    @property
    def done(self):
        """ Bool - task is over. """
        return self.finished_at is not None

    def set_result(self, result):
        """ Set a result to a task.

        :param result: json serializable.
        :raises:
        """
        self.finished_at = int(time.time())
        if isinstance(result, Exception):
            self._set_result_exception(result)
        else:
            try:
                json.dumps(result)
            except TypeError:
                exception = ValueError("Task result is not serializable")
                logging.error(f"{result} is not serializable")
                self._set_result_exception(exception)
            else:
                self.result = result

    def _set_result_exception(self, exception):
        """ Result is an exception.

        :param Exception exception:
        """
        self.result = {"exception": {"class": exception.__class__.__name__,
                                     "args": exception.args,
                                     "str": str(exception)}}

    @classmethod
    def load(cls, dump):
        """ Load Task from a dump. """
        return cls(**json.loads(dump))

    def dump(self):
        """ Serialization. """
        return json.dumps({
            "task_id": self.task_id,
            "name": self.name,
            "params": self.params,
            "created_at": self.created_at,
            "finished_at": self.finished_at,
            "result": self.result,
        })

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.dump())

    def __hash__(self):
        return hash(self.task_id) + hash(self.finished_at)
