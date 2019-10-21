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


"""State machine for enabling/disabling controls."""


class ControlsStateMachine:
    """ State machine for enable/disable/hide/show controls. """
    def __init__(self):
        """ Initialization. """
        self.__states = {}
        self.__controls = []

    def add_state(self, state_name):
        """ Add new state (or reset existing one). """
        self.__states[state_name] = {
            'invisible': [],
            'disabled': []
        }

    def setup_state(self, state_name, invisible=[], disabled=[]):
        """ Setup sate. """
        if state_name not in self.__states:
            self.add_state(state_name)
        self._setup_controls_state(invisible, state_name, 'invisible')
        self._setup_controls_state(disabled, state_name, 'disabled')

    def set_state(self, state_name):
        """ Set currect state. """
        for c in self.__controls:
            c.setVisible(c not in self.__states[state_name]['invisible'])
            c.setEnabled(c not in self.__states[state_name]['disabled'])

    def _setup_controls_state(self, controls, state_name, key):
        """ Helper function. """
        self.__states[state_name][key] = []
        for c in controls:
            if c not in self.__controls:
                self.__controls.append(c)
            self.__states[state_name][key].append(c)
