# -*- coding: utf-8 -*-
from drummer.messages import Response, StatusCode

class Task:
    """Base class for tasks.

    This class is subclassed by user-defined tasks.

    Attributes:
        config (dict): Environment configuration.
        logger (object): Logger object.
    """

    def __init__(self, config, logger):
        """Object initialization."""

        self.config = config
        self.logger = logger

    def run(self, args):
        raise NotImplementedError
