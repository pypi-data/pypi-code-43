'''
Light World map
'''

from . import maps

__all__ = 'start',


def start(worldtracker) -> maps.MapDisplay:
    '''
    Open light world map.

    Args:
        worldtracker: world state tracker
    '''

    display = maps.MapDisplay('light')
    worldtracker.add_map('light', display)
    return display
