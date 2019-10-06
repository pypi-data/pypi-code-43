import logging

_logger = logging.getLogger(__name__)

from mnectar.registry import Registry, Plugin
from mnectar.action import Action, Actionable
from mnectar.library.view import ViewPointer

import Registry.Control

class AlbumSkip(Plugin, Actionable, registry=Registry.Control):
    next_album = Action("Playback", "playback", "Next Album", "Ctrl+Right")
    prev_album = Action("Playback", "playback", "Previous Album", "Ctrl+Left")

    def __init__(self, *arg, **kw):
        super().__init__(*arg, **kw)

        self._playing = ViewPointer()
        self.app.signal.playing.connect(self.on_playing)

        _logger.debug("Plugin INIT: Album Skip")

    def on_playing(self, pointer, length):
        self._playing = pointer

    @next_album.triggered
    def on_next_album(self):
        pointer = self._playing

        # Scan forward in the playlist until a different album is detected
        while pointer.valid and pointer.next.valid and pointer.next.record['album'] == pointer.record['album']:
            pointer = pointer.next

        # Play the first track encountered in the new album
        if pointer.next.valid:
            self.app.signal.playNew.emit(pointer.next)
        else:
            self.app.signal.stop.emit()


    @prev_album.triggered
    def on_next_album(self):
        pointer = self._playing

        # Scan backwards in the playlist until a different album is detected
        while pointer.valid and pointer.prev.valid and pointer.prev.record['album'] == pointer.record['album']:
            pointer = pointer.prev

        # Move to the new album
        pointer = pointer.prev

        # Scan backwards in the playlist until a different album is detected
        # ... This finds the first track of the album in the playlist
        while pointer.valid and pointer.prev.valid and pointer.prev.record['album'] == pointer.record['album']:
            pointer = pointer.prev

        # Play the track (the first track in the album)
        if pointer.valid:
            self.app.signal.playNew.emit(pointer)
        else:
            self.app.signal.stop.emit()
