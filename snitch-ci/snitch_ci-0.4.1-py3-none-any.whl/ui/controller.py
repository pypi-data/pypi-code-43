""" Application entry point """
import logging as log
import json
import pickle
import os.path

from PyQt5.QtCore import Qt, pyqtSlot, QModelIndex
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QFileDialog, QMenu, QAction, QMessageBox, QHeaderView
import pyautogui
from pynput.keyboard import Key

from ..model.data.events import Event
from ..model.data.screenshot import Screenshot
from ..model.eventproperties import EventPropertiesModel, EventPropertiesItemDelegate
from ..model.eventlist import EventList, EventListModel
from ..model.properties import PropertiesTableModel
from ..model.snaplist import SnapListModel, SnapList
from .controller_ui import Ui_Controller
from .about import AboutDialog
from ..recorder import EventRecorder, KeyEventCatcher
from ..player import EventPlayer, SnapshotPlayer
from ..settings import SETTINGS
from ..snapper import Snapper
from .. import FILE_VERSION

class Data:
    #pylint: disable=too-few-public-methods
    TYPES = [pickle, json]
    NAMES = ["Pickle (*.p)", "Json (*.json *.js)"]
    DEFAULT_TYPE = json
    PANES_SIZES = [720, 198]

class Controller(QMainWindow):
    STATUS_TEXT = QApplication.translate('Controller', '{0} events recorded.')
    """ Main window for the app """
    def __init__(self, parent=None):
        super().__init__(parent)

        self._file_version = FILE_VERSION

        self._ui = Ui_Controller()
        self._ui.setupUi(self)

        self._ui.tableEvents.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self._ui.eventSplitter.setSizes(Data.PANES_SIZES)
        self._ui.snapshotSplitter.setSizes(Data.PANES_SIZES)

        self._selected_event = None
        self._selected_snap = None
        self._saved_geometry = None
        self._catch_interrupt = None
        self._save_dir = ''

        self.snap = None

        self._ui.menuAdd = QMenu(self._ui.eventMgmtButtons.ui.buttonAdd)
        for event_type in Event.get_subclasses():
            self._ui.menuAdd.addAction(event_type.__name__)
        self._ui.menuAdd.triggered.connect(self.add_event)
        self._ui.eventMgmtButtons.ui.buttonAdd.setMenu(self._ui.menuAdd)

        self._event_list = EventList(self)
        self._recorder = EventRecorder(self._event_list, parent=self)
        self._player = EventPlayer(self._event_list, parent=self)
        self._ui.tableEvents.setModel(EventListModel(self._event_list, self))
        self._ui.tableEvents.selectionModel().selectionChanged.connect(self.update_selected_event)
        self._ui.tableProperties.setModel(EventPropertiesModel(None, self))
        self._ui.tableProperties.setItemDelegate(EventPropertiesItemDelegate(self))

        self._snap_list = SnapList(self)
        self._snap_player = SnapshotPlayer(self._snap_list, parent=self)

        self._ui.listSnap.setModel(SnapListModel(self._snap_list, self))
        self._ui.listSnap.selectionModel().selectionChanged.connect(self.update_selected_snap)
        self._ui.tableSnapProps.setModel(PropertiesTableModel(None, self))

        self._ui.eventMgmtButtons.ui.buttonDel.clicked.connect(lambda: self._event_list.remove(self._selected_event))
        self._ui.eventMgmtButtons.ui.buttonUp.clicked.connect(self.move_up)
        self._ui.eventMgmtButtons.ui.buttonDown.clicked.connect(self.move_down)

        self._ui.capsEventMgmtButtons.ui.buttonDel.clicked.connect(lambda: self._snap_list.remove(self._selected_snap))

        self._ui.buttonRecord.clicked.connect(self._recorder.start)
        self._ui.buttonStop.clicked.connect(self._recorder.stop)
        self._ui.buttonPlay.clicked.connect(self.playback)
        self._ui.capsEventMgmtButtons.ui.buttonAdd.clicked.connect(self.capture)
        self._ui.buttonClear.clicked.connect(self._event_list.clear)
        self._ui.buttonClear.clicked.connect(self._snap_list.clear)
        self._ui.buttonCapture.clicked.connect(self.capture)
        self._ui.buttonPlaySnaps.clicked.connect(self._snap_player.play)
        self._ui.buttonDiff.clicked.connect(self.diff)

        self._ui.actionMinimizeWhenRecording.toggled.connect(SETTINGS.set_minimize_on_record)

        self._event_list.list_changed.connect(self.update_status)
        self._event_list.list_changed.connect(self.update_selected_event)
        self._snap_list.list_changed.connect(self.update_selected_snap)

        self._status_label = Controller.STATUS_TEXT.format(self._event_list.size())
        self._ui.statustext = QLabel(self._status_label, self._ui.statusbar)
        self._ui.statusbar.addWidget(self._ui.statustext)


######## ##     ## ######## ##    ## ########  ######
##       ##     ## ##       ###   ##    ##    ##    ##
##       ##     ## ##       ####  ##    ##    ##
######   ##     ## ######   ## ## ##    ##     ######
##        ##   ##  ##       ##  ####    ##          ##
##         ## ##   ##       ##   ###    ##    ##    ##
########    ###    ######## ##    ##    ##     ######


    def select_event(self, event):
        """ Selects the row in the table for the event passed as parameter """
        self._ui.tableEvents.selectRow(self._event_list.events.index(event))
        self._ui.tableEvents.scrollTo(self._ui.tableEvents.selectedIndexes()[0])
        # Allows UI update, but may be time consuming, remove if necessary:
        QApplication.processEvents()

    def get_selected_index(self):
        """
        :return: The index of the selected row of the event list,
                 or -1 if the selection is empty
        """
        selected_rows = self._ui.tableEvents.selectionModel().selectedRows()
        if selected_rows:
            # this is ok since the selection mode/behavior is single/rows
            return selected_rows[0].row()
        return -1

    @pyqtSlot()
    def playback(self, include_snapshots=False):
        """ Plays the recorded events """
        keys = [ {Key.esc} ]
        with KeyEventCatcher(keys, self._player.stop) as catcher:
            self._player.play(
                start_at=self.get_selected_index(),
                event_played_callback=self.select_event,
                key_event_catcher=catcher
            )
        if include_snapshots:
            self._snap_player.play()
        else:
            QMessageBox.information(
                self,
                self.tr("Information"),
                self.tr("Sequence playback over.")
            )

    @pyqtSlot()
    def stop_playback(self):
        """ Interrupts the playback """
        self._player.stop()


    @pyqtSlot(QAction)
    def add_event(self, event_type):
        """
        :type event_type: QAction
        """
        self._event_list.insert(self.get_selected_index(), event_type.text())

    @pyqtSlot()
    def move_up(self):
        """ Move selected event up one row """
        self._move(-1)

    @pyqtSlot()
    def move_down(self):
        """ Move selected event down one row """
        self._move(+1)

    def _move(self, direction):
        self._event_list.move(self._selected_event, direction)
        self._ui.tableEvents.selectRow(self.get_selected_index()+direction)

    @pyqtSlot()
    def update_selected_event(self):
        """ Sets the properties table to the selected event """
        item_index = self.get_selected_index()
        if not self._recorder.is_recording:
            if item_index < 0:
                self._event_list.offset = self._event_list.size()
            else:
                self._event_list.offset = item_index+1

        if 0 <= item_index < self._event_list.size():
            self._selected_event = self._event_list.events[item_index]
        else:
            self._selected_event = None

        self._update_control_buttons(item_index)
        self._update_properties()

    def _update_control_buttons(self, index):
        """ Updates enableness of the buttons of the selected event """
        is_event_selected = self._selected_event is not None
        self._ui.eventMgmtButtons.ui.buttonDel.setEnabled(is_event_selected)
        self._ui.eventMgmtButtons.ui.buttonUp.setEnabled(is_event_selected and index > 0)
        self._ui.eventMgmtButtons.ui.buttonDown.setEnabled(is_event_selected and index < self._event_list.size()-1)

    def _update_properties(self):
        """ Updates the property view of the selected event """
        if self._selected_event is not None:
            self._ui.tableProperties.setEnabled(True)
            model = EventPropertiesModel(self._selected_event, self)
            self._ui.tableProperties.setModel(model)
        else:
            self._selected_event = None
            self._ui.tableProperties.setEnabled(False)
            self._ui.tableProperties.setModel(EventPropertiesModel(None, self))

    @pyqtSlot(str)
    def change_event_type(self, new_class):
        """ Change the type of the selected event (may be unsafe) """
        if self._selected_event is not None:
            event = Event.create(new_class, self._selected_event)
            self._event_list.replace(self._selected_event, event)
            self._selected_event = event
            self._update_properties()

    @pyqtSlot(tuple)
    def set_shortcut_modifiers(self, modifiers):
        if self._selected_event is not None:
            self._selected_event.modifiers = modifiers
            self._update_properties() # TODO check if necessary


 ######  ##    ##    ###    ########   ######  ##     ##  #######  ########  ######
##    ## ###   ##   ## ##   ##     ## ##    ## ##     ## ##     ##    ##    ##    ##
##       ####  ##  ##   ##  ##     ## ##       ##     ## ##     ##    ##    ##
 ######  ## ## ## ##     ## ########   ######  ######### ##     ##    ##     ######
      ## ##  #### ######### ##              ## ##     ## ##     ##    ##          ##
##    ## ##   ### ##     ## ##        ##    ## ##     ## ##     ##    ##    ##    ##
 ######  ##    ## ##     ## ##         ######  ##     ##  #######     ##     ######


    def get_selected_snap_index(self):
        """
        :return: The index of the selected row of the snapshot list,
                 or -1 if the selection is empty
        """
        selected_rows = self._ui.listSnap.selectionModel().selectedRows()
        if selected_rows:
            return selected_rows[0].row()
        return -1

    @pyqtSlot()
    def update_selected_snap(self):
        """
        Sets the properties table to the selected snapshot and updates the
        snap preview
        """
        item_index = self.get_selected_snap_index()
        if 0 <= item_index < self._snap_list.size():
            self._selected_snap = self._snap_list.get(item_index)
            img = self._selected_snap.as_image()
            if img is not None:
                self._ui.labelPreview.setPixmap(img)
                self._ui.labelPreview.setScaledContents(True)
        else:
            self._selected_snap = None

        self._update_snap_properties()
        self._update_snap_control_buttons(item_index)

    def _update_snap_control_buttons(self, index):
        """ Updates enableness of the buttons of the selected snapshot """
        is_snap_selected = self._selected_snap is not None
        self._ui.capsEventMgmtButtons.ui.buttonDel.setEnabled(is_snap_selected)
        self._ui.capsEventMgmtButtons.ui.buttonUp.setEnabled(is_snap_selected and index > 0)
        self._ui.capsEventMgmtButtons.ui.buttonDown.setEnabled(is_snap_selected and index < self._snap_list.size()-1)

    def _update_snap_properties(self):
        """ Updates the property view of the selected snapshots """
        if self._selected_snap is not None:
            self._ui.tableSnapProps.setEnabled(True)
            model = PropertiesTableModel(self._selected_snap, self)
            self._ui.tableSnapProps.setModel(model)
        else:
            self._ui.tableSnapProps.setEnabled(False)
            self._ui.tableSnapProps.setModel(EventPropertiesModel(None, self))

    @pyqtSlot()
    def capture(self):
        """ Starts the screen capture sequence """
        QApplication.setOverrideCursor(Qt.CrossCursor)
        self.snap = Snapper()
        self.snap.area_captured.connect(self.save_capture)

    @pyqtSlot(int, int, int, int)
    def save_capture(self, x, y, w, h):
        """ Slot called when the capture is performed """
        self.snap = None

        capture = Screenshot(region=(x, y, w, h))
        capture.do_capture()
        self._snap_list.push(capture)
        self._ui.listSnap.setCurrentIndex(self._ui.listSnap.model().index(self._snap_list.size()-1, 0, QModelIndex()))
        QApplication.restoreOverrideCursor()

    @pyqtSlot()
    def diff(self):
        """ Shows the image diff window for the selected capture """
        selection = self._ui.listSnap.selectedIndexes()
        if selection:
            snap_id = selection[0].row()
            self._snap_player.show_diff(snap_id)


######## #### ##       ########    ##     ##  ######   ##     ## ########
##        ##  ##       ##          ###   ### ##    ##  ###   ###    ##
##        ##  ##       ##          #### #### ##        #### ####    ##
######    ##  ##       ######      ## ### ## ##   #### ## ### ##    ##
##        ##  ##       ##          ##     ## ##    ##  ##     ##    ##
##        ##  ##       ##          ##     ## ##    ##  ##     ##    ##    ###
##       #### ######## ########    ##     ##  ######   ##     ##    ##    ###


    @pyqtSlot()
    def show_save_dialog(self):
        """ Opens the file save dialog """
        filename, filetype = QFileDialog.getSaveFileName(
            self,
            self.tr("Save as"),
            self._save_dir+"/record.json",
            ';;'.join(Data.NAMES),
            dict(zip(Data.TYPES, Data.NAMES))[Data.DEFAULT_TYPE]
        )
        if filename:
            self.save(filename, dict(zip(Data.NAMES, Data.TYPES))[filetype])
            self._save_dir = os.path.dirname(filename)


    def save(self, filename, export_module):
        """
        Saves the event recording into a file
        :param filename: The name of the file
        :param export_module: Either pickle or json
        """
        log.info('Saving %d events into "%s"', self._event_list.size(), filename)
        try:
            file_content = {
                'version': self._file_version,
                'screen': pyautogui.size(),
                **self._event_list.get_serializable(),
                **self._snap_list.get_serializable()
            }
            if export_module == json:
                with open(filename, 'w') as record:
                    log.debug(file_content)
                    json.dump(file_content, record, indent=4, ensure_ascii=False)
            else:
                with open(filename, 'bw') as record:
                    pickle.dump(file_content, record)
        except OSError as ex:
            log.error(str(ex))
            QMessageBox.warning(
                self,
                self.tr("Error"),
                self.tr("An error occured while writing the file: \n")+str(ex)
            )


    @pyqtSlot()
    def show_open_dialog(self):
        """ Opens the file open dialog """
        filename, filetype = QFileDialog.getOpenFileName(
            self,
            self.tr("Open"),
            self._save_dir,
            ';;'.join(Data.NAMES),
            dict(zip(Data.TYPES, Data.NAMES))[Data.DEFAULT_TYPE]
        )
        if filename:
            self._event_list.clear()
            self._snap_list.clear()
            self.load(filename, dict(zip(Data.NAMES, Data.TYPES))[filetype])
            self._save_dir = os.path.dirname(filename)


    def load(self, filename, import_module=json):
        """
        Loads the event recording from a file
        :param filename: The name of the file
        :param import_module: Either pickle or json
        """
        try:
            if import_module == json:
                with open(filename, 'r') as record:
                    data = json.load(record)
                    self.build_list_from_dict(data)
            elif import_module == pickle:
                with open(filename, 'r') as record:
                    file_content = pickle.load(record)
                    self._file_version = file_content['version']
                    self._event_list = file_content['events']
                    self._snap_list = file_content['screenshots']
            else:
                log.error('Unsuported file format: %s', import_module)

            log.info('Loaded %d events from "%s"', self._event_list.size(), filename)
        except OSError as ex:
            log.error(str(ex))
            QMessageBox.warning(
                self,
                self.tr("Error"),
                self.tr("An error occured while reading the file: \n")+str(ex)
            )




    def build_list_from_dict(self, event_list_dict):
        """
        :param event_list_dict: dictionnary of the JSON decoded object
        """
        try:
            self._file_version = event_list_dict['version']
            for event_item in event_list_dict['events']:
                event = Event.create(event_item['type'])
                event.__dict__ = event_item
                self._event_list.push(event)
            self._event_list.list_changed.emit()
            for snap_item in event_list_dict['screenshots']:
                snap = Screenshot()
                snap.__dict__ = snap_item
                self._snap_list.push(snap)
            self._snap_list.list_changed.emit()

        except (KeyError, IndexError) as err:
            log.error("Can't decode file: %s", err)


##     ## ####  ######   ######         ##     ## ####
###   ###  ##  ##    ## ##    ##        ##     ##  ##
#### ####  ##  ##       ##              ##     ##  ##
## ### ##  ##   ######  ##              ##     ##  ##
##     ##  ##        ## ##              ##     ##  ##
##     ##  ##  ##    ## ##    ## ###    ##     ##  ##
##     ## ####  ######   ######  ###     #######  ####


    @pyqtSlot()
    def update_status(self):
        """ Updates the statusbar text on event list change """
        message = self.tr('Event list cleared.')
        if self._event_list.size() > 0:
            message = self.tr('Event added: {0}'.format(self._event_list.events[-1]))
        self._ui.statusbar.showMessage(message, 1000)
        self.update_status_label()

    @pyqtSlot()
    def update_status_label(self):
        """ Updates the default string of the statusbar """
        action = ''
        if self._recorder.is_recording:
            action = self.tr('RECORDING... ')
        self._status_label = action + Controller.STATUS_TEXT.format(self._event_list.size())
        self._ui.statustext.setText(self._status_label)

    @pyqtSlot()
    def show_about_dialog(self):
        """ Opens the information dialog """
        AboutDialog(self).show()
