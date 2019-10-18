import importlib
import inspect
import logging
import pkgutil
from enum import Enum
from enum import unique


@unique
class MWStep(Enum):
    BEFORE = 'before'
    AFTER = 'after'


class Middleware(object):
    """Base class for creating middlewares"""

    def __repr__(self):
        return self.__module__ + '.' + self.__class__.__name__

    def before(self, context):
        """This hook is called before generating the pages"""
        raise NotImplementedError

    def after(self, context):
        """This hook is called after generating the pages"""
        raise NotImplementedError

    def process(self, step, context):
        """This function dispatches the call to the correct hook.
            In case the hook doesn't exist, the unmodified context is returned.
        """
        try:
            context = getattr(self, step.value)(context)
            if context is None:
                logging.warning('Middleware %s: Step "%s" is not returning context. Context will be None.',
                                self,
                                step.value)
            return context
        except NotImplementedError:
            logging.debug('Skipping middleware %s, step "%s" not implemented', self, step.value)
            return context


class MWLoader(object):
    """Class responsible for loading and executing the middlewares"""

    def __init__(self, mw_path):
        self.middleware_chain = []
        logging.debug('Looking for middleware under folder "%s"', mw_path)
        self.load_middleware(str(mw_path))

    def load_middleware(self, package):
        """Loads the chain of middlewares"""
        # Try to load middlewares folder as package
        try:
            mw_package = importlib.import_module(package)
        except ImportError:
            logging.info('Folder "%s" not found. Usage of middleware skipped.', package)
            return

        # Extract classes of each module in the middlewares package
        for _, mw_module_name, is_pkg in pkgutil.iter_modules(mw_package.__path__, mw_package.__name__ + '.'):
            if not is_pkg:
                mw_module = importlib.import_module(mw_module_name)
                mw_classes = inspect.getmembers(mw_module, inspect.isclass)
                for (_, mwc) in mw_classes:
                    # If the class is a subclass of middleware, add the middleware to the chain
                    if issubclass(mwc, Middleware) and (mwc is not Middleware):
                        logging.debug('Found middleware %s.%s', mwc.__module__, mwc.__name__)
                        self.middleware_chain.append(mwc())

    def execute_chain(self, step, context):
        """Executes the chain of middlewares"""
        logging.info('Executing step "%s" of middleware(s) ...', step.value)
        for mw in self.middleware_chain:
            logging.debug("Executing middleware %s", mw)
            context = mw.process(step, context)
        return context
