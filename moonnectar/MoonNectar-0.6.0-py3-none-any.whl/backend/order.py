from __future__ import annotations

import logging

_logger = logging.getLogger(__name__)

from mnectar.config import Setting
from mnectar.library.view import ViewPointer
from mnectar.library.view import Randomized
from mnectar.library.view import RandomGroup
from mnectar.library.view import Sorted
from mnectar.library.view import Shifted

import Registry.Control


class OrderAgents(Registry, parent=Registry.Control):
    pass


class OrderManager(Registry.Plugin, registry=Registry.Control):
    _pointer = None # The most recent playlist pointer

    order = Setting(
        'playback.order', None, "--order", default="Linear", action="store", help="Playback Order"
    )

    @property
    def agents(self):
        return Registry.Control.OrderAgents.plugins

    @property
    def agent_names(self):
        return [_.__name__ for _ in self.agents]

    @property
    def agent_dict(self):
        return {_.__name__: _ for _ in self.agents}

    @property
    def agent(self):
        return self._agent

    @agent.setter
    def agent(self, new_agent):
        _logger.debug2(f"Set Order Agent: {new_agent}")
        if type(new_agent) == str:
            self._agent = self.agent_dict[new_agent](self.app)
        else:
            self._agent = new_agent(self.app)

        self.on_playing()

    def enable(self):
        self.agent = self.order

        self.app.signal.playing    .connect(self.on_playing)
        self.app.signal.playlistEnd.connect(self.on_playlist_end)

        _logger.debug("Playback Order Agent Active")

    def disable(self):
        self.app.signal.playing    .disconnect(self.on_playing)
        self.app.signal.playlistEnd.disconnect(self.on_playlist_end)

    def on_playing(self, pointer=None, length=None):
        self._pointer = pointer or self._pointer
        if self._pointer is not None and not self.agent.is_ordered(self._pointer):
            pnew = self.agent.reorder(self._pointer)
            if pnew.valid:
                # Update the playing track order by calling play_after
                # ... the backend will take care of all logic from here
                self.app.signal.playAfter.emit(pnew)

                # Update our local pointer store
                # ... we may not be notified of the above change!
                self._pointer = pnew

    def on_playlist_end(self, pointer):
        self._pointer = None


class AgentBase(Registry.Plugin, registry=None):
    """
    Base class defining the interface for an ordering agent.  While this class does not
    need to be used as a base class, its methods should be implemented as appropriate.
    """

    description = "Do not change view pointer ordering"
    order_stack = ()

    def reorder(self, pointer: ViewPointer) -> ViewPointer:
        """
        Set a new order view for the specified view pointer
        """
        new_pointer = pointer.reorder(pointer.view)

        for agent,default in self.order_stack:
            if default == "__pointer__":
                default = pointer
            new_pointer = new_pointer.reorder(agent(new_pointer.order, default=default))

        return new_pointer

    def is_ordered(self, pointer):
        """
        Test if this agent has already set the order in the provided pointer.
        """

        stack_rev = list(reversed(self.order_stack))
        chain = pointer.order.chain

        if len(chain) < len(stack_rev):
            return False
        else:
            for ix in range(len(stack_rev)):
                if not isinstance(chain[ix], stack_rev[ix][0]):
                    return False
                elif stack_rev[ix][1] == "__pointer__" and not isinstance(
                    chain[ix]._default, ViewPointer
                ):
                    return False
                elif (
                    stack_rev[ix][1] != "__pointer__"
                    and stack_rev[ix][1] != chain[ix]._default
                ):
                    return False
            return True


class Linear(AgentBase, registry=OrderAgents):
    description = "Original View Order"
    order_stack = ()

    def is_ordered(self, pointer):
        return pointer.view == pointer.order


class Random(AgentBase, registry=OrderAgents):
    description = "Random Order"
    order_stack = (
        (Randomized, None),
        (Shifted, "__pointer__"),
    )


class RandomAlbum(AgentBase, registry=OrderAgents):
    description = "Random albums, order maintained otherwise"
    order_stack = (
        (RandomGroup, "album"),
        (Shifted, "__pointer__"),
    )


class RandomArtist(AgentBase, registry=OrderAgents):
    description = "Random artists (grouped), random tracks within each artist"
    order_stack = (
        (Randomized, None),
        (RandomGroup, "artist"),
        (Shifted, "__pointer__"),
    )

