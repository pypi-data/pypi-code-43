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

'''Various prompt-style conditions'''

from prompt_toolkit.filters import Condition
from prompt_toolkit.application.current import get_app


@Condition
def is_insert_state():
    controller = get_app().controller()
    if not controller:
        return False
    return controller.is_insert_state()


@Condition
def is_normal_state():
    controller = get_app().controller()
    if not controller:
        return False
    return controller.is_normal_state()
