import inspect
import types

# dict(output=function) map output to function that can produce it
output2function = dict()

def make(*args, **kwargs):
    """ decorator that wraps a function to create a Function """
    from .function import Function

    def inner(f):
        task = Function(f, *args, **kwargs)
        #if no oname then cannot be turned into path
        if not hasattr(task, "oname"):
            return f
        # store so tasks can search for upstream tasks to make their inputs.
        output2function[task.oname] = task
        return task
    return inner

def make_all(module):
    """ create Function for each function in a module; and replace references in locals() with the Function.
    """
    # update module (import module)
    for k, v in module.__dict__.items():
        if isinstance(v, types.FunctionType) and v.__module__ == module.__name__:
            setattr(module, k, make()(v))

    # update locals (from module import *)
    frame = inspect.currentframe()
    try:
        for k,v in frame.f_back.f_locals.items():
            if not k.startswith("_") and isinstance(v, types.FunctionType) and v.__module__ == module.__name__:
                frame.f_back.f_locals[k] =  make()(v)
    finally:
        del frame