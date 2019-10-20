#! /usr/bin/env python3

__all__ = ["Hardware"]

import math

from .._daemon import Base, set_action


class Hardware(Base):
    _kind = "base-hardware"

    def __init__(self, name, config, config_filepath):
        self.units = config.get("units", None)
        super().__init__(name, config, config_filepath)

    def id(self):
        ret = super().id()
        ret.update({"units": self.units})
        return ret

    def get_position(self):
        return self._position

    def get_destination(self):
        return self._destination

    @set_action
    def set_position(self, position):
        self._destination = position
        self._set_position(position)

    def _set_position(self, position):
        self._position = position
        self._busy = False

    def get_state(self):
        return {"position": self._position, "destination": self._destination}

    def _load_state(self, state):
        self._position = state.get("position", math.nan)
        self._destination = state.get("destination", math.nan)


if __name__ == "__main__":
    BaseHardwareDaemon.main()
