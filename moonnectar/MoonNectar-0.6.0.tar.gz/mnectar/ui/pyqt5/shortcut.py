from __future__ import annotations

import inspect
from typing import Optional, Callable
from mnectar.util import Decorator
from mnectar.util import classproperty
from mnectar.action import Actionable

from mnectar.util.signal import Signal
from mnectar.config import Setting
from mnectar.action import Action, Actionable


class Foo(Actionable):
    _playing = False
    _loop = False

    loop  = Setting("playback.loop",  default = True)
    order = Setting("playback.order", default = "Linear")

    mute        = Signal() # Action: Mute audio (via the backend player) (ARGS: state [bool])
    pause       = Signal() # Action: Pause Playback
    play        = Signal() # Action: Play current MRL if paused OR next if nothing playing (NOTE: NO ARGS)
    playAfter   = Signal() # Action: Play a new track after the current one finishes (ARGS: ViewPointer)
    playNew     = Signal() # Action: Play an new playlist (ARGS: ViewPointer)
    playNext    = Signal() # Action: Play the next track in the active playlist
    playPrev    = Signal() # Action: Play the previous track in the active playlist
    seek        = Signal() # Action: Seek to the specified position in the paying MRL (ARGS: Position [0.0-1.0])
    skip        = Signal() # Action: Skip forward/backward in the playing track (ARGS: time(seconds))
    stop        = Signal() # Action: Stop Playback
    togglePause = Signal() # Action: Play/Pause Toggle
    toggleMute  = Signal() # Action: Mute Toggle

    # fmt: off
    #action_play_pause        = Action("Playback",       "playback", "Play/Pause Toggle",    "Space",        signal    = togglePause, )
    #action_play_next         = Action("Playback",       "playback", "Next Track",           "BracketLeft",  signal    = playNext,    )
    #action_play_prev         = Action("Playback",       "playback", "Previous Track",       "BracketRight", signal    = playPrev,    )
    #action_stop              = Action("Playback",       "playback", "Stop Playback",        "Ctrl+Shift+S", signal    = stop,        )
    #action_loop              = Action("Playback",       "",         "Loop Playlist",        "Ctrl+Shift+L", setting   = loop,        checkable = True, )
    #action_mute              = Action("Playback",       "",         "Mute",                 "Ctrl+M",       signal    = toggleMute,  )
    #action_linear            = Action("Playback|Order", "order",    "Linear",               "Ctrl+L",       checkable = True,        exclusive = True, setting   = order, args = ("Linear",       ), )
    #action_random            = Action("Playback|Order", "order",    "Random",               "Ctrl+R",       checkable = True,        exclusive = True, setting   = order, args = ("Random",       ), )
    #action_random_album      = Action("Playback|Order", "order",    "Random Album",         "",             checkable = True,        exclusive = True, setting   = order, args = ("RandomAlbum",  ), )
    #action_random_artist     = Action("Playback|Order", "order",    "Random Artist",        "",             checkable = True,        exclusive = True, setting   = order, args = ("RandomArtist", ), )
    #action_skip_rev_long     = Action("Playback",       "seek",     "Skip Reverse (long)",  "Shift+Right",  signal    = skip,        args   = (-60,    ),                 )
    #action_skip_rev_short    = Action("Playback",       "seek",     "Skip Reverse (short)", "Right",        signal    = skip,        args   = (-10,    ),                 )
    #action_skip_fwd_short    = Action("Playback",       "seek",     "Skip Forward (short)", "Right",        signal    = skip,        args   = (10,     ),                 )
    #action_skip_fwd_long     = Action("Playback",       "seek",     "Skip Forward (long)",  "Shift+Right",  signal    = skip,        args   = (60,     ),                 )
    action_scan              = Action("Library",        "",         "Rescan Library",       )
    #
    #action_show_hash_manager = Action("View",           "",         "Hashtag Manager",      "Ctrl+H",       checkable = True)
    # fmt: on

    @action_show_hash_manager.checked
    def action_show_hash_manager_checked(self, state):
        ... # Show Window


a=Foo()
b=ActionCreator()
m=QtWidgets.QMenu('Foo')
b.create_menu_actions(m)
m.findChildren(QtWidgets.QMenu)
[_.title() for _ in m.findChildren(QtWidgets.QMenu, options=QtCore.Qt.FindDirectChildrenOnly)]
