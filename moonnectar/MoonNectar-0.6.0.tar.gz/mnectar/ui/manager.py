import abc
import logging

from ..config import Configurable
from ..registry import Plugin, Registry

_logger = logging.getLogger(__name__)

class UI(Registry, Configurable, parent=Registry):
    @classmethod
    def create_config(cls, parser):
        try:
            import Registry.UI.GuiPyQt
            default=Registry.UI.GuiPyQt._optname
        except ImportError as ex:
            _logger.warning(f"PyQt Load Error: {ex}", exc_info=True)
            import Registry
            default=Registry.UI.UiPlugin._optname

        parser.add_argument('-U', '--user-interface',
                action  = 'store',
                dest    = 'ui',
                choices = cls.ui_list(),
                default = default,
                help    = "Specify the user interface")

    @classmethod
    def ui_list(cls):
        return [_._optname for _ in cls.plugins]

    @classmethod
    def get_ui(cls, name):
        uis = {_._optname: _ for _ in cls.plugins}
        return uis[name]

    @classmethod
    def create(cls, app, name=None):
        """
        Create the specified user interface given its name.
        """
        if name is None:
            name = app.config.ui

        if name not in cls.ui_list():
            _logger.critical(f"Attempt to create unknown UI '{name}'.  Available Choices: {', '.join(cls.ui_list())}")
        elif hasattr(app, 'ui'):
            _logger.exception(f"Attempt to create UI '{name}' when '{cls.ui.optname}' is already in use!")
        else:
            app.ui = cls.get_ui(name)(app=app)
            app.ui.init()
            return app.ui

class UiPlugin(Plugin, registry=UI):
    """
    Both a base class for UI entry points and an empty UI for when no UI is used.
    """

    _optname = "None"

    def __init_subclass__(self, optname=None, **kw):
        super().__init_subclass__(**kw)
        self._optname = optname

    def init(self):
        """
        Initialize the user interface.

        This is separate from the class constructor as other UI components
        may rely on the user interface object.
        """
        pass

    def run(self):
        "Run the user interface main loop"
        ...

