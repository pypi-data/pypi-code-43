import logging
from .util.signal import Signal
from .action import Action
from .action import Actionable
from .config import Setting

class SignalControl(Actionable):
    """Central signal distribution class"""

    def __init__(self, app):
        self.app = app
        super().__init__(app=app)

        # Forward multimedia key hardware signals to normal control signals
        self.mmkey_playNext.connect(self.playNext)
        self.mmkey_playPrev.connect(self.playPrev)
        self.mmkey_togglePause.connect(self.togglePause)

    # Action Signals
    # ... These are used to request a change in the application state
    pause       = Signal() # Action: Pause Playback
    play        = Signal() # Action: Play current MRL if paused OR next if nothing playing (NOTE: NO ARGS)
    playAfter   = Signal() # Action: Play a new track after the current one finishes (ARGS: ViewPointer)
    playNew     = Signal() # Action: Play an new playlist (ARGS: ViewPointer)
    playNext    = Signal() # Action: Play the next track in the active playlist
    playPrev    = Signal() # Action: Play the previous track in the active playlist
    seek        = Signal() # Action: Seek to the specified position in the paying MRL (ARGS: Position [0.0-1.0])
    skip        = Signal() # Action: Skip forward/back in the playing MRL (ARGS: skip time in seconds)
    stop        = Signal() # Action: Stop Playback
    togglePause = Signal() # Action: Play/Pause Toggle
    mute        = Signal() # Action: Mute audio (via the backend player) (ARGS: state [bool])
    toggleMute  = Signal() # Action: Mute toggle

    # Action Signals: Multimedia Hardware Keys
    # ... These are separate from the above signals so that the rest of the application
    #     distinguish between internal signals and hardware signals originating from
    #     outside the application.
    mmkey_playNext    = Signal() # Action: Multimedia Hardware Key: Play the next track in the active playlist
    mmkey_playPrev    = Signal() # Action: Multimedia Hardware Key: Play the previous track in the active playlist
    mmkey_togglePause = Signal() # Action: Multimedia Hardware Key: Play/Pause Toggle

    # State Signals
    # ... These indicate changes in the current state of the application
    initComplete = Signal()                   # State: App Initialization Complete
    paused       = Signal()                   # State: Playback Paused
    playEnd      = Signal()                   # State: Playback Ended (end of track)
    playError    = Signal()                   # State: Playback Error (ARGS: MRL)
    playing      = Signal()                   # State: Playback Started (ARGS: ViewPointer, length[milliseconds])
    playlist     = Signal()                   # State: Active Playlist (ARGS: Playlist Class Instance)
    playlistEnd  = Signal()                   # State: Playlist Playback Ended (ARGS: ViewPointer[invalid])
    position     = Signal(log=logging.DEBUG3) # State: Playback Current Position (ARGS: Playback Position [0.0-1.0])
    stopped      = Signal()                   # State: Playback Stopped by Request
    time         = Signal(log=logging.DEBUG3) # State: Playback Current Time  (ARGS: Playback Time [seconds])
    muted        = Signal()                   # State: Audio mute state changed (ARGS: new state [bool])

    # Action Hooks
    action_play_pause     = Action("Playback", "playback", "Play/Pause Toggle",    "Space",        signal = mmkey_togglePause, )
    action_play_next      = Action("Playback", "playback", "Next Track",           "]",            signal = mmkey_playNext,    )
    action_play_prev      = Action("Playback", "playback", "Previous Track",       "[",            signal = mmkey_playPrev,    )
    action_stop           = Action("Playback", "playback", "Stop Playback",        "Ctrl+Shift+S", signal = stop,              )
    action_mute           = Action("Playback", "",         "Mute",                 "Ctrl+M",       signal = toggleMute,        )
    action_skip_rev_long  = Action("Playback", "seek",     "Skip Reverse (long)",  "Shift+Left",   signal = skip,              args = (-60, ), )
    action_skip_rev_short = Action("Playback", "seek",     "Skip Reverse (short)", "Left",         signal = skip,              args = (-10, ), )
    action_skip_fwd_short = Action("Playback", "seek",     "Skip Forward (short)", "Right",        signal = skip,              args = (10,  ), )
    action_skip_fwd_long  = Action("Playback", "seek",     "Skip Forward (long)",  "Shift+Right",  signal = skip,              args = (60,  ), )

    # Global Settings
    # ... These are typically not used here (though they can be)
    # ... But they must be defined in a central location to be linked to an action
    loop = Setting('playback.loop', default=False)

    action_loop  = Action("Playback",       "",         "Loop Playlist",        "Ctrl+Shift+L", setting   = loop,        checkable = True, )
