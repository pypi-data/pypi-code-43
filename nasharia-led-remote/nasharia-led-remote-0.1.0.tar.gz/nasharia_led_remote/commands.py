"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of nasharia-led-remote.

nasharia-led-remote is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

nasharia-led-remote is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with nasharia-led-remote.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""


command_map = {
    "POWER": "POWER",
    "BRIGHTNESS_DOWN": "BRIGHTNESSDOWN",
    "BRIGHTNESS_UP": "BRIGHTNESSUP",
    "COLOR_RED": "F1",
    "COLOR_GREEN": "F2",
    "COLOR_BLUE": "F3",
    "COLOR_WHITE": "F4",
    "COLOR_DARK_ORANGE": "F5",
    "COLOR_LIGHT_GREEN": "F6",
    "COLOR_LIGHT_BLUE": "F7",
    "COLOR_LIGHT_PINK": "F8",
    "COLOR_ORANGE": "F9",
    "COLOR_LIGHT_TURQUOISE": "F10",
    "COLOR_DARK_PURPLE": "F11",
    "COLOR_DARK_PINK": "F12",
    "COLOR_LIGHT_ORANGE": "F13",
    "COLOR_TURQUOISE": "F14",
    "COLOR_PURPLE": "F15",
    "COLOR_LIGHT_SKY_BLUE": "F16",
    "COLOR_YELLOW": "F17",
    "COLOR_DARK_TURQUOISE": "F18",
    "COLOR_LIGHT_PURPLE": "F19",
    "COLOR_DARK_SKY_BLUE": "F20",
    "DIY_RED_UP": "NUMERIC_1",
    "DIY_RED_DOWN": "NUMERIC_2",
    "DIY_GREEN_UP": "NUMERIC_3",
    "DIY_GREEN_DOWN": "NUMERIC_4",
    "DIY_BLUE_UP": "NUMERIC_5",
    "DIY_BLUE_DOWN": "NUMERIC_6",
    "DIY_1": "NUMERIC_7",
    "DIY_2": "NUMERIC_8",
    "DIY_3": "NUMERIC_9",
    "DIY_4": "NUMERIC_10",
    "DIY_5": "NUMERIC_11",
    "DIY_6": "NUMERIC_12",
    "FLASH": "FN_F1",
    "FADE_3": "FN_F2",
    "FADE_7": "FN_F3",
    "JUMP_3": "FN_F4",
    "JUMP_7": "FN_F5",
    "AUTO": "FN_F6",
    "QUICK": "RIGHT",
    "SLOW": "LEFT",
    "PLAY_PAUSE": "PLAY",
    "PLAY": "PLAY",
    "PAUSE": "PAUSE"
}
"""
Dictionary mapping available command names to the corresponding keys
in the lirc configuration
"""
