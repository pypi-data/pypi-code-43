'''
Presets for configuration file
'''

import sys

from ..version import __version__ as version

__all__ = 'DEFAULT', 'OVERWRITE'


DEFAULT = {
    'gui': ('gui-tkinter', str),
    'font_size': (
        '14' if sys.platform.startswith('win32') else '12', int),
    'icon_size': ('1.0', float),
    'map_size': ('1.0', float),
    'autosave': ('autosave.json', str),
    'button_layout': ('buttons.json', str),
    'window_layout': ('windows.json', str),

    'entrance_randomiser': (True, bool),
    'world_state': ('Open', str),
    'glitch_mode': ('None', str),
    'item_placement': ('Advanced', str),
    'dungeon_items': ('Standard', str),
    'goal': ('Defeat Ganon', str),
    'swords': ('Randomised', str),
}


OVERWRITE = {
    '0.9.0': set(),
    '0.9.1': set(),
    '0.9.2': set(),
    '0.9.3': set(),
    '0.9.4': set(),
    '0.9.5': set(),
    '0.9.6': set(),
}
