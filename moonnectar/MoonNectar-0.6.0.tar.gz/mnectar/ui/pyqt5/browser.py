import logging

_logger = logging.getLogger(__name__)

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import Qt

from mnectar.action import Action, Actionable
from mnectar.config import Setting
from mnectar.registry import Registry, Plugin

from .PlaylistDetail_UI import Ui_PlaylistDetail


class BrowserContainer(QtWidgets.QStackedWidget):
    def __init__(self, *arg, **kw):
        super().__init__(*arg, **kw)

    def create(self, widget_class):
        obj = widget_class(parent=self, app=self.window().app)
        index = self.addWidget(obj)

        return obj


class BrowserPlugin(Plugin, Actionable, registry=None):
    show_state = Setting(default=False)
    act_show_browser = Action(
        "View",
        "Browser",
        "Unknown",
        "",
        setting=show_state,
        checkable=True,
        exclusive=True,
    )

    @property
    def model(self):
        return self.window().app.ui.browser_model

    def __init_subclass__(self, menu_name="", menu_key="", **kw):
        super().__init_subclass__(**kw)
        self._menu_name = menu_name
        self._menu_key = menu_key

    def __init__(self, *arg, **kw):
        super().__init__(*arg, **kw)

        self.act_show_browser.name = self._menu_name
        self.act_show_browser.shortcut_default = self._menu_key

        self.config_ui()

    def config_ui(self):
        pass

    @act_show_browser.triggered
    def show_browser(self, state):
        if state:
            self.parent().setCurrentWidget(self)


class DefaultBrowser(
    QtWidgets.QWidget,
    BrowserPlugin,
    registry=Registry.UI.PyQt.Browsers,
    menu_name="Default Browser",
    menu_key="Ctrl+1",
):
    search_string = None
    default_search = Setting(default="")
    search_delay = Setting(default=50)

    def config_ui(self):
        self.ui = Ui_PlaylistDetail()
        self.ui.setupUi(self)

        self.ui.playlist_view.setName("Library")
        self.ui.playlist_view.setModel(self.model)

        self.ui.playlist_view.sortByColumn(0, Qt.AscendingOrder)

        self.ui.search.textEdited.connect(self.on_filter)

        self.ui.search.setText(self.default_search)

        self.filter_timer = QtCore.QTimer()
        self.filter_timer.setSingleShot(True)
        self.filter_timer.timeout.connect(self.on_filter_delay)

        self.on_filter(self.default_search)

        # FIXME Once a changeable central widget exists, this should be made more generic
        # FIXME Possibly change this to playing / resuming the previous track played
        # self.window().app.signal.playAfter.emit(self.model.playlist.pointer(0))

    def on_filter(self, searchstr):
        self.search_string = searchstr

        # Delay filtering the playlist
        # ... because re-filtering on every character typed is needlessly time consuming
        # ... a small delay won't be noticed and improves perormance significantly
        if not self.filter_timer.isActive():
            self.filter_timer.start(self.search_delay)

    def on_filter_delay(self):
        self.model.filter(self.search_string)
        self.default_search = self.search_string
