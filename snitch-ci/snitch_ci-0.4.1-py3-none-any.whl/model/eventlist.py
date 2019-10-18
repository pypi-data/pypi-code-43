import logging as log

from PyQt5.QtCore import Qt, QCoreApplication, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtCore import QVariant

from pynput.keyboard import Key

from .list import ListModel
from .data.events import Event, MouseClick, MouseDoubleClick, \
    TextEntered, KeyPressed

class EventList(QObject):
    """
    Class managing a collection of user input events.
    All items in the list of events must subclass Event
    """
    list_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.events = []
        self.offset = 0

    #region## Elements management
    def push(self, event):
        """
        Adds an event to the list. Merge with the previous event
        when possible.
        :param event: The event to add
        :type event: Any subclass of Event
        """
        #pylint: disable=unidiomatic-typecheck
        if not self.events:
            # ensures no other branch is processed => self.events[-1] can
            # be called safely in other branches
            pass
        elif isinstance(event, TextEntered):
            if isinstance(self.events[self.offset-1], TextEntered):
                self.events[self.offset-1].text += str(event.text)
                event = None
        elif type(event) == KeyPressed:
            if isinstance(self.events[self.offset-1], TextEntered):
                if event.key == Key.space.value.vk:
                    self.events[self.offset-1].text += str(' ')
                    event = None
                elif event.key == Key.backspace.value.vk:
                    self.events[self.offset-1].text = self.events[self.offset-1].text[:-1]
                    event = None
        # type() is used on purpose here, ie we want the real type
        elif type(event) == MouseClick:
            if type(self.events[self.offset-1]) == MouseClick:
                if abs(event.time - self.events[self.offset-1].time) < Event.DOUBLE_CLICK_THRESHOLD:
                    self.events[self.offset-1] = MouseDoubleClick(event.x, event.y)
                    event = None

        if event:
            self.events.insert(self.offset, event)
            self.offset += 1
            log.debug('New offset = %d', self.offset)

        log.debug('Last event: %s. New list size: %d',
            self.events[self.offset-1].__class__.__name__,
            self.size())

        self.list_changed.emit()

    def pop(self):
        """ Removes and returns the last event in the list """
        event = None
        if self.size() > 0:
            self.offset -= 1
            event = self.events[self.offset]
            del self.events[self.offset]
            self.list_changed.emit()
        return event

    @pyqtSlot()
    def clear(self):
        """ Removes all the elements from the list """
        del self.events[:]
        self.list_changed.emit()
    def insert(self, index, event_type):
        if index < 0:
            self.events.append(Event.create(event_type))
        else:
            self.events.insert(index, Event.create(event_type))
        self.list_changed.emit()

    @pyqtSlot(Event)
    def remove(self, event):
        """ Remove event from list """
        if event in self.events:
            self.events.remove(event)
            self.list_changed.emit()
            return True
        return False

    def move(self, event, direction):
        """
        Change event position in list
        :param direction: +1 to move down, -1 to move up
        """
        if event in self.events:
            index = self.events.index(event)
            self.events[index+direction], self.events[index] = self.events[index], self.events[index+direction]
            self.list_changed.emit()
            return True
        return False


    def replace(self, old, new):
        """ Replaces an event in the list by another """
        if old in self.events:
            self.events[self.events.index(old)] = new
            self.list_changed.emit()
            return True
        return False

    def size(self):
        """ :return: The number of events """
        return len(self.events)
    #endregion##

    def get_serializable(self):
        """ :return: this object as a dict """
        return {
            'events': list(map(lambda l: l.__dict__, self.events))
        }


class EventListModel(ListModel):
    """ Model for displaying an EventList in a QTableView """
    HEADERS = [
        QCoreApplication.translate('EventListModel', 'Time'),
        QCoreApplication.translate('EventListModel', 'Type'),
        QCoreApplication.translate('EventListModel', 'Description')
    ]

    def __init__(self, data, parent=None):
        """
        :type data: EventList
        """
        super().__init__(data, parent)
        self._last_col = len(EventListModel.HEADERS)-1

    def columnCount(self, parent):
        #pylint: disable=unused-argument, no-self-use
        """ There's 3 columns in the table: Timestamp, Type and Description string"""
        return 3

    def data(self, index, role=Qt.DisplayRole):
        """
        Returns the data for the specified cell for the specified role
        :param index: The table cell
        :type index: QModelIndex
        :param role: The Qt role of the returned value (only DisplayRole is implemented)
        """
        value = QVariant()
        if role == Qt.DisplayRole:
            event = self._data.events[index.row()]
            col = index.column()
            if col == 0:
                display = event.time
                if index.row() > 0:
                    delay = event.time - self._data.events[0].time
                    if delay < 10000:
                        display = "  +{}ms".format(delay)
                    else:
                        display = "  +{}s".format(round(delay/1000, 1))
                value = display
            elif col == 1:
                value = event.__class__.__name__
            elif col == 2:
                value = str(event)

        return value

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        #pylint: disable=no-self-use
        """ The table column titles """
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return EventListModel.HEADERS[section]
            return section
        return QVariant()
    #endregion##
