import logging

from PyQt5               import QtWidgets
from PyQt5               import QtCore
from .MainWindow_UI      import Ui_MainWindow
from .PlaybackControl    import PlaybackControl
from .PlaybackStatusText import PlaybackStatusCoverText
from .PlaybackStatusText import PlaybackStatusText
from .browser            import BrowserContainer
from .settings           import SettingsDialog
from mnectar.registry    import Registry
from mnectar.config      import Setting

_logger = logging.getLogger(__name__)

class MainWindow(QtWidgets.QMainWindow):
    savedState    = Setting(default = False)
    savedGeometry = Setting(default = False)

    def __init__(self, app=None, *arg, **kw):
        super().__init__(*arg, **kw)
        self.app = app

        self.ui  = Ui_MainWindow()
        self.ui.setupUi(self)

        self.config_ui()

        self.show()

        self.app.signal.initComplete.connect(self.onInitComplete)

    def onInitComplete(self):
        if self.savedGeometry:
            self.restoreGeometry(self.savedGeometry)
        if self.savedState:
            self.restoreState(self.savedState)

    def closeEvent(self, event):
        _logger.debug("Close Event ... saving window state")
        self.savedGeometry = self.saveGeometry().data()
        self.savedState    = self.saveState().data()

    def config_ui(self):
        self.ui.playbackcontrol = PlaybackControl(self)
        self.ui.playbackcontroldock = self.ui.playbackcontrol.make_dock_widget(self)

        self.ui.playbackstatus = PlaybackStatusCoverText(self)
        self.ui.playbackstatusdock = self.ui.playbackstatus.make_dock_widget(self)

        self.ui.browser = self.app.ui.browser = BrowserContainer(parent=self)
        self.setCentralWidget(self.app.ui.browser)

        self.menus = {}

        self.settings_action = QtWidgets.QAction("settings", self)
        self.settings_action.triggered.connect(self.show_settings)
        self.settings_menu = self.ui.menubar.addMenu("settings")
        self.settings_menu.addAction(self.settings_action)

    def show_settings(self):
        obj = SettingsDialog(self.app, self)
        obj.exec_()

    def addMenuItem(self, menu_name, name, action, shortcut=None):
        menu = self.getMenu(menu_name)

        menu.addAction(name, action, shortcut)

    def getMenu(self, menu_name):
        menu = self.ui.menubar.findChild(QtWidgets.QMenu, menu_name, QtCore.Qt.FindDirectChildrenOnly)
        if not menu:
            menu = self.ui.menubar.addMenu(menu_name)
            menu.setObjectName(menu_name)
        return menu
