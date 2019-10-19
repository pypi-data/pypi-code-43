from pipemaker.queues.rabbitq import Rabbitq

class Logq(Rabbitq):
    """ receive log messages from all processes
    """
    name = "log_queue"