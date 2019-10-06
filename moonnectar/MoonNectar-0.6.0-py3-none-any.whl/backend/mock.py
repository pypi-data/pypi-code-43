import asyncio
import logging
import threading

from mnectar.registry import Plugin, Registry
from mnectar.library.view import ViewPointer

import Registry.Backend

_logger = logging.getLogger(__name__)

class BackendMock(Plugin, registry=Registry.Backend):
    """
    This backend player is a null loop for testing.
    No files are played, but all system signals are reacted to appropriately.
    This is primarily for automated testing in environments where playing a media file
    is not possible (such as cloud-based CI/CD servers.

    This backend simulation has one limitation:  Every track played has a length of
    60 seconds because no method for obtaining the actual length exists.
    """

    _pointer       = None
    _pointer_after = None     # ViewPointer to play after _pointer playback completes
    _mute          = False
    _paused        = False
    _playing       = False
    _position      = 0
    _time          = 0
    _resolution    = 0.1
    _running       = False
    _length        = 60.0

    def __init__(self, *arg, **kw):
        super().__init__(*arg, **kw)
        self._event_loop_running = threading.Event()
        self._pointer = ViewPointer(self.app, None)

    def _start(self):
        self._event_thread = threading.Thread(target=self._event_loop_main, daemon=True)
        self._event_loop_running.clear()
        self._event_thread.start()
        self._wait_on_event_loop()

    def _stop(self):
        self._running = False
        self._event_thread.join()
        self._event_loop_running.clear()
        self._event_thread = None

    def _wait_on_event_loop(self, timeout=1.0):
        running = self._event_loop_running.wait(timeout)
        if not running:
            _logger.error("Event Loop Startup Failed!")
            self.disable()

    def _event_loop_main(self):
        if self._running:
            _logger.error("Attempt to start an event loop that is already running!")
        else:
            self._running = True
            asyncio.run(self._playing_timer())

    async def _playing_timer(self):
        self._event_loop_running.set()

        while self._running:
            if self._playing and not self._paused:
                self._time     = min(self._length, self._time + self._resolution)
                self._position = min(1.0, (self._time+self._resolution)/self._length)

                self.app.signal.position.emit(self._position)
                self.app.signal.time.emit(self._time)
                if self._position >= 1.0:
                    self.app.signal.playEnd.emit(self._pointer)
                    self.play_next()
            await asyncio.sleep(self._resolution)

    @property
    def enabled(self):
        return self._event_loop_running.is_set()

    def enable(self):
        if not self.enabled:
            # Connect to the relevant application signals
            self.app.signal.pause      .connect(self.pause)
            self.app.signal.play       .connect(self.play)
            self.app.signal.playAfter  .connect(self.play_after)
            self.app.signal.playNew    .connect(self.play_new)
            self.app.signal.playNext   .connect(self.play_next)
            self.app.signal.playPrev   .connect(self.play_prev)
            self.app.signal.stop       .connect(self.stop)
            self.app.signal.togglePause.connect(self.togglePause)
            self.app.signal.seek       .connect(self.set_position)
            self.app.signal.skip       .connect(self.skip)
            self.app.signal.mute       .connect(self.mute)
            self.app.signal.toggleMute .connect(self.toggleMute)
            self._start()

    def disable(self):
        if self.enabled:
            # Disconnect all connected signals
            self.app.signal.pause      .disconnect(self.pause)
            self.app.signal.play       .disconnect(self.play)
            self.app.signal.playNew    .disconnect(self.play_new)
            self.app.signal.playNext   .disconnect(self.play_next)
            self.app.signal.playPrev   .disconnect(self.play_prev)
            self.app.signal.stop       .disconnect(self.stop)
            self.app.signal.togglePause.disconnect(self.togglePause)
            self.app.signal.seek       .disconnect(self.set_position)
            self.app.signal.skip       .disconnect(self.skip)
            self.app.signal.mute       .disconnect(self.mute)
            self.app.signal.toggleMute .disconnect(self.toggleMute)
            self._stop()

    def pause(self):
        self._paused = True
        self.app.signal.paused.emit()

    def play(self):
        if self._pointer is None:
            self.play_next()
        elif self._pointer.valid and self._pointer.mrl and not self._playing:
            self._paused  = False
            self._playing = True
            self.app.signal.playing.emit(self._pointer, self._length)
        elif self._pointer.valid and self._pointer.mrl and self._playing and self._paused:
            self._paused  = False
            self.app.signal.playing.emit(self._pointer, self._length)
        elif not self._pointer.valid:
            self.app.signal.playlistEnd.emit(self._pointer)
        else: # pragma: no cover
            # Should be impossible, but put it in for completeness anyways
            self.play_next()

    def play_new(self, pointer):
        if self.is_playing():
            self.app.signal.playEnd.emit(self._pointer)

        if pointer.valid:
            self._playing       = False
            self._position      = 0
            self._time          = 0
            self._pointer       = pointer
            self._length        = pointer.record['length']
            self._pointer_after = None
        else:
            self._playing       = False
            self._position      = 0
            self._time          = 0
            self._pointer       = pointer
            self._pointer_after = None
        self.play()

    def play_after(self, pointer):
        """
        Play the specified record after the current playback finishes.
        """
        if pointer == self._pointer:
            self._pointer = pointer
            self._pointer_after = None
        else:
            self._pointer_after = pointer

    def play_next(self):
        if self._pointer_after is not None:
            new = self._pointer_after
            self._pointer_after = None
            if new.valid:
                self.play_new(new)
            else:
                self.app.signal.playlistEnd.emit(new)
                self._playing  = False
                self._position = 0
                self._time     = 0
        elif self._pointer is not None:
            new = self._pointer.next
            if new.valid:
                self.play_new(new)
            else:
                self.app.signal.playlistEnd.emit(new)
                self._playing  = False
                self._position = 0
                self._time     = 0
        else:
            self.app.signal.playlistEnd.emit(ViewPointer(self.app, None))
            self._playing  = False
            self._position = 0
            self._time     = 0

    def play_prev(self):
        if self._pointer is not None:
            new = self._pointer.prev
            if new.valid:
                self.play_new(new)
            else:
                self.app.signal.playlistEnd.emit(new)
                self._playing  = False
                self._position = 0
                self._time     = 0
        else:
            self.app.signal.playlistEnd.emit(ViewPointer(self.app, None))
            self._playing  = False
            self._position = 0
            self._time     = 0

    def stop(self):
        self._playing  = False
        self._position = 0
        self._time     = 0
        self.app.signal.stopped.emit()

    def togglePause(self):
        if self._paused:
            self.play()
        elif self._playing:
            self.pause()
        else:
            self.app.signal.playNext.emit()

    def set_position(self, position):
        self._time = self._length * position

    def mute(self, state):
        if state != self._mute:
            self.app.signal.muted.emit(state)
        self._mute = state

    def toggleMute(self):
        self._mute = not self._mute
        self.app.signal.muted.emit(self._mute)

    def is_paused(self):
        return self._paused

    def is_playing(self):
        return self._playing and not self._paused

    def skip(self, delta):
        self._time     = max(0.0, min(self._length, self._time + delta))
        self._position = max(0.0, min(1.0, (self._time + delta) / self._length))
