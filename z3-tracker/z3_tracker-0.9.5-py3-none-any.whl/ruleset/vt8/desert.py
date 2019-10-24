'''
Desert
'''

__all__ = 'LOCATIONS',


LOCATIONS = {
    'Desert': {
        'type': 'area',
        'link': {
            'Misery Mire Surface': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'Light Bottle Ocarina': [],
            'Southern Shores': [],
            "Aginah's Cave Entrance (E)": [],
            'Desert Cave Valley': [
                ('settings', 'inverted'),
                ('glitch', 'major'),
                ('and', [
                    ('glitch', 'overworld'), ('item', 'pegasus')])],
            'Desert Palace Stairs': [('item', 'mudora')],
            'Desert Portal (LW)': [('and', [
                ('glitch', 'overworld'), ('item', 'pegasus')])],
            'Desert Ridge': [('and', [
                ('glitch', 'overworld'), ('item', 'pegasus')])]},
        'visible': {"Vulture's Heart": []}
    },
    "Aginah's Cave Entrance (E)": {
        'type': 'entrance_unique', 'map': 'light', 'coord': (132, 546),
        'link': {
            'Desert': [],
            "Aginah's Cave Entrance (I)": []}
    },
    "Aginah's Cave Entrance (I)": {
        'type': 'interior',
        'link': {
            "Aginah's Cave Entrance (E)": [],
            "Aginah's Cave Interior": []}
    },
    "Aginah's Cave Interior": {
        'type': 'area',
        'link': {
            "Aginah's Cave Entrance (I)": [],
            "Aginah's Cave": [('item', 'bombs')]}
    },
    "Aginah's Cave": {
        'type': 'cave', 'map': 'light', 'coord': (132, 546),
        'link': {
            "Aginah's Cave Interior": []}
    },
    'Desert Cave Valley': {
        'type': 'area',
        'link': {
            'Misery Mire Surface': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'Desert': [],
            'Desert Cave Entrance (E)': [('item', 'powerglove')]}
    },
    'Desert Cave Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (116, 515),
        'link': {
            'Desert Cave Valley': [],
            'Desert Cave Entrance (I)': []}
    },
    'Desert Cave Entrance (I)': {
        'type': 'interior',
        'link': {
            'Desert Cave Entrance (E)': [],
            'Desert Cave': []}
    },
    'Desert Cave': {
        'type': 'drop', 'map': 'light', 'coord': (116, 515),
        'link': {
            'Desert Cave Entrance (I)': []}
    },

    'Desert Portal (LW)': {
        'type': 'area',
        'link': {
            'Desert Portal (DW)': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'Desert Portal': [('item', 'titansmitts')],
            'Desert': []}
    },
    'Desert Portal': {
        'type': 'area',
        'link': {
            'Desert Portal (DW)': [('and', [
                ('nosettings', 'inverted'), ('state', 'rabbit')])],
            'Desert Portal (LW)': [('and', [
                ('settings', 'inverted'), ('state', 'rabbit')])]}
    },

    'Desert Palace Stairs': {
        'type': 'area',
        'link': {
            'Misery Mire Surface': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'Desert Palace Main Entrance Entrance (E)': []}
    },
    'Desert Palace Main Entrance Entrance (E)': {
        'type': 'entrance_dungeon', 'map': 'light', 'coord': (49, 549),
        'link': {
            'Desert Palace Stairs': [],
            'Desert Palace Main Entrance Entrance (I)': []}
    },
    'Desert Palace Main Entrance Entrance (I)': {
        'type': 'interior',
        'link': {
            'Desert Palace Main Entrance Entrance (E)': [],
            'Desert Palace Interior': [('rabbitbarrier', None)]}
    },
    'Desert Palace Side Entrance Entrance (I)': {
        'type': 'interior',
        'link': {
            'Desert Palace Side Entrance Entrance (E)': [],
            'Desert Palace Interior': [('rabbitbarrier', None)]}
    },
    'Desert Palace Side Entrance Entrance (E)': {
        'type': 'entrance_dungeon', 'map': 'light', 'coord': (75, 527),
        'link': {
            'Desert': [],
            'Desert Palace Side Entrance Entrance (I)': []}
    },

    'Desert Palace Interior': {
        'type': 'area', 'dungeon': 'Desert Palace',
        'link': {
            'Desert Palace Main Entrance Entrance (I)': [],
            'Desert Palace Side Entrance Entrance (I)': [],
            'Desert Palace Back Entrance Entrance (I)': [],
            'Desert Palace Compass': [('smallkey', ('Desert Palace', 2))],
            'Desert Palace Map': [],
            'Desert Palace Small Key': [('item', 'pegasus')],
            'Desert Palace Treasure': [('bigkey', 'Desert Palace')]}
    },
    'Desert Palace Compass': {
        'type': 'dungeonchest', 'dungeon': 'Desert Palace',
        'link': {
            'Desert Palace Interior': [],
            'Desert Palace Big Key': []}
    },
    'Desert Palace Big Key': {
        'type': 'dungeonchest', 'dungeon': 'Desert Palace',
        'link': {
            'Desert Palace Compass': []}
    },
    'Desert Palace Map': {
        'type': 'dungeonchest', 'dungeon': 'Desert Palace',
        'link': {
            'Desert Palace Interior': []}
    },
    'Desert Palace Small Key': {
        'type': 'dungeonchest', 'dungeon': 'Desert Palace',
        'link': {
            'Desert Palace Interior': []}
    },
    'Desert Palace Treasure': {
        'type': 'dungeonchest_nokey', 'dungeon': 'Desert Palace',
        'link': {
            'Desert Palace Interior': []}
    },
    'Desert Palace Back Entrance Entrance (I)': {
        'type': 'interior',
        'link': {
            'Desert Palace Back Entrance Entrance (E)': [],
            'Desert Palace Interior': [('rabbitbarrier', None)]}
    },
    'Desert Palace Back Entrance Entrance (E)': {
        'type': 'entrance_dungeon', 'map': 'light', 'coord': (23, 527),
        'link': {
            'Desert Ridge': [],
            'Desert Palace Back Entrance Entrance (I)': []}
    },

    'Desert Ridge': {
        'type': 'area',
        'link': {
            'Misery Mire Surface': [('and', [
                ('settings',  'inverted'), ('item', 'mirror')])],
            'Desert Palace Back Entrance Entrance (E)': [],
            'Desert': [],
            "Vulture's Heart": [],
            'Desert Palace Gauntlet Entrance': [('item', 'powerglove')]}
    },
    "Vulture's Heart": {
        'type': 'item', 'map': 'light', 'coord': (16, 606),
        'link': {
            'Desert Ridge': []}
    },
    'Desert Palace Gauntlet Entrance': {
        'type': 'area',
        'link': {
            'Misery Mire Surface': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'Desert Ridge': [('item', 'powerglove')],
            'Desert Palace Gauntlet Entrance (E)': []}
    },
    'Desert Palace Gauntlet Entrance (E)': {
        'type': 'entrance_dungeon', 'map': 'light', 'coord': (49, 507),
        'link': {
            'Desert Palace Gauntlet Entrance': [],
            'Desert Palace Gauntlet Entrance (I)': []}
    },
    'Desert Palace Gauntlet Entrance (I)': {
        'type': 'interior',
        'link': {
            'Desert Palace Gauntlet Entrance (E)': [],
            'Desert Palace Trap Room 1': [('rabbitbarrier', None)]}
    },
    'Desert Palace Trap Room 1': {
        'type': 'area', 'dungeon': 'Desert Palace',
        'link': {
            'Desert Palace Gauntlet Entrance (I)': [],
            'Desert Palace Hidden Key 1': [],
            'Desert Palace Trap Room 2': [('smallkey', ('Desert Palace', 2))]}
    },
    'Desert Palace Hidden Key 1': {
        'type': 'dungeonkey', 'dungeon': 'Desert Palace',
        'link': {
            'Desert Palace Trap Room 1': []}
    },
    'Desert Palace Trap Room 2': {
        'type': 'area', 'dungeon': 'Desert Palace',
        'link': {
            'Desert Palace Trap Room 1': [],
            'Desert Palace Hidden Key 2': [],
            'Desert Palace Torch Room': [('smallkey', ('Desert Palace', 2))]}
    },
    'Desert Palace Hidden Key 2': {
        'type': 'dungeonkey', 'dungeon': 'Desert Palace',
        'link': {
            'Desert Palace Trap Room 2': []}
    },
    'Desert Palace Torch Room': {
        'type': 'area', 'dungeon': 'Desert Palace',
        'link': {
            'Desert Palace Trap Room 2': [],
            'Desert Palace Boss': [('and', [
                ('or', [('item', 'lantern'), ('item', 'firerod')]),
                ('bigkey', 'Desert Palace')])]}
    },
    'Desert Palace Boss': {
        'type': 'dungeonboss', 'dungeon': 'Desert Palace',
        'link': {
            'Desert Palace Boss Item': [
                ('item', 'sword'), ('item', 'hammer'), ('item', 'bow'),
                ('item', 'firerod'), ('item', 'icerod'), ('item', 'byrna'),
                ('item', 'somaria')]}
        },
    'Desert Palace Boss Item': {
        'type': 'dungeonchest_nokey', 'dungeon': 'Desert Palace',
        'link': {
            'Desert Palace Reward': []}
    },
    'Desert Palace Reward': {
        'type': 'dungeonreward', 'dungeon': 'Desert Palace',
        'link': {
            'Desert Palace Main Entrance Entrance (I)': []}
    },
}
