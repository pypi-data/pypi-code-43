import logging

# Change the log level for the pyqtconsole.qt module
# ... because it has an INFO level message which we don't want displayed every time
logging.getLogger('pyqtconsole.qt').setLevel('WARNING')

from PyQt5               import QtCore
from PyQt5               import QtGui
from PyQt5               import QtWidgets
from PyQt5.QtCore        import Qt
from pyqtconsole.console import PythonConsole, InputArea
from mnectar.ui.pyqt5    import Dockable

import Registry.UI.PyQt

_logger = logging.getLogger('mnectar.'+__name__)

class PyConsole(QtWidgets.QWidget, Dockable, Registry.Plugin,
        registry    = Registry.UI.PyQt.Docked,
        menu        = 'View',
        menu_name   = 'Python Console',
        menu_key    = "Ctrl+P",
        location    = Qt.RightDockWidgetArea):

    def __init__(self, *arg, **kw):
        super().__init__(*arg, **kw)

        self.config_ui()

    def config_ui(self):

        # Create the console widget
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.console = PythonConsole(self)
        self.verticalLayout.addWidget(self.console)

        # Make the application available for debugging
        self.console.push_local_ns('app', self.window().app)

        # Evaluate the console in its own thread (non-blocking)
        self.console.eval_in_thread()

        # Shut down the console on app exit
        self.window().app.ui.uiapp.aboutToQuit.connect(self.console.exit)

        # Install an event filter
        self.installEventFilter(self)

    def eventFilter(self, source, event):
        # Ignore shortcut keys mappings when this field is active.
        # ... If this is not set, shortcuts interfere with typing!
        if (
            event.type() == QtCore.QEvent.ShortcutOverride
            and not (event.modifiers() & QtCore.Qt.ControlModifier)
            and not (event.modifiers() & QtCore.Qt.AltModifier)
            and not (event.modifiers() & QtCore.Qt.MetaModifier)
        ):
            event.accept()
        return super().eventFilter(source, event)
