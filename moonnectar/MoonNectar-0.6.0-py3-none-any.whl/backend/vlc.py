import logging
import vlc

from mnectar.registry     import Plugin, Registry
from mnectar.util.signal  import Signal
from mnectar.library.view import ViewPointer

import Registry.Backend

logger = logging.getLogger(__name__)

class BackendVLC(Plugin, registry=Registry.Backend):
    """VLC based backend.  Requires the VLC media player be installed"""

    _vlcmp         = None     # The VLC media player instance
    _pointer       = None     # ViewPointer to the track being played
    _pointer_after = None     # ViewPointer to play after _pointer playback completes

    def __init__(self, *arg, **kw):
        super().__init__(*arg, **kw)

    @property
    def enabled(self):
        return hasattr(self, "_vlcmp") and self._vlcmp is not None

    def enable(self):
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

        self.create()

    def disable(self):
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

        self.destroy()

    def _vlcmp_event(self, event):
        if event.type == vlc.EventType.MediaPlayerPlaying:
            self.app.signal.playing.emit(self._pointer, self._vlcmp.get_length()/1000)

        elif event.type == vlc.EventType.MediaPlayerEndReached:
            # Indicate that track playback has ended
            self.app.signal.playEnd.emit(self._pointer)

            # Cannot interact with VLC from the VLC event loop
            # ... so use an internal signal to call the next track from outside the
            #     event loop.
            self.app.signal.playNext.emit()

        elif event.type == vlc.EventType.MediaPlayerTimeChanged:
            self.app.signal.time.emit(event.u.new_time / 1000)

        elif event.type == vlc.EventType.MediaPlayerPositionChanged:
            self.app.signal.position.emit(event.u.new_position)

        elif event.type == vlc.EventType.MediaPlayerStopped:
            self.app.signal.stopped.emit()

        elif event.type == vlc.EventType.MediaPlayerPaused:
            self.app.signal.paused.emit()

        elif event.type == vlc.EventType.MediaPlayerMuted:
            self.app.signal.muted.emit(True)

        elif event.type == vlc.EventType.MediaPlayerUnmuted:
            self.app.signal.muted.emit(False)

        elif event.type == vlc.EventType.MediaPlayerEncounteredError: # pragma: no cover
            logger.error(f"VLC Encountered an error playing file: {self._pointer.mrl}")
            self.app.signal.playError.emit(self._pointer.mrl)

        elif event.type in (
                vlc.EventType.MediaPlayerBuffering,
                vlc.EventType.MediaPlayerTimeChanged): # pragma: no cover
            # Ignored Event
            pass

        elif event.type == vlc.EventType.MediaPlayerLengthChanged: # pragma: no cover
            # Probably not needed, but list it separately in case it comes up in testing
            #logger.debug(f"Event Received: {event.type} {event.u.new_length}")
            pass

        else:
            logger.debug2(f"Event Received: {event.type}")

    def create(self):
        if self._vlcmp is None:
            # Create a new media player object
            logger.debug(f"Creating New VLC Media Player Object")
            self._vlcmp = vlc.MediaPlayer()

            self._vlcmp_events = self._vlcmp.event_manager()

            for eventid in vlc.EventType._enum_names_.keys():
                event_type = vlc.EventType(eventid)
                logger.debug3(f"Registering VLC Event Type: {event_type}")
                self._vlcmp_events.event_attach(event_type, self._vlcmp_event)

    def destroy(self):
        if self._vlcmp is not None:
            self._vlcmp.release()
            self._vlcmp = None

    def play_next(self):
        if self._pointer_after is not None:
            new = self._pointer_after
            self._pointer_after = None
            if new.valid:
                self.play_new(new)
            else:
                self.app.signal.playlistEnd.emit(new)
        elif self._pointer is not None:
            new = self._pointer.next
            if new.valid:
                self.play_new(new)
            else:
                self.app.signal.playlistEnd.emit(new)
        else:
            self.app.signal.playlistEnd.emit(ViewPointer(self.app, None))

    def play_prev(self):
        if self._pointer is not None:
            new = self._pointer.prev
            if new.valid:
                self.play_new(new)
            else:
                self.app.signal.playlistEnd.emit(new)
        else:
            self.app.signal.playlistEnd.emit(ViewPointer(self.app, None))

    def play_new(self, pointer):
        if self._vlcmp.is_playing():
            self.app.signal.playEnd.emit(self._pointer)

        # Save the MRL being played
        self._pointer = pointer
        self._pointer_after = None

        # Create the media player object if necessary...
        self.create()

        # Set the MRL to play ...
        self._vlcmp.set_mrl(self._pointer.mrl)

        # Start the media playing
        logger.debug(f"Playing MRL: {pointer.mrl}")
        if not self._vlcmp.is_playing():
            self._vlcmp.play()

    def play_after(self, pointer):
        """
        Play the specified record after the current playback finishes.
        """
        if pointer == self._pointer:
            self._pointer = pointer
            self._pointer_after = None
        else:
            self._pointer_after = pointer

    def play(self):
        # If nothing played yet, automatically play the next track ...
        if self._pointer is None:
            self.play_next()

        # If an MRL is playing now
        # ... play it (probably was paused)
        elif self._vlcmp is not None and (self.is_playing() or self.is_paused()):
            self._vlcmp.play()

        # If an MRL is configured but we are not active playing (above case)
        # ... play this MRL again
        # ... This accounts for a stop-play scenario
        elif self._vlcmp.get_media() is not None and self._vlcmp.get_media().get_mrl():
            self._vlcmp.play()

        # Should be impossible, but put it in for completeness anyways
        else: # pragma: no cover
            self.play_next()

    def pause(self):
        if self.is_playing():
            self.togglePause()

    def togglePause(self):
        if self.is_paused():
            self._vlcmp.play()
        elif self.is_playing():
            self._vlcmp.pause()
        else:
            self.app.signal.playNext.emit()

    def stop(self):
        if self._vlcmp is not None:
            self._vlcmp.stop()

    def is_playing(self):
        return self._vlcmp.is_playing()

    def is_paused(self):
        state = self._vlcmp.get_state()
        return state == vlc.State.Paused

    def set_position(self, position):
        self._vlcmp.set_position(position)

    def mute(self, state):
        self._vlcmp.audio_set_mute(state)

    def toggleMute(self):
        self._vlcmp.audio_toggle_mute()

    def skip(self, delta):
        deltams = int(delta*1000)
        self._vlcmp.set_time(self._vlcmp.get_time() + deltams)
