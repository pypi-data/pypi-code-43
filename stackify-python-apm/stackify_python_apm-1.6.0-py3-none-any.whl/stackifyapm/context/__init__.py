def init_execution_context():
    try:
        from stackifyapm.context.contextvars import execution_context
    except ImportError:
        from stackifyapm.context.threadlocal import execution_context

    return execution_context
