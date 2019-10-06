import logging

_logger = logging.getLogger(__name__)

import inspect
import pathlib

from contextlib import contextmanager
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

from mnectar.config import Setting


class ProxyProperty:
    def setting(self, instance):
        return instance.__dict__.get(self.name)[0]

    def instance(self, instance):
        return instance.__dict__.get(self.name)[1]

    def owner(self, instance):
        return instance.__dict__.get(self.name)[1].__class__

    def __set_name__(self, owner, name):
        self.name = name

    def __init__(self, default=None):
        self.default = default

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return self.setting(instance).__get__(self.instance(instance), self.owner(instance))

    def __set__(self, instance, value):
        if isinstance(value, tuple) and inspect.isdatadescriptor(value[0]):
            instance.__dict__[self.name] = value
        else:
            self.setting(instance).__set__(self.instance(instance), value)


class AutoSettingMixin:
    proxy = ProxyProperty()

    @property
    def setting(self):
        return self.__dict__.get('proxy')[0]

    @property
    def instance(self):
        return self.__dict__.get('proxy')[1]

    def __init__(self, setting, instance, *arg, **kw):
        super().__init__(*arg, **kw)
        self.proxy = (setting, instance)


class SettingFilename(QtWidgets.QGroupBox, AutoSettingMixin):
    def __init__(self, setting, instance, *arg, **kw):
        super().__init__(setting=setting, instance=instance, *arg, **kw)
        self.config_ui()

    def config_ui(self):
        self.layout   = QtWidgets.QHBoxLayout(self)
        self.filename = QtWidgets.QLineEdit(self)
        self.choose   = QtWidgets.QPushButton("Select ...", self)

        self.layout.addWidget(self.filename)
        self.layout.addWidget(self.choose)

        self.setTitle(self.setting.help)
        self.filename.setReadOnly(True)
        self.filename.setText(str(self.proxy))

        self.choose.clicked.connect(self.on_choose)

    def on_choose(self):
        newfile, filter = QtWidgets.QFileDialog.getSaveFileName(
            self,
            self.setting.help,
            self.filename.text(),
            "JSON Library Database (*.json)",
            options=QtWidgets.QFileDialog.DontConfirmOverwrite
        )
        if newfile:
            self.filename.setText(newfile)
            self.proxy = newfile

class SettingBool(QtWidgets.QWidget, AutoSettingMixin):
    def __init__(self, setting, instance, *arg, **kw):
        super().__init__(setting=setting, instance=instance, *arg, **kw)
        self.config_ui()

    def config_ui(self):
        self.layout = QtWidgets.QHBoxLayout(self)
        self.state  = QtWidgets.QCheckBox(self)

        self.layout.addWidget(self.state)
        self.state.setText(self.setting.help)
        self.state.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.state.setChecked(self.proxy)
        self.state.toggled.connect(self.on_changed)

    def on_changed(self, state):
        self.proxy = state


class SettingStringList(QtWidgets.QGroupBox, AutoSettingMixin):
    def __init__(self, setting, instance, add_remove=False, up_down=False, *arg, **kw):
        super().__init__(setting=setting, instance=instance, *arg, **kw)
        self.add_remove = add_remove
        self.up_down = up_down
        self.config_ui()

    def _hspacer(self):
        return QtWidgets.QSpacerItem(
            40, 20, hPolicy=QtWidgets.QSizePolicy.Expanding
        )

    def _vspacer(self):
        return QtWidgets.QSpacerItem(
            20, 40, vPolicy=QtWidgets.QSizePolicy.Expanding
        )

    def config_ui(self):
        self.layout = QtWidgets.QGridLayout(self)
        self.paths  = QtWidgets.QListView(self)
        self.model  = SettingListModel(self.setting, self.instance, parent=self)

        self.setTitle(self.setting.help)
        self.layout.addWidget(self.paths, 0, 0, 3, 3)

        if self.add_remove:
            self.add    = QtWidgets.QPushButton("Add",    self)
            self.remove = QtWidgets.QPushButton("Remove", self)

            self.layout.addWidget      (self.remove, 3, 0)
            self.layout.addItem        (self._hspacer(), 3, 1)
            self.layout.addWidget      (self.add, 3, 2)
            self.add   .clicked.connect(self.on_add)
            self.remove.clicked.connect(self.on_remove)
            self.remove.setEnabled     (False)

        if self.up_down:
            self.up   = QtWidgets.QPushButton("Up",   self)
            self.down = QtWidgets.QPushButton("Down", self)

            self.layout.addWidget      (self.up, 0, 3)
            self.layout.addItem        (self._vspacer(), 1, 3)
            self.layout.addWidget      (self.down, 2, 3)
            self.up    .clicked.connect(self.on_up)
            self.down  .clicked.connect(self.on_down)
            self.up    .setEnabled     (False)
            self.down  .setEnabled     (False)

        self.paths.setModel(self.model)
        self.paths.selectionModel().selectionChanged.connect(self.on_selection_changed)

    def on_selection_changed(self, selected, deselected):
        if self.add_remove:
            if len(self.paths.selectionModel().selectedIndexes()) > 0:
                self.remove.setEnabled(True)
            else:
                self.remove.setEnabled(False)

        if self.up_down:
            selected = self.paths.selectionModel().selectedIndexes()
            if len(selected) == 1:
                if selected[0].row() > 0:
                    self.up.setEnabled(True)
                else:
                    self.up.setEnabled(False)
                if selected[0].row() < len(self.proxy)-1:
                    self.down.setEnabled(True)
                else:
                    self.down.setEnabled(False)
            else:
                self.up.setEnabled(False)
                self.down.setEnabled(False)

    @contextmanager
    def _layout_change_manager(self):
        try:
            # Send a signal that the layout will be changing
            self.model.layoutAboutToBeChanged.emit([], self.model.VerticalSortHint)

            # Save the old persistent index list
            # ... so they can be updated later
            old_persist_list = self.model.persistentIndexList()
            old_index_rows = [_.row() for _ in old_persist_list]
            old_index_values = [self.proxy[_] for _ in old_index_rows]

            yield
        finally:
            # Create the new persistent index objects

            if len(old_persist_list) > 0:
                new_index_rows = [self.proxy.index(_) for _ in old_index_values]
                new_persist_list = [self.model.index(_, 0) for _ in new_index_rows]

                self.model.changePersistentIndexList(old_persist_list, new_persist_list)

            self.model.layoutChanged.emit([], self.model.VerticalSortHint)

    def on_up(self):
        selected = self.paths.selectionModel().selectedIndexes()
        if len(selected) == 1:
            old    = selected[0].row()
            new    = selected[0].row()-1
            oldidx = selected[0]
            newidx = self.model.index(selected[0].row()-1, 0)
            value  = self.proxy[selected[0].row()]
            self.model.removeRow(selected[0].row())
            self.model.insertRow(selected[0].row()-1)
            self.model.setData(self.model.index(selected[0].row()-1, 0), value)
            self.paths.selectionModel().select(oldidx, QtCore.QItemSelectionModel.Deselect)
            self.paths.selectionModel().select(newidx, QtCore.QItemSelectionModel.Select)

    def on_down(self):
        selected = self.paths.selectionModel().selectedIndexes()
        if len(selected) == 1:
            old    = selected[0].row()
            new    = selected[0].row()+1
            oldidx = selected[0]
            newidx = self.model.index(selected[0].row()+1, 0)
            value  = self.proxy[selected[0].row()]
            self.model.removeRow(old)
            self.model.insertRow(new)
            self.model.setData(newidx, value)
            self.paths.selectionModel().select(oldidx, QtCore.QItemSelectionModel.Deselect)
            self.paths.selectionModel().select(newidx, QtCore.QItemSelectionModel.Select)

    def on_add(self):
        self.model.insertRow(len(self.proxy))

    def on_remove(self):
        indexes = self.paths.selectionModel().selectedIndexes()
        for index in sorted(indexes, key=lambda _:_.row(), reverse=True):
            self.model.removeRow(index.row())
        self.remove.setEnabled(False)


class SettingPathList(SettingStringList):
    def __init__(self, setting, instance, *arg, **kw):
        super().__init__(
            setting    = setting,
            instance   = instance,
            add_remove = True,
            *arg,
            **kw
        )

    def config_ui(self):
        super().config_ui()
        self.paths.setSelectionMode(self.paths.ExtendedSelection)

    def on_add(self):
        newfile = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            self.setting.help,
            str(pathlib.Path.home()/"Music"),
        )
        if newfile:
            existing = self.proxy
            if not newfile in existing:
                existing.append(newfile)
                existing.sort()
                self.model.modelAboutToBeReset.emit()
                self.proxy = existing
                self.model.endResetModel()


class SettingStringEntry(SettingStringList):
    def __init__(self, setting, instance, *arg, **kw):
        super().__init__(
            setting    = setting,
            instance   = instance,
            add_remove = True,
            up_down    = True,
            *arg,
            **kw
        )


class LibrarySettings(QtWidgets.QWidget):
    def __init__(self, app=None, *arg, **kw):
        super().__init__(*arg, **kw)

        self.app = app

        settings = dict(
            inspect.getmembers(
                self.app.library.__class__,
                predicate=lambda _: isinstance(_, Setting),
            )
        )

        self.layout = QtWidgets.QVBoxLayout(self)
        self.dbfile = SettingFilename(settings['dbfile'], app.library, parent=self)
        self.scan_at_start = SettingBool(settings['scan_at_start'], app.library, parent=self)
        self.directories = SettingPathList(settings['directories'], app.library, parent=self)
        self.cover_files = SettingStringEntry(settings['cover_files'], app.library, parent=self)
        self.layout.addWidget(self.dbfile)
        self.layout.addWidget(self.scan_at_start)
        self.layout.addWidget(self.directories)
        self.layout.addWidget(self.cover_files)


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, app=None, *arg, **kw):
        self.app = app
        super().__init__(*arg, **kw)

        self.config_ui()

    def config_ui(self):
        self.setWindowTitle("Preferences")
        self.setObjectName("SettingsDialog")
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.tabWidget      = QtWidgets.QTabWidget(self)
        self.buttonBox      = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.verticalLayout.addWidget(self.tabWidget)
        self.verticalLayout.addWidget(self.buttonBox)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.resize(600, 500)

        self.library = LibrarySettings(self.app, self)
        self.tabWidget.addTab(self.library, "Library")

        self.shortcuts = ShortcutSettings(app=self.app, parent=self)
        self.tabWidget.addTab(self.shortcuts, "Shortcuts")

        self.tabWidget.setCurrentIndex(0)


class SettingListModel(QtCore.QAbstractListModel, AutoSettingMixin):
    def __init__(self, setting, instance, parent=None, *arg, **kw):
        super().__init__(setting=setting, instance=instance, *arg, **kw)

    def rowCount(self, parent=None):
        return len(self.proxy)

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            if index.isValid():
                return self.proxy[index.row()]

        return QtCore.QVariant()

    def flags(self, index):
        if index.isValid():
            return super().flags(index) | QtCore.Qt.ItemIsEditable
        else:
            return super().flags(index)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if (
            role == QtCore.Qt.EditRole
            and index.isValid()
            and index.row() < len(self.proxy)
        ):
            current = self.proxy
            current[index.row()] = value
            self.proxy = current
            self.dataChanged.emit(index, index, [QtCore.Qt.DisplayRole])
            return True
        else:
            return False

    def insertRow(self, before, parent=QtCore.QModelIndex()):
        self.insertRows(before, 1, parent)

    def insertRows(self, before, count, parent=QtCore.QModelIndex()):
        self.beginInsertRows(parent, before, before+count-1)
        self.proxy = self.proxy[:before] + [""]*count + self.proxy[before:]
        self.endInsertRows()
        return True

    def removeRow(self, toRemove, parent=QtCore.QModelIndex()):
        self.removeRows(toRemove, 1, parent)

    def removeRows(self, start, count, parent=QtCore.QModelIndex()):
        self.beginRemoveRows(parent, start, start+count-1)
        self.proxy = self.proxy[:start] + self.proxy[start+count:]
        self.endRemoveRows()
        return True


class ShortcutDisplay(QtWidgets.QLineEdit):
    def __init__(self, app, action, *arg, **kw):
        super().__init__(*arg, **kw)
        self.app    = app
        self.action = action
        self.config_ui()

    def config_ui(self):
        self.setReadOnly(True)
        self.setText(self.action.shortcut)

    def mouseReleaseEvent(self, event):
        dlg = QtWidgets.QDialog(self)
        lyt = QtWidgets.QVBoxLayout(dlg)
        seq = QtWidgets.QKeySequenceEdit(dlg)
        btn = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok |
                                         QtWidgets.QDialogButtonBox.Cancel |
                                         QtWidgets.QDialogButtonBox.Reset,
                                         parent=dlg,)
        self.key_display = seq

        lyt.addWidget(seq)
        lyt.addWidget(btn)
        btn.accepted.connect(dlg.accept)
        btn.rejected.connect(dlg.reject)
        btn.clicked .connect(self.on_dlg_reset)
        btn.addButton("Clear", QtWidgets.QDialogButtonBox.ActionRole)
        seq.setKeySequence(QtGui.QKeySequence.fromString(self.action.shortcut))
        dlg.setModal(True)
        dlg.exec_()

        if dlg.result() == dlg.Accepted:
            self.setText(seq.keySequence().toString())
            self.action.shortcut = seq.keySequence().toString()

    def on_dlg_reset(self, button):
        if button.text() == "Reset":
            self.key_display.setKeySequence(QtGui.QKeySequence.fromString(self.action.shortcut_default))
        elif button.text() == "Clear":
            self.key_display.setKeySequence(QtGui.QKeySequence.fromString(""))


class ShortcutSettings(QtWidgets.QWidget):
    def __init__(self, *arg, app=None, **kw):
        super().__init__(*arg, **kw)
        self.app = app

        self.config_ui()

    def config_ui(self):
        self.layout    = QtWidgets.QGridLayout(self)
        self.labels    = []
        self.shortcuts = []
        actions        = []

        for obj in getattr(self.app, "_actionable_instances", []):
            actions.extend(obj.actionables.values())

        actions.sort(key=lambda action: action.name)

        for row,action in enumerate(actions):
            self.labels.append(QtWidgets.QLabel(parent=self, text=action.name))
            self.shortcuts.append(ShortcutDisplay(self.app, action, parent=self))
            self.layout.addWidget(self.labels[-1], row, 0)
            self.layout.addWidget(self.shortcuts[-1], row, 1)

