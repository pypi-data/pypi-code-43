import importlib
import inspect
import logging

from django.conf import settings

from aorta.model.eda.provider import EventListenerProvider
from aorta.model.cqrs.provider import CommandHandlerProvider


class AutoDiscoverMixin:
    ignored_apps = ['aorta.ext.django']
    logger = logging.getLogger('aorta.environment')

    def autodiscover(self):
        """Inspect ``settings.INSTALLED_APPS`` to import message
        handler classes.
        """
        for app in settings.INSTALLED_APPS:
            if app in self.ignored_apps:
                continue
            qualname = f'{app}.{self.handlers_import_module}'
            try:
                handlers = importlib.import_module(qualname)
                self.logger.debug("Imported handlers module %s", qualname)
            except ImportError:
                continue
            classes = inspect.getmembers(handlers, inspect.isclass)
            for name, cls in classes:
                if not issubclass(cls, self.handler_base_class):
                    continue
                self.add(cls)
                self.logger.debug("Registered handler class %s",
                    cls.__name__)


class DjangoEventListenerProvider(AutoDiscoverMixin, EventListenerProvider):
    """Implements the :meth:`EventListenerProvider.autodiscover()``
    method to discover event listener classes from Django apps.
    """
    handlers_import_module = 'listeners'


class DjangoCommandHandlerProvider(AutoDiscoverMixin, CommandHandlerProvider):
    """Implements the :meth:`CommandHandlerProvider.autodiscover()``
    method to discover command handler classes from Django apps.
    """
    handlers_import_module = 'handlers'
