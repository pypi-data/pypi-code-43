import os
import logging

from PyQt5               import QtCore
from PyQt5               import QtGui
from PyQt5               import QtWidgets
from PyQt5.QtCore        import Qt
from mnectar.formats     import MRL

from .PlaybackStatusText_UI      import Ui_PlaybackStatusText
from .PlaybackStatusCoverText_UI import Ui_PlaybackStatusCoverText
from .Dockable                   import Dockable

_logger = logging.getLogger(__name__)

class PlaybackStatusText(QtWidgets.QWidget, Dockable,
        location=Qt.TopDockWidgetArea):

    def __init__(self, *arg, **kw):
        super().__init__(*arg, **kw)

        self.config_ui()

    def config_ui(self):
        self.ui = Ui_PlaybackStatusText()
        self.ui.setupUi(self)

        self.window().app.signal.playing.connect(self.on_playing)

    def on_playing(self, pointer, length):
        if not pointer.valid:
            self.ui.track_info.setText("")
        else:
            track = pointer.record
            self.track_time = length
            track_text = self.window().app.columns['summary'].displayFunc(track, length=length)

            self.ui.track_info.setText(track_text)

class PlaybackStatusCoverText(PlaybackStatusText,
        location=Qt.TopDockWidgetArea):

    def __init__(self, *arg, **kw):
        super().__init__(*arg, **kw)

    def config_ui(self):
        self.ui = Ui_PlaybackStatusCoverText()
        self.ui.setupUi(self)

        self.window().app.signal.playing .connect(self.on_playing)
        self.window().app.signal.position.connect(self.on_position)
        self.window().app.signal.time    .connect(self.on_time_changed)

        self.ui.position.valueChanged.connect (self.on_position_changed)

    def on_position(self, position):
        # TODO: Blocking signals is necessary to prevent the setValue signal
        #       ... from being emitted.  This is a brutal and ugly solution!
        #       ... Consider subclassing the widget to permit programatic
        #       ... value setting without emitting the signal.
        state = self.ui.position.blockSignals(True)
        self.ui.position.setValue(position * self.ui.position.maximum())
        self.ui.position.blockSignals(state)

    def on_time_changed(self, time):
        self.ui.elapsed  .setText(f"{round(time//60):3d}:{round(time%60):02d}")
        self.ui.remaining.setText(f"{round((self.track_time-time)//60):3d}:{round((self.track_time-time)%60):02d}")

    def on_position_changed(self, position):
        self.window().app.signal.seek.emit(position / self.ui.position.maximum())

    def on_playing(self, pointer, length):
        super().on_playing(pointer, length)

        # Clear the existing cover
        # ... this ensures that no album art is displayed for albums with no album art
        # ... this also clears the album art when an invalid track is playing
        self.ui.cover.setPixmap(QtGui.QPixmap())

        if pointer.valid:
            cover = MRL(pointer.mrl).cover()

            if cover is not None:
                pixmap = QtGui.QPixmap()
                pixmap.loadFromData(cover)
                self.ui.cover.setPixmap(pixmap.scaledToWidth(self.ui.cover.width(),Qt.SmoothTransformation))

