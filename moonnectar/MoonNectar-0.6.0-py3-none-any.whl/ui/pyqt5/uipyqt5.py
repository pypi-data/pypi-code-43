import functools
import sys
import logging

from PyQt5 import QtWidgets

from .MainWindow import MainWindow
from .pyqtsignal import QSignalControl
from .QPlaylistModel import QPlaylistModel
from .ActionCreator import ActionCreator
from mnectar.util import oscheck
from mnectar.config import Setting
from mnectar.library.view import Selected

import Registry.UI

_logger = logging.getLogger(__name__)


class GuiPyQt(Registry.UI.UiPlugin, registry=Registry.UI, optname="pyqt"):
    def __init__(self, app=None, *arg, **kw):
        super().__init__(app=app, *arg, **kw)

        # Flag indicating the PyQt5 GUI is in use
        # ... useful for plugins to determine if they should load
        self.pyqt5 = True

        self.app.signal.pyqt = QSignalControl(self.app)

        # Create the application
        self.uiapp = QtWidgets.QApplication([sys.argv])

    @oscheck(target="Darwin")
    def macos_disable_tab_bar(self):
        """
        Disable MacOS automatic tab bar functionality, which can only occur via the
        native interface.
        """
        try:
            import AppKit
            AppKit.NSWindow.setAllowsAutomaticWindowTabbing_(False)
        except ImportError:
            pass

    def patch_setting(self):
        """
        patch the Setting class to work with PyQt objects so that the app instance can
        be stored in the main window object without necessarily needing to store it in
        each instance.
        """

        def pyqt_getSettingManager(function):
            @functools.wraps(function)
            def wrapper(self, instance, app=None):
                if isinstance(instance, QtWidgets.QWidget):
                    app = instance.window().app
                else:
                    app = None
                return function(self, instance, app=app)
            return wrapper

        Setting._getSettingManager = pyqt_getSettingManager(Setting._getSettingManager)

    def init(self):
        # TODO: PyQt5 v5.13.1+: New Exit Scheme
        #       ... A new exit cleanup scheme was added to cleanup (among other things)
        #       ... clipboard bugs on app exit.  This should be come standard in
        #       ... PyQt5 v5.14.x.
        # TODO: Remove these lines with PyQt5 v5.14.x
        from PyQt5.QtCore import pyqt5_enable_new_onexit_scheme
        pyqt5_enable_new_onexit_scheme(True)

        # Cleanup macos behavior
        self.macos_disable_tab_bar()

        # Patch the Setting class to work better with PyQt
        self.patch_setting()

        # Get the library content
        self.library_view = self.app.library.content.records

        # Setup the selected records view
        self.selected = Selected(self.library_view)

        # Create the main window
        self.main = MainWindow(self.app)

        # Set the main window as active in the application
        self.uiapp.setActiveWindow(self.main)

        # Create the global library browser model
        self.browser_model = QPlaylistModel(self.app)

        # Create all browser widgets
        Registry.UI.PyQt.Browsers.create_all(self.app, self.main)

        # Create all docked plugins
        Registry.UI.PyQt.Docked.create_all(self.app, self.main)

        # Create all menu plugins
        Registry.UI.PyQt.Menu.create_all(self.app, self.main)

        # Create all auto actions
        self.action_manager = ActionCreator(self.main, app=self.app)
        self.action_manager.create_menu_actions(self.main.ui.menubar)

    def run(self):
        # Run the application event loop
        exit_code = self.uiapp.exec_()

        # Destroy the backend!
        return exit_code
