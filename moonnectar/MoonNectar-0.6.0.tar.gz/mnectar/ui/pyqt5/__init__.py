import Registry


class PyQt(Registry, parent=Registry.UI):
    ...


class Docked(Registry, parent=PyQt):
    @classmethod
    def create_all(cls, app, parent):
        if not hasattr(app.ui, "docked"):
            app.ui.docked = {}
        for plugin in cls.plugins:
            app.ui.docked[plugin.path] = plugin(app=app, parent=parent)


class Browsers(Registry, parent=PyQt):
    @classmethod
    def create_all(cls, app, parent):
        if not hasattr(app.ui, 'browser_widgets'):
            app.ui.browser_widgets = {}
        for plugin in cls.plugins:
            app.ui.browser_widgets[plugin.path] = app.ui.browser.create(plugin)


class Menu(Registry, parent=PyQt):
    @classmethod
    def create_all(cls, app, parent):
        if not hasattr(app.ui, "menu_widgets"):
            app.ui.menu_widgets = {}
        for plugin in cls.plugins:
            app.ui.menu_widgets[plugin.path] = plugin(app=app, parent=parent)
            app.ui.menu_widgets[plugin.path].enable()


class Settings(Registry, parent=Registry.UI.PyQt):
    pass


from .Dockable       import Dockable
from .QPlaylistModel import QPlaylistModel
from .QPlaylistView  import QPlaylistView
from .action         import Action
from .roles          import UserRoles
from .htmldelegate   import HTMLDelegate
