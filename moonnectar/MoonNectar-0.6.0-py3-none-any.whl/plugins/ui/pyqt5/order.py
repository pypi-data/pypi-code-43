import logging

_logger = logging.getLogger(__name__)

from functools import partial
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from mnectar.registry import Plugin, Registry
from mnectar.config import Setting, Configurable
from mnectar.action import Action, Actionable
from mnectar.util.signal import Signal

import Registry.UI.PyQt.Menu


class OrderMenu(QtCore.QObject, Plugin, Configurable, Actionable, registry=Registry.UI.PyQt.Menu):
    order = Setting('playback.order', default='Linear')

    action_linear        = Action("Playback|Order", "order", "Linear",        "Ctrl+L", checkable = True, exclusive = True, setting = order, args = ("Linear",       ), )
    action_random        = Action("Playback|Order", "order", "Random",        "Ctrl+R", checkable = True, exclusive = True, setting = order, args = ("Random",       ), )
    action_random_album  = Action("Playback|Order", "order", "Random Album",  "",       checkable = True, exclusive = True, setting = order, args = ("RandomAlbum",  ), )
    action_random_artist = Action("Playback|Order", "order", "Random Artist", "",       checkable = True, exclusive = True, setting = order, args = ("RandomArtist", ), )

    def enable(self):
        self.setOrder(self.order)

    @action_linear.triggered
    @action_random.triggered
    @action_random_album.triggered
    @action_random_artist.triggered
    def setOrder(self, agent):
        order_manager = self.app.controllers.get('Registry.Control.OrderManager', None)
        if order_manager:
            order_manager.agent = agent
