import logging

from PyQt5           import QtWidgets
from PyQt5           import QtCore
from PyQt5.QtCore    import pyqtSignal
from PyQt5.QtCore    import Qt
from mnectar.config  import Setting

from mnectar.action import Action, Actionable

_logger = logging.getLogger(__name__)


class Dockable(Actionable):
    __doc__ = """The Dockable class indicates a normal widget which can be docked.
    This class also acts as a registry of all dockable widgets for GUI plugin
    registration.
    """

    _DOCKABLE_WIDGETS = []

    _dock_location   = Setting()
    _dock_show_state = Setting(default=False)

    _dock_show_action = Action("View", "", "Unknown", "", setting=_dock_show_state, checkable = True)

    def __init_subclass__(cls,
            location  = Qt.RightDockWidgetArea,
            menu      = None,
            menu_name = "",
            menu_key  = "",
            features  = QtWidgets.QDockWidget.DockWidgetMovable|QtWidgets.QDockWidget.DockWidgetMovable,
            areas     = Qt.AllDockWidgetAreas,
            **kw):

        super().__init_subclass__(**kw)

        cls._DOCKABLE_WIDGETS.append(cls)
        cls._dock_menu       = menu
        cls._dock_menu_name  = menu_name
        cls._dock_menu_key   = menu_key
        cls._dock_defloc     = location
        cls._dock_features   = features
        cls._dock_areas      = areas

    def make_dock_widget(self, parent):
        """Convert this widget into a docked widget.
        The specified parent must be able to accept dock widgets!"""

        self.dock_widget_obj = QtWidgets.QDockWidget(parent)
        self.dock_widget_obj.setAllowedAreas(self._dock_areas)
        self.dock_widget_obj.setFeatures(self._dock_features)
        self.dock_widget_obj.setWidget(self)
        self.dock_widget_obj.setObjectName(f"{self.__class__.__name__}:Docked")
        self.dock_widget_obj.dockLocationChanged.connect(self._onDockLocationChanged)

        self.dock_widget_obj.titleWidget = QtWidgets.QWidget(self.dock_widget_obj)

        title = self.dock_widget_obj.titleWidget
        title.layout = QtWidgets.QHBoxLayout(title)
        title.layout.setSpacing(0)
        title.layout.setContentsMargins(0,10,0,0)
        title.setStyleSheet("""
            .QWidget {
                border-bottom: 1px solid #999;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #EEE, stop: 0.3 #AAA, stop: 0.6 #999099, stop: 1 #998899);
            }
            """)

        self.dock_widget_obj.setTitleBarWidget(self.dock_widget_obj.titleWidget)

        parent.addDockWidget(
                self._dock_location or self._dock_defloc,
                self.dock_widget_obj)

    def _onDockLocationChanged(self, location):
        self._dock_location = location

    @QtCore.pyqtSlot()
    def _dock_toggle(self):
        if not hasattr(self, 'dock_widget_obj'):
            self.make_dock_widget(self.window())

        if self.dock_widget_obj.isVisible():
            self._dockShow(False)
        else:
            self._dockShow(True)

    @_dock_show_action.triggered
    def _dockShow(self, state):
        if not hasattr(self, 'dock_widget_obj'):
            self.make_dock_widget(self.window())

        self.dock_widget_obj.setVisible(state)
        self._dock_show_state = state

    def __init__(self, *arg, **kw):
        super().__init__(*arg, **kw)

        self._dock_show_action.name             = self._dock_menu_name
        self._dock_show_action.shortcut_default = self._dock_menu_key

        if self._dock_show_state is True:
            self._dockShow(self._dock_show_state)
