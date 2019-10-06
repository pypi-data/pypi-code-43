import inspect
import time

from strategery.exceptions import TaskError, StrategyError
from strategery.logging import BypassLogger
from strategery.strategy import get_strategy

logger = BypassLogger()

def execute(*args, targets, preprocessed):
    if type(preprocessed) is list or type(preprocessed) is tuple:
        # Convert lists/tuples to type-indexed dictionary
        preprocessed = { type(p): p for p in preprocessed }

    queue = get_strategy(targets, start=None, preprocessed=preprocessed)

    print("Processing strategy:", file=logger)
    for stage in queue:
        print([t.__name__ for t in stage],
              file=logger)
    print("\n", file=logger)

    # Populate with preprocessed
    processed = preprocessed

    for stage in queue:
        for task in stage:
            if task not in processed:
                try:
                    ts = time.time()

                    __assert_task_type(task)

                    dependencies = tuple()
                    if hasattr(task, "dependencies"):
                        dependencies = tuple([processed[d] for d in task.dependencies])

                    __assert_task_parameters(task, dependencies)

                    processed[task] = task(*dependencies)
                    te = time.time()
                    print('[%2.2f sec] Processed: %r ' % (te - ts, task.__name__),
                          file=logger)
                except Exception as e:
                    raise TaskError('Stategery failed at task {t}, found at "{f}:{l}".\n\nInner error:\n{et}: {e}'.format(
                        t=task.__name__,
                        et=type(e).__name__,
                        e=e,
                        f=inspect.getmodule(task).__file__,
                        l=task.__code__.co_firstlineno
                    ))

    return tuple([processed[t] for t in targets])

def __assert_task_type(task):
    if not inspect.isfunction(task) and not inspect.isclass(task):
        raise Exception("Task cannot be processed, '{t}' is not a function or a class.".format(t=task.__name__))


def __assert_task_parameters(task, dependencies):
    while hasattr(task, "original_function"):
        task = task.original_function
    signature = inspect.signature(task)
    if len(signature.parameters) != len(dependencies):
        raise StrategyError("Stategery task {t} expects parameters {p}, we have parameters {d}".format(
            t=task.__name__,
            p=[k for k in signature.parameters.keys()],
            d=[d.__name__ if hasattr(d, "__name__") else type(d)
               for d in dependencies]
        ))
