'''
Skull Woods
'''

__all__ = 'LOCATIONS',


LOCATIONS = {
    'Kakariko Portal (DW)': {
        'type': 'area',
        'link': {
            'Kakariko Portal (LW)': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Kakariko Portal': [('item', 'powerglove')],
            'Skull Woods Surface': [('rabbitbarrier', None)],
            "Thieves' Town Surface": [('item', 'titansmitts')]}
    },
    'Skull Woods Surface': {
        'type': 'area',
        'link': {
            'Lost Woods': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Dark Bottle Ocarina': [],
            'Kakariko Portal (DW)': [],
            "Thieves' Town Surface": [],
            'Skull Woods First Entrance Entrance (E)': [],
            'Skull Woods West Drop Entrance (E)': [],
            'Skull Woods East Drop Entrance (E)': [],
            'Skull Woods Central Drop Entrance (E)': [('rabbitbarrier', None)],
            'Skull Woods Second Entrance Entrance (E)': [],
            'North Dark World': []}
    },
    'Skull Woods First Entrance Entrance (E)': {
        'type': 'entrance_dungeon', 'map': 'dark', 'coord': (116, 98),
        'link': {
            'Skull Woods Surface': [],
            'Skull Woods First Entrance Entrance (I)': []}
    },
    'Skull Woods First Entrance Entrance (I)': {
        'type': 'interior',
        'link': {
            'Skull Woods First Entrance Entrance (E)': [],
            'Skull Woods First Entrance': [
                ('settings', 'placement_advanced'),
                ('and', [
                    ('or', [
                        ('settings', 'swordless'), ('item', 'sword')]),
                    ('item', 'bottle')])]}
    },
    'Skull Woods First Entrance': {
        'type': 'area', 'dungeon': 'Skull Woods',
        'link': {
            'Skull Woods First Entrance Entrance (I)': [],
            'Skull Woods Map': [('rabbitbarrier', None)],
            'Skull Woods West Drop': [('smallkey', ('Skull Woods', 5))]}
    },
    'Skull Woods Map': {
        'type': 'dungeonchest', 'dungeon': 'Skull Woods',
        'link': {
            'Skull Woods First Entrance': []}
    },
    'Skull Woods West Drop': {
        'type': 'area', 'dungeon': 'Skull Woods',
        'link': {
            'Skull Woods First Entrance': [('smallkey', ('Skull Woods', 5))],
            'Skull Woods Front Key': [('rabbitbarrier', None)],
            'Skull Woods Compass': [('rabbitbarrier', None)],
            'Skull Woods East Drop': []}
    },
    'Skull Woods Front Key': {
        'type': 'dungeonchest', 'dungeon': 'Skull Woods',
        'link': {
            'Skull Woods West Drop': []}
    },
    'Skull Woods Compass': {
        'type': 'dungeonchest', 'dungeon': 'Skull Woods',
        'link': {
            'Skull Woods West Drop': []}
    },
    'Skull Woods East Drop': {
        'type': 'area', 'dungeon': 'Skull Woods',
        'link': {
            'Skull Woods First Entrance': [('smallkey', ('Skull Woods', 5))],
            'Skull Woods Safety Key': [('rabbitbarrier', None)]}
    },
    'Skull Woods Safety Key': {
        'type': 'dungeonchest', 'dungeon': 'Skull Woods',
        'link': {
            'Skull Woods East Drop': []}
    },
    'Skull Woods West Drop Entrance (E)': {
        'type': 'entrance_drop', 'map': 'dark', 'coord': (98, 117),
        'link': {
            'Skull Woods West Drop Entrance (I)': []}
    },
    'Skull Woods West Drop Entrance (I)': {
        'type': 'interior',
        'link': {
            'Skull Woods West Drop': [
                ('settings', 'placement_advanced'),
                ('and', [
                    ('or', [
                        ('settings', 'swordless'), ('item', 'sword')]),
                    ('item', 'bottle')])]}
    },
    'Skull Woods East Drop Entrance (E)': {
        'type': 'entrance_drop', 'map': 'dark', 'coord': (124, 113),
        'link': {
            'Skull Woods East Drop Entrance (I)': []}
    },
    'Skull Woods East Drop Entrance (I)': {
        'type': 'interior',
        'link': {
            'Skull Woods East Drop': [
                ('settings', 'placement_advanced'),
                ('and', [
                    ('or', [
                        ('settings', 'swordless'), ('item', 'sword')]),
                    ('item', 'bottle')])]}
    },
    'Skull Woods Central Drop Entrance (E)': {
        'type': 'entrance_drop', 'map': 'dark', 'coord': (120, 83),
        'link': {
            'Skull Woods Central Drop Entrance (I)': []}
    },
    'Skull Woods Central Drop Entrance (I)': {
        'type': 'interior',
        'link': {
            'Skull Woods Central Drop': [
                ('settings', 'placement_advanced'),
                ('and', [
                    ('or', [
                        ('settings', 'swordless'), ('item', 'sword')]),
                    ('item', 'bottle')])]}
    },
    'Skull Woods Central Drop': {
        'type': 'area', 'dungeon': 'Skull Woods',
        'link': {
            'Skull Woods First Entrance': [],
            'Skull Woods Treasure': [('rabbitbarrier', None)]}
    },
    'Skull Woods Treasure': {
        'type': 'dungeonchest_nokey', 'dungeon': 'Skull Woods',
        'link': {
            'Skull Woods Central Drop': []}
    },
    'Skull Woods Second Entrance Entrance (E)': {
        'type': 'entrance_dungeon', 'map': 'dark', 'coord': (90, 96),
        'link': {
            'Skull Woods Surface': [],
            'Skull Woods Second Entrance Entrance (I)': []}
    },
    'Skull Woods Second Entrance Entrance (I)': {
        'type': 'interior',
        'link': {
            'Skull Woods Second Entrance Entrance (E)': [],
            'Skull Woods Connector': [
                ('settings', 'placement_advanced'),
                ('and', [
                    ('or', [
                        ('settings', 'swordless'), ('item', 'sword')]),
                    ('item', 'bottle')])]}
    },
    'Skull Woods Connector': {
        'type': 'area', 'dungeon': 'Skull Woods',
        'link': {
            'Skull Woods Second Entrance Entrance (I)': [],
            'Skull Woods Big Key': [('rabbitbarrier', None)],
            'Skull Woods Hidden Key': [('rabbitbarrier', None)],
            'Skull Woods Third Entrance Entrance (I)': []}
    },
    'Skull Woods Big Key': {
        'type': 'dungeonchest', 'dungeon': 'Skull Woods',
        'link': {
            'Skull Woods Connector': []}
    },
    'Skull Woods Hidden Key': {
        'type': 'dungeonkey', 'dungeon': 'Skull Woods',
        'link': {
            'Skull Woods Connector': []}
    },
    'Skull Woods Third Entrance Entrance (I)': {
        'type': 'interior',
        'link': {
            'Skull Woods Connector': [],
            'Skull Woods Third Entrance Entrance (E)': [
                ('settings', 'placement_advanced'),
                ('and', [
                    ('or', [
                        ('settings', 'swordless'), ('item', 'sword')]),
                    ('item', 'bottle')])]}
    },
    'Skull Woods Third Entrance Entrance (E)': {
        'type': 'entrance_dungeon', 'map': 'dark', 'coord': (33, 86),
        'link': {
            'Skull Woods Third Entrance Entrance (I)': [],
            'Hidden Skull Woods': []}
    },
    'Hidden Skull Woods': {
        'type': 'area',
        'link': {
            'Lost Woods': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Skull Woods Third Entrance Entrance (E)': [],
            'Skull Woods North Drop Entrance (E)': [],
            'Skull Woods Fourth Entrance Entrance (E)': [('item', 'firerod')]}
    },
    'Skull Woods North Drop Entrance (E)': {
        'type': 'entrance_drop', 'map': 'dark', 'coord': (74, 60),
        'link': {
            'Skull Woods North Drop Entrance (I)': []}
    },
    'Skull Woods North Drop Entrance (I)': {
        'type': 'interior',
        'link': {
            'Skull Woods Connector': [
                ('settings', 'placement_advanced'),
                ('and', [
                    ('or', [
                        ('settings', 'swordless'), ('item', 'sword')]),
                    ('item', 'bottle')])]}
    },
    'Skull Woods Fourth Entrance Entrance (E)': {
        'type': 'entrance_dungeon', 'map': 'dark', 'coord': (20, 43),
        'link': {
            'Hidden Skull Woods': [],
            'Skull Woods Fourth Entrance Entrance (I)': []}
    },
    'Skull Woods Fourth Entrance Entrance (I)': {
        'type': 'interior',
        'link': {
            'Skull Woods Fourth Entrance Entrance (E)': [],
            'Skull Woods Gauntlet Entrance': [
                ('settings', 'placement_advanced'),
                ('and', [
                    ('or', [
                        ('settings', 'swordless'), ('item', 'sword')]),
                    ('item', 'bottle')])]}
    },
    'Skull Woods Gauntlet Entrance': {
        'type': 'area', 'dungeon': 'Skull Woods',
        'link': {
            'Skull Woods Fourth Entrance Entrance (I)': [],
            'Skull Woods Gauntlet Key': [('rabbitbarrier', None)],
            'Skull Woods Gauntlet 1': [('smallkey', ('Skull Woods', 5))]}
    },
    'Skull Woods Gauntlet Key': {
        'type': 'dungeonchest', 'dungeon': 'Skull Woods',
        'link': {
            'Skull Woods Gauntlet Entrance': []}
    },
    'Skull Woods Gauntlet 1': {
        'type': 'area', 'dungeon': 'Skull Woods',
        'link': {
            'Skull Woods Gauntlet Entrance': [],
            'Skull Woods Gauntlet 2': [('and', [
                ('item', 'firerod'),
                ('item', 'sword')])]}
    },
    'Skull Woods Gauntlet 2': {
        'type': 'area', 'dungeon': 'Skull Woods',
        'link': {
            'Skull Woods Gauntlet 2': [],
            'Skull Woods Gibdo Key': [],
            'Skull Woods Boss': [('smallkey', ('Skull Woods', 5))]}
    },
    'Skull Woods Gibdo Key': {
        'type': 'dungeonkey', 'dungeon': 'Skull Woods',
        'link': {
            'Skull Woods Gauntlet 2': []}
    },
    'Skull Woods Boss': {
        'type': 'dungeonboss', 'dungeon': 'Skull Woods',
        'link': {
            'Skull Woods Boss Item': [('and', [
                ('or', [
                    ('settings', 'placement_advanced'),
                    ('item', 'mastersword'),
                    ('and', [
                        ('or', [
                            ('item', 'bottle'), ('item', 'halfmagic')]),
                        ('item', 'firerod')])]),
                ('or', [
                    ('and', [
                        ('or', [
                            ('item', 'bottle'), ('item', 'halfmagic')]),
                        ('or', [
                            ('item', 'firerod'), ('item', 'somaria'),
                            ('item', 'byrna')])]),
                    ('item', 'sword'),
                    ('item', 'hammer')])])]}
    },
    'Skull Woods Boss Item': {
        'type': 'dungeonchest_nokey', 'dungeon': 'Skull Woods',
        'link': {
            'Skull Woods Reward': []}
    },
    'Skull Woods Reward': {
        'type': 'dungeonreward', 'dungeon': 'Skull Woods',
        'link': {
            'Skull Woods Fourth Entrance Entrance (I)': []}
    },
}
