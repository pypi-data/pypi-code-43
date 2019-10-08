"""Logger factory abstraction

The provided AbstractLoggerFactory has to be implemented as a base class
for your project's classes. That way, all your objects will have a `logger`
property which is in fact a `logging.Logger`
"""

from ._constants import Level

import abc
import logging


class AbstractLoggerFactory(metaclass=abc.ABCMeta):
    """Base factory for loggers

    It provides a set of abstract methods for the various configuration
    parameters, and is intended to return one different logger per calling
    class.
    """

    def __init__(self, callerType):
        """Constructor

        Parameters
        ----------
        callerType: type
            The ClaLogger child's type having invoked this factory
        """
        self._callerType = callerType
        self._logger = None

    @property
    def logger(self):
        """The python logger

        It is created and configured if not yet done

        Returns
        -------
        logging.Logger
        """
        if self._logger is None:
            name = '.'.join([
                self._callerType.__module__,
                self._callerType.__name__
            ])
            logger = logging.getLogger(name)
            logger = self.configureLogger(logger)
            self._logger = logger
        return self._logger

    def configureLogger(self, logger):
        """Configure the logger and returns it

        Parameters
        ----------
        logger: logging.Logger
            The logger who's has only his name configured

        Returns
        -------
        logging.Logger
            The fully configured logger
        """
        if isinstance(self.level, Level):
            logger.setLevel(self.level.value)
        elif isinstance(self.level, [int, str]):
            logger.setLevel(self.level)
        self.setupHandlers(logger)
        return logger

    @property
    @abc.abstractmethod
    def level(self):
        """The factory's level

        Returns
        -------
        A `clalogger.Level` value, or a `logging` level constant (str or int)
        """
        raise NotImplementedError

    @abc.abstractmethod
    def setupHandlers(self, logger):
        """Instanciates the handlers

        You have to instanciate handlers provided in the clalogger.handlers
        module. It will automatically associate the level and add them to the
        logger

        Parameters
        ----------
        logger: logging.Logger

        Returns
        -------
        None
        """
        raise NotImplementedError
