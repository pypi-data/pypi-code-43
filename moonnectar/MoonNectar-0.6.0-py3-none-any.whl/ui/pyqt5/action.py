import logging

from PyQt5        import QtWidgets

_logger = logging.getLogger(__name__)

class Action(QtWidgets.QAction):
    def __init__(self, text,
            parent      = None,
            icon        = None,
            checkable   = False,
            checked     = False,
            shortcut    = None,
            separator   = False,
            onTriggered = None,
            onToggled   = None):
        super().__init__(text, parent)

        if separator:
            self.setSeparator(True)
        else:
            self.setCheckable(checkable)

            if checkable:               self.setChecked(checked)
            if icon is not None:        self.setIcon(icon)
            if shortcut is not None:    self.setShortcut(shortcut)
            if onTriggered is not None: self.triggered.connect(onTriggered)
            if onToggled is not None:   self.toggled.connect(onToggled)

