
def is_rpc(command):
    """
    Decorate a function to signal it is a WCraaS RPC function and provide its command.

    >>> @is_rpc("awesome_command")
    ... def func(): pass
    ...
    >>> func.is_rpc
    True
    >>> func.rpc_command
    'awesome_command'
    """
    def decorator(fn):
        fn.is_rpc = True
        fn.rpc_command = command
        return fn
    return decorator

def consume(queue_name):
    """
    Decorate a function to signal it is a WCraaS consumer and provide its queue name.

    >>> @consume("awesome_queue")
    ... def func(): pass
    ...
    >>> func.is_consume
    True
    >>> func.consume_queue
    'awesome_queue'
    """
    def decorator(fn):
        fn.is_consume = True
        fn.consume_queue = queue_name
        return fn
    return decorator
