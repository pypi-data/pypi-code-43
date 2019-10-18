from PyQt5.QtCore import Qt
from PyQt5.QtCore import QVariant
from PyQt5.QtWidgets import QStyledItemDelegate, QComboBox

from .properties import PropertiesTableModel
from .data.events import Event
from ..ui.modifier_picker import ModifierCheckboxes


class EventPropertiesModel(PropertiesTableModel):
    def __init__(self, event, parent=None):
        """
        :type event: EventList
        """
        super().__init__(event, parent)
        self.event_class_name = event.__class__.__name__

    def data(self, index, role=Qt.DisplayRole):
        """
        Returns the data for the specified cell for the specified role
        :param index: The table cell
        :type index: QModelIndex
        :param role: The Qt role of the returned value (only DisplayRole is implemented)
        """
        row = index.row()
        col = index.column()
        value = QVariant()
        if role in [Qt.DisplayRole, Qt.EditRole]:
            if row == 0:
                value = self.tr('type') if col == 0 else self.event_class_name
            else:
                props = self._dict.copy()
                if 'type' in props:
                    del props['type']

                if col == 0:
                    value = list(props.keys())[row-1]
                elif col == 1:
                    value = list(props.values())[row-1]
                    if isinstance(value, (list, tuple, set)):
                        if role != Qt.EditRole:
                            value = ','.join(value)
        else:
            value = super().data(index, role)

        return value


class EventPropertiesItemDelegate(QStyledItemDelegate):
    """ Class handling the cell edition of the properties table """

    def createEditor(self, parent, option, index):
        """ Creating the widget used as cell editor """
        # ComboBox only in column 1
        if index.column() == 1 and index.row() == 0:
            # Create the combobox and populate it
            comboType = QComboBox(parent)
            comboType.addItems(list(map(lambda l: l.__name__, Event.get_subclasses())))
            # asserting self.parent is a Controller
            comboType.currentTextChanged.connect(self.parent().change_event_type)
            return comboType

        if index.column() == 1 and isinstance(index.data(Qt.EditRole), (list, tuple, set)):
            checkModifiers = ModifierCheckboxes(parent)
            checkModifiers.values_changed.connect(self.parent().set_shortcut_modifiers)
            return checkModifiers

        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        """ Definfing the data according to the cell editor type """
        if isinstance(editor, QComboBox):
            # get the index of the text in the combobox that matches the current value of the itenm
            current_text = str(index.data(Qt.EditRole))
            cb_index = editor.findText(current_text)
            # if it is valid, adjust the combobox
            if cb_index >= 0:
                editor.blockSignals(True)
                editor.setCurrentIndex(cb_index)
                editor.blockSignals(False)
        elif isinstance(editor, ModifierCheckboxes):
            editor.blockSignals(True)
            editor.set_values(index.data(Qt.EditRole))
            editor.blockSignals(False)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        """ Sets the edited data to the model """
        if isinstance(editor, QComboBox):
            # save the current text of the combo box as the current value of the item
            model.setData(index, editor.currentText(), Qt.EditRole)
        elif isinstance(editor, ModifierCheckboxes):
            model.setData(index, editor.values(), Qt.EditRole)
        else:
            super().setModelData(editor, model, index)
