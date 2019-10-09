import platform

from logging import getLogger

from pyqalx.config import UserConfig
from pyqalx.core.adapters import QalxBlueprint, QalxBot, QalxGroup, \
    QalxItem, QalxQueue, QalxSet, QalxWorker
from pyqalx.core.log import configure_logging
from pyqalx.core.registry import Registry
from pyqalx.core.tags import Tags
from pyqalx.transport import PyQalxAPI


class QalxSession:
    """The session that any interaction with the API will use."""

    def __init__(self,
                 profile_name="default",
                 config_class=None,
                 skip_ini=False,
                 rest_api_class=None,
                 project_name=None):
        """
        :param profile_name: profile name to get from `config_class` (default="default")
        :type profile_name: str
        :config_class: The class for the config that will be used for this session
        :param skip_ini: Should loading the config from the inifile be skipped
        :type skip_ini: bool
        :param rest_api_class: The class to use for the rest api
        :param tags: A list of dicts for tags that you want to add to every
                     entity that is added/saved during this session
        :type tags: list
        """

        if config_class is None:
            config_class = UserConfig
        self.config = config_class()
        """an instance of the `config_class` (default=pyqalx.config.UserConfig())"""
        if not skip_ini:
            self.config.from_inifile(profile_name)

        configure_logging(self.config)
        if rest_api_class is None:
            rest_api_class = PyQalxAPI
        self.rest_api = rest_api_class(self.config)
        self._registry = Registry()
        self._registry._register_defaults()
        self.tags = Tags([], rest_api=self.rest_api)
        if project_name:
            self.tags.add(name="project_name", value=project_name)

    def __setattr__(self, key, value):
        if key == 'tags' and hasattr(self, 'tags'):
            # The user is completely replacing the tags.
            # Attempt to validate them before replacing them.
            self.tags._validate(value)
        return super(QalxSession, self).__setattr__(key, value)

    @property
    def log(self):
        return getLogger('pyqalx.integration')

    def _update_config(self, config):
        """
        Method to use if the config needs to be updated after the session has
        been created.  Used when creating a `~bot.Bot` as a `QalxSession`
        needs to be created using a `BotConfig` and then update it with the
        token the `~bot.Bot` needs to use to interact with the
        `~entities.Queue`.
        Also updates the rest_api with the updated config

        :param config:
        :return:
        """
        self.config.update(config)
        self.rest_api = self.rest_api.__class__(self.config)

    def register(self, cls):
        self._registry.register(cls)

    def unregister(self, cls):
        self._registry.unregister(cls)

    @property
    def _host_info(self):
        return {
            "node": platform.node(),
            "platform": platform.platform(),
            # TODO: add more platform and IP address infos
        }

    @property
    def item(self):
        """
        returns a :class:`~pyqalx.core.adapters.item.QalxItem` adapter for this session

        :return: pyqalx.core.adapters.item.QalxItem
        """
        return QalxItem(self)

    @property
    def set(self):
        """
        returns a :class:`~pyqalx.core.adapters.set.QalxSet` adapter for this session

        :return: pyqalx.core.adapters.set.QalxSet
        """
        return QalxSet(self)

    @property
    def group(self):
        """
        returns a :class:`~pyqalx.core.adapters.group.QalxGroup` adapter for this session

        :return: pyqalx.core.adapters.group.QalxGroup
        """
        return QalxGroup(self)

    @property
    def queue(self):
        """
        returns a :class:`~pyqalx.core.adapters.queue.QalxQueue` adapter for this session

        :return: pyqalx.core.adapters.queue.QalxQueue
        """
        return QalxQueue(self)

    @property
    def bot(self):
        """
        returns a :class:`~pyqalx.core.adapters.bot.QalxBot` adapter for this session

        :return: pyqalx.core.adapters.bot.QalxBot
        """
        return QalxBot(self)

    @property
    def worker(self):
        """
        returns a :class:`~pyqalx.core.adapters.worker.QalxWorker` adapter for this session

        :return: pyqalx.core.adapters.worker.QalxWorker
        """
        return QalxWorker(self)

    @property
    def blueprint(self):
        """
        returns a :class:`~pyqalx.core.adapters.blueprint.QalxBlueprint` adapter for this session

        :return: pyqalx.core.adapters.blueprint.QalxBlueprint
        """
        return QalxBlueprint(self)
