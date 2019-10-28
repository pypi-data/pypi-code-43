import abc


class Command(object):

    def __init__(self):
        pass

    @abc.abstractmethod
    def execute(self):
        pass