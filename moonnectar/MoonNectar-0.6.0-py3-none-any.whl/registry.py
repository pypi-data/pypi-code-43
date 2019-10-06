from pregistry import Plugin as _Plugin
from pregistry import Registry as _Registry
from .config   import Configurable
from .config   import Setting

class Registry(_Registry, base=True):
    _entry_point_group = 'mnectar.plugins'
Registry.import_enable()


class Plugin(_Plugin, registry=Registry):
    app = None
    def __init__(self, app=None, *arg, **kw):
        self.app = self.app or app
        super().__init__(*arg, **kw)


class Storage(Registry, parent=Registry):
    ...

class Control(Registry, parent=Registry):
    @classmethod
    def create(cls, app):
        if not app.config.plugins_disabled:
            if not hasattr(app, 'controllers'):
                app.controllers = {}
            for plugin in cls.plugins:
                app.controllers[plugin.path] = plugin(app=app)
                app.controllers[plugin.path].enable()

class Playlist(Registry, parent=Registry):
    ...

class Backend(Registry, Configurable, parent=Registry):
    @classmethod
    def create_config(cls, parser):
        parser.add_argument('-b', '--backend',
                action  = 'store',
                default = 'VLC',
                choices = ['None','VLC','Mock'],
                help    = "Specify the backend player type")

    @classmethod
    def create(cls, app):
        if app.config.backend == 'VLC':
            app.backend = Registry.Backend.BackendVLC(app=app)
            app.backend.enable()
        elif app.config.backend == 'Mock':
            app.backend = Registry.Backend.BackendMock(app=app)
            app.backend.enable()
        elif app.config.backend == 'None':
            pass
        else:
            pass


class PluginSetting(Setting):
    """
    Identical to the Setting class, except designed to work with plugins.
    The default key (if none is specified) is taken from the plugin registry path
    instead of the module name.

    Example
    --------
        >>> class Foo(Registry):
        ...     pass
        >>> class BarPlugin(Plugin, registry=FooRegistry):
        ...     my_setting = PluginSetting()
        >>> x = BarPlugin()
        >>> f"{x.path}.my_setting"
        Registry.Foo.BarPlugin.my_setting

    The above value is equivalent to the setting key
    """

    def _getkey(self, instance):
        if self.userkey is not None:
            return self.userkey
        else:
            return f"{instance.path}.{self.name}"

