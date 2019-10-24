'''
Swamp Palace
'''

__all__ = 'LOCATIONS',


LOCATIONS = {
    'Swamp Palace Entrance (E)': {
        'type': 'entrance_dungeon', 'map': 'dark', 'coord': (304, 621),
        'link': {
            'South Dark World': [],
            'Swamp Palace Entrance (I)': []}
    },
    'Swamp Palace Entrance (I)': {
        'type': 'interior',
        'link': {
            'Swamp Palace Entrance (E)': [],
            'Swamp Palace Before Canal': [
                ('settings', 'placement_advanced'),
                ('and', [
                    ('or', [
                        ('settings', 'swordless'), ('item', 'sword')]),
                    ('item', 'bottle')])]}
    },
    'Swamp Palace Before Canal': {
        'type': 'area', 'dungeon': 'Swamp Palace',
        'link': {
            'Swamp Palace Entrance (I)': [],
            'Swamp Palace Canal': [('and', [
                ('access', 'Water Drain'),
                ('or', [('settings', 'entrance'), ('item', 'mirror')])])]}
    },
    'Swamp Palace Canal': {
        'type': 'area', 'dungeon': 'Swamp Palace After Canal',
        'link': {
            'Swamp Palace Before Canal': [],
            'Swamp Palace After Canal': [('item', 'flippers')]}
    },
    'Swamp Palace After Canal': {
        'type': 'area', 'dungeon': 'Swamp Palace',
        'link': {
            'Swamp Palace Canal': [('item', 'flippers')],
            'Swamp Palace Key': [],
            'Swamp Palace Water Hall': [('smallkey', ('Swamp Palace', 1))]}
    },
    'Swamp Palace Key': {
        'type': 'dungeonchest', 'dungeon': 'Swamp Palace',
        'link': {
            'Swamp Palace After Canal': []}
    },
    'Swamp Palace Water Hall': {
        'type': 'area', 'dungeon': 'Swamp Palace',
        'link': {
            'Swamp Palace After Canal': [],
            'Swamp Palace Map': [('item', 'bombs')],
            'Swamp Palace First Hidden Key': [],
            'Swamp Palace East Basin': [('smallkey', ('Swamp Palace', 1))]}
    },
    'Swamp Palace Map': {
        'type': 'dungeonchest', 'dungeon': 'Swamp Palace',
        'link': {
            'Swamp Palace Water Hall': []}
    },
    'Swamp Palace First Hidden Key': {
        'type': 'dungeonkey', 'dungeon': 'Swamp Palace',
        'link': {
            'Swamp Palace Water Hall': []}
    },
    'Swamp Palace East Basin': {
        'type': 'area', 'dungeon': 'Swamp Palace',
        'link': {
            'Swamp Palace Water Hall': [],
            'Swamp Palace Second Hidden Key': [],
            'Swamp Palace East Switch Room': [
                ('smallkey', ('Swamp Palace', 1))]}
    },
    'Swamp Palace Second Hidden Key': {
        'type': 'dungeonkey', 'dungeon': 'Swamp Palace',
        'link': {
            'Swamp Palace East Basin': []}
    },
    'Swamp Palace East Switch Room': {
        'type': 'area', 'dungeon': 'Swamp Palace',
        'link': {
            'Swamp Palace East Basin': [],
            'Swamp Palace East Switch': [('item', 'hammer')]}
    },
    'Swamp Palace East Switch': {
        'type': 'area', 'dungeon': 'Swamp Palace',
        'link': {
            'Swamp Palace East Switch Room': [],
            'Swamp Palace Water Hall': [('item', 'flippers')],
            'Swamp Palace Main Hall': [('item', 'flippers')]}
    },
    'Swamp Palace Main Hall': {
        'type': 'area', 'dungeon': 'Swamp Palace',
        'link': {
            'Swamp Palace East Switch': [],
            'Swamp Palace Compass': [],
            'Swamp Palace Third Hidden Key': [],
            'Swamp Palace West Switch': [('smallkey', ('Swamp Palace', 1))],
            'Swamp Palace Treasure': [('bigkey', 'Swamp Palace')],
            'Swamp Palace Fourth Hidden Key': [('item', 'hookshot')],
            'Swamp Palace Gauntlet Entrance': [('item', 'hookshot')]}
    },
    'Swamp Palace Compass': {
        'type': 'dungeonchest', 'dungeon': 'Swamp Palace',
        'link': {
            'Swamp Palace Main Hall': []}
    },
    'Swamp Palace Third Hidden Key': {
        'type': 'dungeonkey', 'dungeon': 'Swamp Palace',
        'link': {
            'Swamp Palace Main Hall': []}
    },
    'Swamp Palace West Switch': {
        'type': 'area', 'dungeon': 'Swamp Palace',
        'link': {
            'Swamp Palace Main Hall': [],
            'Swamp Palace West Basin': [('item', 'flippers')]}
    },
    'Swamp Palace West Basin': {
        'type': 'area', 'dungeon': 'Swamp Palace',
        'link': {
            'Swamp Palace Main Hall': [('item', 'flippers')],
            'Swamp Palace Fake Big Key': [],
            'Swamp Palace Big Key': []}
    },
    'Swamp Palace Fake Big Key': {
        'type': 'dungeonchest', 'dungeon': 'Swamp Palace',
        'link': {
            'Swamp Palace West Basin': []}
    },
    'Swamp Palace Big Key': {
        'type': 'dungeonchest', 'dungeon': 'Swamp Palace',
        'link': {
            'Swamp Palace West Basin': []}
    },
    'Swamp Palace Treasure': {
        'type': 'dungeonchest_nokey', 'dungeon': 'Swamp Palace',
        'link': {
            'Swamp Palace Main Hall': []}
    },
    'Swamp Palace Fourth Hidden Key': {
        'type': 'dungeonkey', 'dungeon': 'Swamp Palace',
        'link': {
            'Swamp Palace Main Hall': []}
    },
    'Swamp Palace Gauntlet Entrance': {
        'type': 'area', 'dungeon': 'Swamp Palace',
        'link': {
            'Swamp Palace Main Hall': [],
            'Swamp Palace Gauntlet': [('smallkey', ('Swamp Palace', 1))]}
    },
    'Swamp Palace Gauntlet': {
        'type': 'area', 'dungeon': 'Swamp Palace',
        'link': {
            'Swamp Palace Gauntlet Entrance': [],
            'Swamp Palace Left Treasury Chest': [],
            'Swamp Palace Right Treasury Chest': [],
            'Swamp Palace Hidden Chest': [],
            'Swamp Palace Boss': [('item', 'flippers')]}
    },
    'Swamp Palace Left Treasury Chest': {
        'type': 'dungeonchest', 'dungeon': 'Swamp Palace',
        'link': {
            'Swamp Palace Gauntlet': []}
    },
    'Swamp Palace Right Treasury Chest': {
        'type': 'dungeonchest', 'dungeon': 'Swamp Palace',
        'link': {
            'Swamp Palace Gauntlet': []}
    },
    'Swamp Palace Hidden Chest': {
        'type': 'dungeonchest', 'dungeon': 'Swamp Palace',
        'link': {
            'Swamp Palace Gauntlet': []}
    },
    'Swamp Palace Boss': {
        'type': 'dungeonboss', 'dungeon': 'Swamp Palace',
        'link': {
            'Swamp Palace Boss Item': [('and', [
                ('item', 'hookshot'),
                ('or', [
                    ('settings', 'placement_advanced'),
                    ('settings', 'swordless'),
                    ('item', 'mastersword')]),
                ('or', [
                    ('item', 'hammer'),
                    ('item', 'sword'),
                    ('and', [
                        ('or', [
                            ('item', 'halfmagic'), ('item', 'bottle'),
                            ('item', 'bow')]),
                        ('or', [
                            ('item', 'firerod'), ('item', 'icerod')])])])])]}
    },
    'Swamp Palace Boss Item': {
        'type': 'dungeonchest_nokey', 'dungeon': 'Swamp Palace',
        'link': {
            'Swamp Palace Reward': []}
    },
    'Swamp Palace Reward': {
        'type': 'dungeonreward', 'dungeon': 'Swamp Palace',
        'link': {
            'Swamp Palace Entrance (I)': []}
    },
}
