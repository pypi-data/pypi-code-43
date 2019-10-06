import logging

_logger = logging.getLogger(__name__)

import functools

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from mnectar.action import Actionable


class ActionCreator(QtCore.QObject):
    def __init__(self, *arg, app=None, **kw):
        super().__init__(*arg, **kw)
        self.app = app

        if self.app is not None and not hasattr(self.app, "_actionable_instances"):
            self.app._actionable_instances = []

    def create_menu_actions(self, menu):
        parent = self
        actions = []

        for obj in self.app._actionable_instances:
            actions.extend(obj.actionables.values())

        actions.sort(
            key=lambda _: (
                *[
                    (menu, "") if not _.menu.endswith(menu) else (menu, _.group)
                    for menu in _.menu.split("|")
                ],
                (_.name, ""),
            )
        )

        qgroups = {}

        prev = None

        for action in actions:
            if action.name:
                parent_menu = menu
                for submenu in action.menu.split("|"):
                    submenu_obj = parent_menu.findChild(
                        QtWidgets.QMenu, submenu, QtCore.Qt.FindDirectChildrenOnly
                    )
                    if not submenu_obj:
                        submenu_obj = QtWidgets.QMenu(submenu, parent=parent_menu)
                        submenu_obj.setObjectName(submenu)
                        parent_menu.addMenu(submenu_obj)
                    parent_menu = submenu_obj

                if (
                    prev
                    and (
                        action.menu.startswith(prev.menu)
                        or prev.menu.startswith(action.menu)
                    )
                    and prev.group != action.group
                ):
                    parent_menu.addSeparator()

                qaction = QtWidgets.QAction(action.name, parent_menu)
                qaction.setCheckable(action.checkable)

                if action.shortcut:
                    qaction.setShortcut(action.shortcut)

                if action.group:
                    if not action.group in qgroups:
                        group = QtWidgets.QActionGroup(self)
                        qgroups[action.group] = group
                    else:
                        group = qgroups[action.group]
                    group.setExclusive(action.exclusive)
                    group.addAction(qaction)

                if action.menu:
                    parent_menu.addAction(qaction)

                if action.checkable:
                    qaction.setChecked(action.is_checked())

                qaction.triggered.connect(action.on_triggered)
                action._qaction = qaction

                action.set_shortcut_change_callback(
                    functools.partial(self.update_sequence, action, qaction)
                )

                prev = action

    def update_sequence(self, action, qaction, sequence):
        qaction.setShortcut(QtGui.QKeySequence.fromString(sequence))
