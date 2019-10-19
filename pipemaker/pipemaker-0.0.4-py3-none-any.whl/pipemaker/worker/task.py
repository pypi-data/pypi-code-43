from ..filesystem.filepath import Filepath
from ..utils.dotdict import dotdict
from ..utils.defaultlog import log
from ..queues.eventq import Eventq
import inspect

import multiprocess as mp
from datetime import datetime


class Task:
    """
    minimal executable that gets passed to task queue

    * load data, run function, save result (all run locally).
    * trigger events to be actioned on master or elsewhere.
    """
    def __init__(self, func, inputs, output, twostar, **kwargs):
        """
        :param module: module that contains func
        :param func: function to be executed
        :param inputs: data or filepaths to be loaded
        :param output: filepath
        :param twostar: if True then last parameter is \*\*kwargs. Filepaths within this will be expanded.
        :param kwargs: parameters to control runtime, taskid etc..
        """
        self.module = func.__module__
        self.func = func.__name__
        self.inputs = inputs
        self.output = output
        self.twostar = twostar
        self.kwargs = kwargs

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.output.path

    def run(self):
        """ execute in worker_process process """
        self.eventq = Eventq()
        try:
            self.load()
            self.execute()
            self.save()
            self.onEvent("onComplete")
        except Exception as e:
            log.exception(f"exception in {self.output.path}\ne")
            self.onEvent("onError", exception=e)
            return

        return self.outdata

    def load(self):
        """ load data from filepaths """
        self.onEvent("onLoading")

        if not self.inputs:
            self.indata = dict()
            return

        load_dict = lambda param_dict: {k:v.load() if isinstance(v, Filepath) else v for k,v in param_dict.items()}

        # load data except **kwargs
        self.indata = load_dict(self.inputs)

        # load and unpack kwargs
        # todo why not do this always for final var if dict; or all dicts?
        if self.twostar:
            k, v = list(self.inputs.items())[-1]
            kwargs = load_dict(v)
            # unpack
            del self.indata[k]
            self.indata.update(kwargs)

    def execute(self):
        """ import module and execute function """
        self.onEvent("onRunning")
        from importlib import import_module
        module = import_module(self.module)
        func = getattr(module, self.func)

        # In immediate mode on single machine then import will return the MaterTask wrapper.
        if hasattr(func, "func"):
            self.outdata = func.func(**self.indata)
        else:
            self.outdata = func(**self.indata)

    def save(self):
        """ save data to filepath """
        self.onEvent("onSaving")
        if self.kwargs.get("save", True):
            self.output.save(self.outdata)

    def onEvent(self, event, **kwargs):
        """ send event message

        :param event: string e.g. "onError"
        :param kwargs: optional event data e.g. time, process, url
        """
        kwargs = dotdict(kwargs)
        kwargs.time = datetime.now()
        kwargs.event = event
        kwargs.process = mp.current_process().name
        kwargs.url = self.output.url
        self.eventq.put(kwargs)

#####################################################################

def onEvent(event, **kwargs):
    """ fire event from task function via workertask wrapper """
    self = inspect.currentframe().f_back.f_back.f_locals['self']
    return self.onEvent(event, **kwargs)

def progress(i, total):
    """ reports progress at iteration i/total """
    self = inspect.currentframe().f_back.f_back.f_locals['self']
    # every 1%. +1 avoids div zero exception
    if i % (total // 100 + 1) == 0:
        self.onEvent("onProgress", progress=i * 100 // total)

