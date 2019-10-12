# Copyright (C) 2019 Michał Góral.
#
# This file is part of TWC
#
# TWC is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TWC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TWC. If not, see <http://www.gnu.org/licenses/>.

'''User commands'''

from prompt_toolkit.key_binding import KeyBindings
from twc.utils import cancel_all_async_tasks

from twc.conditions import (
    is_normal_state,
)


def event_to_controller(fn):
    def _new_fn(event):
        controller = event.app.controller()
        if not controller:
            return None
        return fn(controller)
    return _new_fn


def global_bindings(cfg):
    kb = KeyBindings()

    @cfg.command_handler('quit', kb, filter=is_normal_state)
    def _(event):
        '''Quit main loop'''
        cancel_all_async_tasks()
        event.app.exit()

    return kb
