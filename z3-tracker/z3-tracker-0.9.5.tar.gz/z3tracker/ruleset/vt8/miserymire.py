'''
Misery Mire
'''

__all__ = 'LOCATIONS',


LOCATIONS = {
    'Misery Mire Surface': {
        'type': 'area',
        'link': {
            'Desert': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Desert Ridge': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Misery Mire Treasury Entrance (E)': [],
            'Misery Mire Fairy Entrance (E)': [],
            'Desert Cave Valley': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Misery Mire Cave Entrance (E)': [],
            'Misery Mire Dungeon Entrance (E)': [('and', [
                ('medallion', 'Misery Mire'), ('item', 'sword')])]}
    },
    'Misery Mire Treasury Entrance (E)': {
        'type': 'entrance_unique', 'map': 'dark', 'coord': (20, 531),
        'link': {
            'Misery Mire Surface': [],
            'Misery Mire Treasury Entrance (I)': []}
    },
    'Misery Mire Treasury Entrance (I)': {
        'type': 'interior',
        'link': {
            'Misery Mire Treasury Entrance (E)': [],
            'Misery Mire Treasury': [('rabbitbarrier', None)]}
    },
    'Misery Mire Treasury': {
        'type': 'chest', 'map': 'dark', 'coord': (20, 528),
        'link': {
            'Misery Mire Treasury Entrance (I)': []}
    },
    'Misery Mire Fairy Entrance (E)': {
        'type': 'entrance', 'map': 'dark', 'coord': (66, 531),
        'link': {
            'Misery Mire Surface': [],
            'Misery Mire Fairy Entrance (I)': []}
    },
    'Misery Mire Fairy Entrance (I)': {
        'type': 'interior',
        'link': {
            'Misery Mire Fairy Entrance (E)': []}
    },
    'Misery Mire Cave Entrance (E)': {
        'type': 'entrance', 'map': 'dark', 'coord': (126, 547),
        'link': {
            'Misery Mire Surface': [],
            'Misery Mire Cave Entrance (I)': []}
    },
    'Misery Mire Cave Entrance (I)': {
        'type': 'interior',
        'link': {
            'Misery Mire Cave Entrance (E)': []}
    },
    'Desert Portal (DW)': {
        'type': 'area',
        'link': {
            'Desert Portal (LW)': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Desert Portal': [('item', 'titansmitts')],
            'Misery Mire Surface': []}
    },

    'Misery Mire Dungeon Entrance (E)': {
        'type': 'entrance_dungeon', 'map': 'dark', 'coord': (43, 553),
        'link': {
            'Misery Mire Surface': [],
            'Misery Mire Dungeon Entrance (I)': []}
    },
    'Misery Mire Dungeon Entrance (I)': {
        'type': 'interior',
        'link': {
            'Misery Mire Dungeon Entrance (E)': [],
            'Misery Mire Descent': [
                ('settings', 'placement_advanced'),
                ('and', [
                    ('or', [
                        ('settings', 'swordless'), ('item', 'mastersword')]),
                    ('or', [
                        ('item', 'bottle'), ('item', 'bluemail')])])]}
    },
    'Misery Mire Descent': {
        'type': 'area', 'dungeon': 'Misery Mire',
        'link': {
            'Misery Mire Dungeon Entrance (I)': [],
            'Misery Mire Interior': [
                    ('item', 'hookshot'),
                    ('and', [
                        ('item', 'pegasus'),
                        ('settings', 'placement_advanced')])]}
    },

    'Misery Mire Interior': {
        'type': 'area', 'dungeon': 'Misery Mire',
        'link': {
            'Misery Mire Descent': [
                ('item', 'hookshot'), ('item', 'pegasus'), ('item', 'mirror')],
            'Misery Mire Bridge Key': [],
            'Misery Mire Hidden Key': [],
            'Misery Mire Spike Key': [],
            'Misery Mire Map': [('smallkey', ('Misery Mire', 3))],
            'Misery Mire Treasure Room': [
                ('item', 'hookshot'), ('item', 'pegasus')],
            'Misery Mire Upper Key': [],
            'Misery Mire Switch Room': [('smallkey', ('Misery Mire', 3))],
            'Misery Mire Gauntlet Bridge': [('bigkey', 'Misery Mire')]}
    },
    'Misery Mire Bridge Key': {
        'type': 'dungeonchest', 'dungeon': 'Misery Mire',
        'link': {
            'Misery Mire Interior': []}
    },
    'Misery Mire Hidden Key': {
        'type': 'dungeonkey', 'dungeon': 'Misery Mire',
        'link': {
            'Misery Mire Interior': []}
    },
    'Misery Mire Spike Key': {
        'type': 'dungeonchest', 'dungeon': 'Misery Mire',
        'link': {
            'Misery Mire Interior': []}
    },
    'Misery Mire Map': {
        'type': 'dungeonchest', 'dungeon': 'Misery Mire',
        'link': {
            'Misery Mire Interior': []},
    },
    'Misery Mire Treasure Room': {
        'type': 'area', 'dungeon': 'Misery Mire',
        'link': {
            'Misery Mire Interior': [],
            'Misery Mire Treasure': [('bigkey', 'Misery Mire')]}
    },
    'Misery Mire Treasure': {
        'type': 'dungeonchest_nokey', 'dungeon': 'Misery Mire',
        'link': {
            'Misery Mire Interior': []},
    },
    'Misery Mire Upper Key': {
        'type': 'dungeonchest', 'dungeon': 'Misery Mire',
        'link': {
            'Misery Mire Interior': []},
    },

    'Misery Mire Switch Room': {
        'type': 'area', 'dungeon': 'Misery Mire',
        'link': {
            'Misery Mire Interior': [],
            'Misery Mire Bari Key': [],
            'Misery Mire Torch Room': [('smallkey', ('Misery Mire', 3))]}
    },
    'Misery Mire Bari Key': {
        'type': 'dungeonkey', 'dungeon': 'Misery Mire',
        'link': {
            'Misery Mire Switch Room': []}
    },
    'Misery Mire Torch Room': {
        'type': 'area', 'dungeon': 'Misery Mire',
        'link': {
            'Misery Mire Switch Room': [],
            'Misery Mire Compass': [('item', 'lantern'), ('item', 'firerod')],
            'Misery Mire Big Key': [('item', 'lantern'), ('item', 'firerod')]}
    },
    'Misery Mire Compass': {
        'type': 'dungeonchest', 'dungeon': 'Misery Mire',
        'link': {
            'Misery Mire Torch Room': [],
            'Misery Mire Interior': []}
    },
    'Misery Mire Big Key': {
        'type': 'dungeonchest', 'dungeon': 'Misery Mire',
        'link': {
            'Misery Mire Interior': []}
    },

    'Misery Mire Gauntlet Bridge': {
        'type': 'area', 'dungeon': 'Misery Mire',
        'link': {
            'Misery Mire Interior': [],
            'Misery Mire Gauntlet': [('item', 'somaria')]}
    },
    'Misery Mire Gauntlet': {
        'type': 'area', 'dungeon': 'Misery Mire',
        'link': {
            'Misery Mire Gauntlet Bridge': [],
            'Misery Mire Boss': [('item', 'bombs')]}
    },
    'Misery Mire Boss': {
        'type': 'dungeonboss', 'dungeon': 'Misery Mire',
        'link': {
            'Misery Mire Boss Item': [('and', [
                ('or', [
                    ('settings', 'placement_advanced'), ('item', 'mastersword'),
                    ('item', 'bow')]),
                ('or', [
                    ('item', 'hammer'), ('item', 'sword'), ('item', 'bow')])])]}
    },
    'Misery Mire Boss Item': {
        'type': 'dungeonchest_nokey', 'dungeon': 'Misery Mire',
        'link': {
            'Misery Mire Reward': []},
    },
    'Misery Mire Reward': {
        'type': 'dungeonreward', 'dungeon': 'Misery Mire',
        'link': {
            'Misery Mire Dungeon Entrance (I)': []}
    },
}
