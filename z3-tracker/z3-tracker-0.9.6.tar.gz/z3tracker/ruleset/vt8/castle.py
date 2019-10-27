'''
Hyrule Castle
'''

__all__ = 'LOCATIONS',


LOCATIONS = {
    'Hyrule Castle': {
        'type': 'area',
        'link': {
            'Pyramid': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'North Light World': [],
            'South Light World': [],
            'East Light World': [('item', 'powerglove')],
            'Secret Path Drop Entrance (E)': [('rabbitbarrier', None)],
            'Gate Portal': [('and', [
                ('access', 'Castle Tower Reward'),
                ('nosettings', 'inverted')])],
            'Secret Path Exit Entrance (E)': [('rabbitbarrier', None)],
            'Castle Gates Entrance (E)': []}
    },
    'Gate Portal': {
        'type': 'area',
        'link': {
            'Pyramid': [('state', 'rabbit')]}
    },
    'Secret Path Drop Entrance (E)': {
        'type': 'entrance_drop', 'map': 'light', 'coord': (395, 276),
        'link': {
            'Secret Path Drop Entrance (I)': []}
    },
    'Secret Path Drop Entrance (I)': {
        'type': 'interior',
        'link': {
            'Secret Path': []}
    },
    'Secret Path': {
        'type': 'drop', 'map': 'light', 'coord': (365, 284),
        'link': {
            'Secret Path Exit Entrance (I)': []}
    },
    'Secret Path Exit Entrance (I)': {
        'type': 'interior',
        'link': {
            'Secret Path': [],
            'Secret Path Exit Entrance (E)': []}
    },
    'Secret Path Exit Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (365, 284),
        'link': {
            'Secret Path Exit Entrance (I)': [],
            'Hyrule Castle': []}
    },

    'Castle Gates Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (332, 291),
        'link': {
            'Hyrule Castle': [],
            'Castle Gates Entrance (I)': []}
    },
    'Castle Gates Entrance (I)': {
        'type': 'interior',
        'link': {
            'Castle Gates Entrance (E)': [],
            'Hyrule Castle Interior': []}
    },
    'Hyrule Castle Interior': {
        'type': 'area', 'dungeon': 'Castle Dungeons',
        'link': {
            'Castle Gates Entrance (I)': [],
            'Western Wall Access Entrance (I)': [],
            'Eastern Wall Access Entrance (I)': [],
            'Secret Escape': [
                ('and', [('access', 'Zelda'), ('rabbitbarrier', None)]),
                ('nosettings', 'standard')],
            'Dungeons Descent 1': []}
    },
    'Dungeons Descent 1': {
        'type': 'area', 'dungeon': 'Castle Dungeons',
        'link': {
            'Hyrule Castle Interior': [],
            'Dungeons Map': [],
            'Dungeons First Soldier Key': [('rabbitbarrier', None)],
            'Dungeons Descent 2': [('smallkey', ('Castle Dungeons', 1))]}
    },
    'Dungeons Map': {
        'type': 'dungeonchest', 'dungeon': 'Castle Dungeons',
        'link': {
            'Dungeons Descent 1': []}
    },
    'Dungeons First Soldier Key': {
        'type': 'dungeonkey', 'dungeon': 'Castle Dungeons',
        'link': {
            'Dungeons Descent 1': []}
    },
    'Dungeons Descent 2': {
        'type': 'area', 'dungeon': 'Castle Dungeons',
        'link': {
            'Dungeons Descent 1': [],
            'Dungeons Second Soldier Key': [],
            'Dungeons Treasure': [],
            'Dungeons Cells': [('smallkey', ('Castle Dungeons', 1))]}
    },
    'Dungeons Second Soldier Key': {
        'type': 'dungeonkey', 'dungeon': 'Castle Dungeons',
        'link': {
            'Dungeons Descent 2': []}
    },
    'Dungeons Treasure': {
        'type': 'dungeonchest', 'dungeon': 'Castle Dungeons',
        'link': {
            'Dungeons Descent 2': []}
    },
    'Dungeons Cells': {
        'type': 'area', 'dungeon': 'Castle Dungeons',
        'link': {
            'Dungeons Descent 2': [],
            'Dungeons Big Key': []}
    },
    'Dungeons Big Key': {
        'type': 'area', 'dungeon': 'Castle Dungeons',
        'link': {
            'Dungeons Cells': [],
            'Zelda': []}
    },
    'Zelda': {
        'type': 'area', 'dungeon': 'Castle Dungeons',
        'link': {
            'Dungeons Cells': [],
            "Zelda's Treasure": []}
    },
    "Zelda's Treasure": {
        'type': 'dungeonchest', 'dungeon': 'Castle Dungeons',
        'link': {
            'Zelda': [],
            'Castle Dungeons': [('rabbitbarrier', None)]}
    },

    'Secret Escape': {
        'type': 'area', 'dungeon': 'Castle Dungeons',
        'link': {
            'Hyrule Castle Interior': [],
            'Sewers': [
                ('item', 'lantern'), ('settings', 'standard'),
                ('and', [
                    ('settings', 'placement_advanced'), ('item', 'firerod')])]}
    },
    'Sewers': {
        'type': 'area', 'dungeon': 'Castle Dungeons',
        'link': {
            'Sewers Chest': [('rabbitbarrier', None)],
            'Sewers Rat Key': [],
            'Sewers Locked Door': [('smallkey', ('Castle Dungeons', 1))]}
    },
    'Sewers Chest': {
        'type': 'drop', 'map': 'light', 'coord': (344, 223),
        'link': {
            'Sewers': [],
            'Sewers Dungeon Chest': []}
    },
    'Sewers Dungeon Chest': {
        'type': 'dungeonchest', 'dungeon': 'Castle Dungeons',
        'link': {
            'Sewers Chest': []}
    },
    'Sewers Rat Key': {
        'type': 'dungeonkey', 'dungeon': 'Castle Dungeons',
        'link': {
            'Sewers': []}
    },
    'Sewers Locked Door': {
        'type': 'area', 'dungeon': 'Castle Dungeons',
        'link': {
            'Sewers': [
                ('item', 'lantern'), ('settings', 'standard'),
                ('and', [
                    ('settings', 'placement_advanced'), ('item', 'firerod')])],
            'Sewers Last Hall': [('state', 'maybe;add')]}
    },
    'Sewers Last Hall': {
        'type': 'area', 'dungeon': 'Castle Dungeons',
        'link': {
            'Sewers Locked Door': [('state', 'maybe;add')],
            'Sewers Treasure': [('item', 'bombs'), ('item', 'pegasus')],
            'Sanctuary': [('rabbitbarrier', None)]}
    },
    'Sewers Treasure': {
        'type': 'drop', 'map': 'light', 'coord': (344, 193),
        'link': {
            'Sewers Last Hall': [],
            'Sewers Treasure Chest 1': [],
            'Sewers Treasure Chest 2': [],
            'Sewers Treasure Chest 3': []}
    },
    'Sewers Treasure Chest 1': {
        'type': 'dungeonchest', 'dungeon': 'Castle Dungeons',
        'link': {
            'Sewers Treasure': []}
    },
    'Sewers Treasure Chest 2': {
        'type': 'dungeonchest', 'dungeon': 'Castle Dungeons',
        'link': {
            'Sewers Treasure': []}
    },
    'Sewers Treasure Chest 3': {
        'type': 'dungeonchest', 'dungeon': 'Castle Dungeons',
        'link': {
            'Sewers Treasure': []}
    },
    'Sanctuary': {
        'type': 'chest', 'map': 'light', 'coord': (306, 172),
        'link': {
            'Sanctuary Entrance Entrance (I)': []}
    },

    'Western Wall Access Entrance (I)': {
        'type': 'interior',
        'link': {
            'Hyrule Castle Interior': [],
            'Western Wall Access Entrance (E)': []}
    },
    'Eastern Wall Access Entrance (I)': {
        'type': 'interior',
        'link': {
            'Hyrule Castle Interior': [],
            'Eastern Wall Access Entrance (E)': []}
    },
    'Western Wall Access Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (298, 257),
        'link': {
            'Western Wall Access Entrance (I)': [],
            'Castle Walls': []}
    },
    'Eastern Wall Access Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (365, 257),
        'link': {
            'Eastern Wall Access Entrance (I)': [],
            'Castle Walls': []}
    },
    'Castle Walls': {
        'type': 'area',
        'link': {
            'Pyramid': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'Western Wall Access Entrance (E)': [],
            'Eastern Wall Access Entrance (E)': [],
            'Hyrule Castle': [],
            'Ganon Drop Entrance (E)': [('and', [
                ('settings', 'inverted'), ('macro', 'ganon')])],
            'Castle Tower Entrance (E)': [
                ('and', [
                    ('nosettings', 'inverted'),
                    ('or', [
                        ('item', 'mastersword'), ('item', 'cape'),
                        ('and', [
                            ('settings', 'swordless'),
                            ('item', 'hammer')])])]),
                ('and', [
                    ('settings', 'inverted'), ('macro', 'ganonstower')])]}
    },
    'Castle Tower Entrance (E)': {
        'type': 'entrance_dungeon', 'map': 'light', 'coord': (332, 265),
        'link': {
            'Castle Walls': [],
            'Castle Tower Entrance (I)': [('nosettings', 'inverted')],
            "Ganon's Tower Entrance (I)": [('settings', 'inverted')]}
    },
    'Castle Tower Entrance (I)': {
        'type': 'interior',
        'link': {
            'Castle Tower Entrance (E)': [('nosettings', 'inverted')],
            "Ganon's Tower Entrance (E)": [('settings', 'inverted')],
            'Castle Tower Ascent 1': []}
    },
    'Castle Tower Ascent 1': {
        'type': 'area', 'dungeon': 'Castle Tower',
        'link': {
            'Castle Tower Entrance (I)': [],
            'Castle Tower First Chest': [],
            'Castle Tower Ascent Stairs': [('smallkey', ('Castle Tower', 1))]}
    },
    'Castle Tower First Chest': {
        'type': 'dungeonchest', 'dungeon': 'Castle Tower',
        'link': {
            'Castle Tower Ascent 1': []}
    },
    'Castle Tower Ascent Stairs': {
        'type': 'area', 'dungeon': 'Castle Tower',
        'link': {
            'Castle Tower First Chest': [],
            'Castle Tower Ascent 2': [
                ('item', 'lantern'),
                ('and', [
                    ('settings', 'placement_advanced'), ('item', 'firerod')])]}
    },
    'Castle Tower Ascent 2': {
        'type': 'area', 'dungeon': 'Castle Tower',
        'link': {
            'Castle Tower Ascent Stairs': [],
            'Castle Tower Second Chest': [],
            'Castle Tower Ascent 3': [('smallkey', ('Castle Tower', 2))]}
    },
    'Castle Tower Second Chest': {
        'type': 'dungeonchest', 'dungeon': 'Castle Tower',
        'link': {
            'Castle Tower Ascent 2': []}
    },
    'Castle Tower Ascent 3': {
        'type': 'area', 'dungeon': 'Castle Tower',
        'link': {
            'Castle Tower Ascent 2': [
                ('item', 'lantern'),
                ('and', [
                    ('settings', 'placement_advanced'), ('item', 'firerod')])],
            'Castle Tower Boss': [('item', 'sword'), ('settings', 'swordless')]}
    },
    'Castle Tower Boss': {
        'type': 'dungeonboss', 'dungeon': 'Castle Tower',
        'link': {
            'Castle Tower Boss Item': [
                ('item', 'sword'),
                ('and', [
                    ('settings', 'swordless'), ('item', 'hammer')]),
                ('item', 'bugnet')]}
    },
    'Castle Tower Boss Item': {
        'type': 'area', 'dungeon': 'Castle Tower',
        'link': {
            'Castle Tower Reward': [('boss', 'Castle Tower')]}
    },
    'Castle Tower Reward': {
        'type': 'area', 'dungeon': 'Castle Tower',
        'link': {
            'Pyramid': [('and', [
                ('nosettings', 'inverted'), ('state', 'rabbit')])],
            'Castle Walls': [('and', [
                ('settings', 'inverted'), ('state', 'rabbit')])]}
    },
}
