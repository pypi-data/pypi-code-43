'''
Dark World map
'''

from . import maps

__all__ = 'start',


def start(worldtracker) -> maps.MapDisplay:
    '''
    Open dark world map.

    Args:
        worldtracker: world state tracker
    '''

    display = maps.MapDisplay('dark')
    worldtracker.add_map('dark', display)
    return display
