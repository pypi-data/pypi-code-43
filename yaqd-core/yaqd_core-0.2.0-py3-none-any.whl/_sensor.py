#! /usr/bin/env python3

__all__ = ["Sensor"]


import asyncio
from ._daemon import Base


class Sensor(Base):
    _kind = "base-sensor"

    def __init__(self, name, config, config_filepath):
        super().__init__(name, config, config_filepath)
        self._measured = dict()  # values must be numbers or arrays
        self.channels = dict()  # values must be list [units, shape]
        self.measurement_id = 0

    def measure(self, loop=False):
        """Start a measurement, optionally looping.

        Sensor will remain busy until measurement completes.

        Parameters
        ----------
        loop: bool, optional
            Toggle looping behavior. Default False.

        See Also
        --------
        stop_looping
        """
        self.looping = loop
        if not self._busy:
            self._busy = True
            self._loop.create_task(self._runner(loop=loop))
        return self.measurement_id

    def get_channels(self):
        """Get current channel information."""
        return self._channels

    def get_measured(self):
        """Get most recently measured values."""
        return self._measured

    async def _measure(self):
        """Do measurement, filling _measured dictionary.

        Returns dictionary with keys channel names, values numbers or arrays.
        """
        return {}

    async def _runner(self, loop):
        """Handle execution of _measure, including looping and setting of measurement_id."""
        while True:
            self._measured = await self._measure()
            assert self._measured.keys() == self.channels.keys()
            self._measured["measurement_id"] = self.measurement_id
            if not self.looping:
                self._busy = False
                self.measurement_id += 1
                break
            await asyncio.sleep(0)

    def stop_looping(self):
        """Stop looping."""
        self.looping = False


if __name__ == "__main__":
    BaseSensorDaemon.main()
