import logging

class SoftConfDbLogger(object):

    supported = ['debug', 'info', 'warning', 'error', 'critical', 'exception']

    def __init__(self, username=None):
        self.setUsername(username)
        self.lb_logger = logging.getLogger()

    def setUsername(self, username=None):
        if username:
            self.username = username
        else:
            self.username = 'NoAuth'

    def __getattr__(self, attr):
        def wrapper(*args, **kwargs):
            if attr in self.supported:
                msg = "[%s]%s" % (self.username, args[0])
                return getattr(self.lb_logger, attr)(msg, *args[1:], **kwargs)
            return getattr(self.lb_logger, attr)(*args, **kwargs)
        if not attr in self.supported or not hasattr(self.lb_logger, attr):
            return super(SoftConfDbLogger, self).__getattr__(attr)
        return wrapper
