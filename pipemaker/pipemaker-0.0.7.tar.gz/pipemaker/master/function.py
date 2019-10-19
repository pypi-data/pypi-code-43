import inspect
from graphviz import Digraph
import dill as pickle
import base64

import logging
log = logging.getLogger()

from .config import config
from .init import db
from ..master import pipeline
from ..utils.dotdict import dotdict
from ..filesystem.filepath import Filepath

from ..worker.task import Task
from ..queues.taskq import Taskq
from ..queues.eventq import onCompleteAll

output2function = pipeline.output2function

class Function:
    """
    Wrap a function that generates tasks to be executed
    """
    def __init__(self, func):
        """
        :param func:    function to wrap
        """
        self.func = func

        # output path. required here as pipeline uses it as a unique id
        sig = inspect.signature(func)
        if sig.return_annotation!=inspect._empty:
            # return annotation
            self.oname = sig.return_annotation
        elif self.func.__name__.startswith("make_"):
            # function name
            self.oname = self.func.__name__[len("make_"):]

        # function parameters. set manually if needed for upstream tasks.
        self.params = dotdict()

        # set save=False to allow function to manage saving
        self.save = True

        self.taskq = Taskq()

    def __repr__(self):
        """ :return func(**params)->output """
        params = ",".join(str(p) for p in inspect.signature(self.func).parameters.values())
        return f"{self.func.__name__}({params})->{repr(self.parse_output())}"


    def __call__(self, *args, **kwargs):
        """ called in same way as underlying function would be called e.g. make_thing(5, a=3)

        :param config.mode: s=sync, a=async, b=block=async+wait
        """
        if config.pathvars.job == "default":
            log.warning("config.pathvars.job is set to default")

        # check output exists
        self.output = self.parse_output()
        if self.output.exists():
            if config.mode=="a":
                return
            else:
                self.outdata = self.output.load()
                return self.outdata

        # parse inputs, upstream and missing_params
        self.inputs = self.parse_inputs(*args, **kwargs)
        self.get_upstream()
        self.worker = self.get_worker()

        # execute
        if config.mode=="s":
            return self.run_s()
        elif config.mode=="a":
            self.run_a()
        else:
            raise Exception("Invalid config.mode")

    def run_s(self):
        """ run sync """
        if self.missing_params:
            raise Exception(f"Missing inputs {self.missing_params}")
        for v in self.upstream_tasks:
            v()
        log.info(f"creating {repr(self.output)}")
        self.outdata = self.worker.run()
        return self.outdata

    def run_b(self):
        """ run upstream async and block until current complete """
        onCompleteAll.clear()
        config.mode = "a"
        for v in self.upstream_tasks.values():
            v()
        onCompleteAll.wait()
        config.mode = "b"
        return self.run_s()

    def run_a(self):
        """ run async """

        # if already running or in queue then don't add again
        existing = db(db.task.url==self.output.url).select().first()
        if existing and existing.status not in ["onCompleteAll", "failed", "failed_missing", "failed_upstream"]:
            return

        # add to database
        pickled = pickle.dumps(self.worker)
        encoded = base64.b64encode(pickled)
        task = db.task.insert(url=self.output.url, job=config.pathvars.job, name=self.output.name,
                              status="pending", details="", task=encoded)
        task = db.task[task]

        # missing_params
        if self.missing_params:
            task.update_record(status="failed_missing", details=self.missing_params)
            downstream = [w.task for w in db(db.waiting.awaiting == task.url).select()]
            for taskid in downstream:
                db(db.task.id == taskid).update(status="failed_upstream", details=f"missing_params {self.missing_params}")
            db.commit()
        # upstream
        elif self.upstream_tasks or self.pending_files:
            task.update_record(status="waiting")

            for fp in self.pending_files:
                db.waiting.insert(task=task, awaiting=fp)

            for t in self.upstream_tasks:
                db.waiting.insert(task=task, awaiting=t.parse_output().url)
                t()
            db.commit()
        # ready
        else:
            task.update_record(status="ready")
            # commit before push to task queue
            db.commit()
            self.taskq.put(pickled, encoded=True)

        return self

    def parse_output(self):
        """ path to output file """
        path = config.paths.get(self.oname, config.path)
        config.pathvars.name = self.oname
        path = path.format(**config.pathvars)
        return Filepath(path)

    def parse_inputs(self, *args, **kwargs):
        """ return inputs

        :param args:    args passed to function at runtime
        :param kwargs:  kwargs passed to function at runtime
        :return:        dict of name=value where value is parameter value or filepath

        inputs are populated from:

            * runtime args/kwargs
            * task parameter e.g. mytask.params.input1=2
            * global parameter e.g. config.params.input=2
            * default parameter e.g. def myfunc(input1=2)

        if none of the above then filepath:

            * global filepath e.g. config.paths.myglobalfile="myglobalfile.pkl"
            * config.path populated from config.pathvars and parameter name (this is the most common usage)
        """

        if config.pathvars.job is None:
            raise Exception("Set config.pathvars.job which is used for file locations")

        # run_time args and arguments as passed above.
        sig = inspect.signature(self.func)

        # map *args, **kwargs onto signature. partial allows some to be missing_params.
        bind = sig.bind_partial(*args, **kwargs)
        arguments = bind.arguments
        self.twostar = len(bind.kwargs) > 0

        # fill any missing_params parameters from pipe or filepath
        for k, v in sig.parameters.items():
            # can only fill named parameters so ignore *args and **kwargs
            if not str(v).startswith("*"):
                arguments.setdefault(k, self.parse_input(k, v))

        return arguments

    def get_upstream(self):
        """ convert filepaths to upstream tasks """

        # flatten arguments and kwargs
        arguments = self.inputs.copy()
        if self.twostar:
            k, v = list(arguments.items())[-1]
            del arguments[k]
            arguments.update(v)

        # get todo_lists = tasks, str(filepath), params
        self.upstream_tasks = []
        self.pending_files = []
        self.missing_params = []
        queued = db.df("task")
        queued = queued[~queued.status.str.startswith("failed")].url.to_list()
        for k,v in arguments.items():
            if not isinstance(v, Filepath) or v.exists():
                continue
            task = output2function.get(k)
            if task:
                self.upstream_tasks.append(task)
            elif v.url in queued:
                self.pending_files.append(v.url)
            else:
                self.missing_params.append(k)

    def parse_input(self, k, v):
        """ populate parameters not passed in args/kwargs """
        # task parameter e.g. mytask.param.input1=2
        if k in self.params:
            return self.params[k]
        # global parameter
        if k in config.params:
            return config.params[k]
        # compile_time default e.g. def myfunc(input1=2)
        if v.default != inspect._empty:
            return v.default

        # Filepath
        path = config.paths.get(k, config.path)
        config.pathvars.name = k
        path = path.format(**config.pathvars)
        return Filepath(path)

    def get_worker(self):
        """ return only what is needed for execution """
        return Task(self.func, self.inputs, self.output, self.twostar, save=self.save)

    def reset(self):
        """ remove output to force step to rerun """
        output = self.parse_output()

        task = db(db.task.url == output.url).select().first()
        if task:
            if task.status=="running":
                raise Exception("Cannot reset a running task. Wait for it to complete or start pipemaker")
            task.delete_record()
            waiting = [waiting.task for waiting in db(db.waiting.awaiting == output.url).select()]
            waiting = [db.task[t].url for t in waiting]
            log.warning(f"The following downstream tasks are waiting for the reset task:\n{waiting}")
            db.commit()

        try:
            output.remove()
        except FileNotFoundError:
            pass

        return self

    def view(self, g=None, parents=False):
        """ return graphviz display of upstream pipeline

        :param g: existing graph. passed recursively to view parents
        :param parents: False views tasks that need to be run. True views all upstream tasks
        """
        # create graph on first call
        if g is None:
            g = Digraph(strict=True, comment=f'{self.func.__name__} pipeline')

        # display formats
        func_style = dict(shape="oval", style="filled", fillcolor="lightgrey")
        exists_style = dict(shape="folder", height=".1", width=".1", style="filled", fillcolor="lightgreen")
        missing_style = dict(shape="folder", height=".1", width=".1", style="")
        pexists_style = dict(shape="box", style="filled", fillcolor="lightgreen")
        pmissing_style = dict(shape="box", style="")

        # function
        g.node(self.func.__name__, **func_style)

        # inputs
        inputs = self.parse_inputs()
        for k,v in inputs.items():
            if isinstance(v, Filepath):
                if v.exists():
                    g.node(k, **exists_style)
                    g.edge(k, self.func.__name__)
                    if parents:
                        pw = output2function.get(k)
                        if pw is not None:
                            pw.view(g, parents)
                else:
                    upstream = output2function.get(k)
                    if upstream:
                        # no file but a task can create it
                        upstream.view(g, parents)
                        g.edge(k, self.func.__name__)
                    else:
                        # no parameter. no file. no task to create it.
                        g.node(k, **pmissing_style)
                        g.edge(k, self.func.__name__)
            else:
                # supplied parameter
                g.node(k, **pexists_style)
                g.edge(k, self.func.__name__)

        # output
        output = self.parse_output()
        if output.exists():
            g.node(output.name, **exists_style)
        else:
            g.node(output.name, **missing_style)

        g.edge(self.func.__name__, output.name)

        return g
