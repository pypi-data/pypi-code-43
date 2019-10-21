# appteka - helpers collection

# Copyright (C) 2018-2019 Aleksandr Popov

# This program is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Lesser GNU General Public License for more details.

# You should have received a copy of the Lesser GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""This module implements the base class for routines."""


class Routine:
    """Base routine class."""
    def __init__(self):
        self.progress_hook = lambda x: True
        self.finished_hook = lambda: True
        self.volume = 1
        self.ready = 0

    def add_progress(self, part):
        """Add part value to progress."""
        self.ready += part
        self.progress_hook(int(100*self.ready/self.volume))

    def __call__(self):
        raise NotImplementedError
