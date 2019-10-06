import logging

from PyQt5               import QtWidgets
from PyQt5               import QtCore
from PyQt5.QtCore        import Qt

from .PlaybackControl_UI import Ui_PlaybackControl
from .Dockable           import Dockable

_logger = logging.getLogger(__name__)

class PlaybackControl(QtWidgets.QWidget, Dockable,
        location=Qt.TopDockWidgetArea):

    DOWN_DELAY = 100

    play_pause_block_next = False

    def __init__(self, *arg, **kw):
        super().__init__(*arg, **kw)

        self.ui = Ui_PlaybackControl()
        self.ui.setupUi(self)
        self.config_ui()

    def config_ui(self):
        self.ui.PlayPause .toggled.connect(self.on_play_pause)
        self.ui.Stop      .clicked.connect(self.on_stop)
        self.ui.Next      .clicked.connect(self.on_next)
        self.ui.Prev      .clicked.connect(self.on_previous)

        self.window().app.signal.stopped       .connect(self.on_stopped_ext)
        self.window().app.signal.playing       .connect(self.on_playing_ext)
        self.window().app.signal.paused        .connect(self.on_paused_ext)
        self.window().app.signal.mmkey_playNext.connect(self.on_next_external)
        self.window().app.signal.mmkey_playPrev.connect(self.on_prev_external)
        self.window().app.signal.mmkey_togglePause.connect(self.on_togglePause_external)

    def on_playing_ext(self, mrl, length):
        if not self.ui.PlayPause.isChecked() and not self.ui.PlayPause.isDown():
            self.ui.PlayPause.setDown(True)
            QtCore.QTimer.singleShot(self.DOWN_DELAY, self.on_playing_delay)

    def on_paused_ext(self):
        if self.ui.PlayPause.isChecked() and not self.ui.PlayPause.isDown():
            self.ui.PlayPause.setDown(True)
            QtCore.QTimer.singleShot(self.DOWN_DELAY, self.on_pause_delay)

    def on_next_external(self):
        self.ui.Next.setDown(True)
        QtCore.QTimer.singleShot(self.DOWN_DELAY, self.on_next_delay)

    def on_prev_external(self):
        self.ui.Prev.setDown(True)
        QtCore.QTimer.singleShot(self.DOWN_DELAY, self.on_prev_delay)

    def on_togglePause_external(self):
        self.ui.PlayPause.setDown(True)
        QtCore.QTimer.singleShot(self.DOWN_DELAY, self.on_togglePause_delay)

    def on_togglePause_delay(self):
        self.ui.PlayPause.setDown(False)
        if self.ui.PlayPause.isChecked():
            self.ui.PlayPause.blockSignals(True)
            self.ui.PlayPause.setChecked(False)
            self.ui.PlayPause.blockSignals(False)
        else:
            self.ui.PlayPause.blockSignals(True)
            self.ui.PlayPause.setChecked(True)
            self.ui.PlayPause.blockSignals(False)

    def on_next_delay(self):
        self.ui.Next.setDown(False)

    def on_prev_delay(self):
        self.ui.Prev.setDown(False)

    def on_pause_delay(self):
        if self.ui.PlayPause.isDown():
            self.ui.PlayPause.setDown(False)
            # This method is for synchonization with the rest of the app
            # ... so block signals when changing the checked state
            # ... or any behavior around the button might trigger!
            self.ui.PlayPause.blockSignals(True)
            self.ui.PlayPause.setChecked(False)
            self.ui.PlayPause.blockSignals(False)

    def on_playing_delay(self):
        if self.ui.PlayPause.isDown():
            self.ui.PlayPause.setDown(False)
            # This method is for synchonization with the rest of the app
            # ... so block signals when changing the checked state
            # ... or any behavior around the button might trigger!
            self.ui.PlayPause.blockSignals(True)
            self.ui.PlayPause.setChecked(True)
            self.ui.PlayPause.blockSignals(False)

    def on_stopped_ext(self):
        # This method is for synchonization with the rest of the app
        # ... so block signals when changing the checked state
        # ... or any behavior around the button might trigger!
        self.ui.PlayPause.blockSignals(True)
        self.ui.PlayPause.setChecked(False)
        self.ui.PlayPause.blockSignals(False)

    def on_play_pause(self, state):
        self.play_pause_block_next = True
        if state:
            self.window().app.signal.play.emit()
        else:
            self.window().app.signal.pause.emit()

    def on_next(self):
        self.play_pause_block_next = True
        self.window().app.signal.playNext.emit()

    def on_previous(self):
        self.play_pause_block_next = True
        self.window().app.signal.playPrev.emit()

    def on_stop(self):
        self.window().app.signal.stop.emit()
