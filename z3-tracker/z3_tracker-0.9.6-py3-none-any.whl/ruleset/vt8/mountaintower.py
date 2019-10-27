'''
Mountain Tower
'''

__all__ = 'LOCATIONS',


LOCATIONS = {
    'Mountain Tower Entrance (E)': {
        'type': 'entrance_dungeon', 'map': 'light', 'coord': (372, 35),
        'link': {
            'West Upper Mount Hebra': [],
            'Mountain Tower Entrance (I)': [('nosettings', 'inverted')],
            'Castle Tower Entrance (E)': [('settings', 'inverted')]}
    },
    'Mountain Tower Entrance (I)': {
        'type': 'interior',
        'link': {
            'Mountain Tower Entrance (E)': [],
            'Mountain Tower Interior': [('rabbitbarrier', None)]}
    },
    'Mountain Tower Interior': {
        'type': 'area', 'dungeon': 'Mountain Tower',
        'link': {
            'Mountain Tower Small Key': [],
            'Mountain Tower Map': [],
            'Mountain Tower Big Key Descent': [
                ('smallkey', ('Mountain Tower', 2))],
            'Mountain Tower Ascent': [('bigkey', 'Mountain Tower')]}
    },
    'Mountain Tower Small Key': {
        'type': 'dungeonchest', 'dungeon': 'Mountain Tower',
        'link': {
            'Mountain Tower Interior': []}
    },
    'Mountain Tower Map': {
        'type': 'dungeonchest', 'dungeon': 'Mountain Tower',
        'link': {
            'Mountain Tower Interior': []}
    },
    'Mountain Tower Big Key Descent': {
        'type': 'area', 'dungeon': 'Mountain Tower',
        'link': {
            'Mountain Tower Interior': [],
            'Mountain Tower Big Key': [
                ('item', 'lantern'), ('item', 'firerod')]}
    },
    'Mountain Tower Big Key': {
        'type': 'dungeonchest', 'dungeon': 'Mountain Tower',
        'link': {
            'Mountain Tower Big Key Descent': []}
    },
    'Mountain Tower Ascent': {
        'type': 'area', 'dungeon': 'Mountain Tower',
        'link': {
            'Mountain Tower Interior': [],
            'Mountain Tower Compass': [],
            'Mountain Tower Treasure': [],
            'Mountain Tower Boss': []}
    },
    'Mountain Tower Compass': {
        'type': 'dungeonchest_nokey', 'dungeon': 'Mountain Tower',
        'link': {
            'Mountain Tower Ascent': []}
    },
    'Mountain Tower Treasure': {
        'type': 'dungeonchest_nokey', 'dungeon': 'Mountain Tower',
        'link': {
            'Mountain Tower Ascent': []}
    },
    'Mountain Tower Boss': {
        'type': 'dungeonboss', 'dungeon': 'Mountain Tower',
        'link': {
            'Mountain Tower Boss Item': [('item', 'sword'), ('item', 'hammer')]}
    },
    'Mountain Tower Boss Item': {
        'type': 'dungeonchest_nokey', 'dungeon': 'Mountain Tower',
        'link': {
            'Mountain Tower Reward': []}
    },
    'Mountain Tower Reward': {
        'type': 'dungeonreward', 'dungeon': 'Mountain Tower',
        'link': {
            'Mountain Tower Entrance (I)': []}
    },
}
