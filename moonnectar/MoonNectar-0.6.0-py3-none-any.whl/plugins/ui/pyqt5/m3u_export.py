import logging

_logger = logging.getLogger(__name__)

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from mnectar.registry import Registry, Plugin
from mnectar.action import Actionable, Action

class M3UMenu(Plugin, Actionable, registry=Registry.UI.PyQt.Menu):
    ...

class M3UExport:
    def view2m3u8(self, pointer):
        ...


