'''
Thieves' Town
'''

__all__ = 'LOCATIONS',


LOCATIONS = {
    "Thieves' Town Surface": {
        'type': 'area',
        'link': {
            'Kakariko': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'South Light World': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Dark Bottle Ocarina': [],
            'South Dark World': [],
            'Frog Prison': [('item', 'titansmitts')],
            "East Thieves' Town": [
                ('item', 'titansmitts'),
                ('or', [
                    ('and', [
                        ('glitch', 'overworld'), ('item', 'pegasus')]),
                    ('glitch', 'major')])],
            "Thieves' Town Southern House Entrance (E)": [('item', 'bombs')],
            "Thieves' Town Shop Entrance (E)": [('item', 'hammer')],
            "Thieves' Town Eastern House Entrance (E)": [],
            "Thieves' Town Underground Entrance (E)": [('rabbitbarrier', None)],
            "Thieves' Town Western House Entrance (E)": [],
            'Skull Woods Surface': [],
            'Kakariko Portal (DW)': [('item', 'titansmitts')],
            'North Dark World': []}
    },
    'Frog Prison': {
        'type': 'area',
        'link': {
            'South Light World': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            "Thieves' Town Surface": [('item', 'titansmitts')]}
    },
    "Thieves' Town Southern House Entrance (E)": {
        'type': 'entrance_unique', 'map': 'dark', 'coord': (67, 386),
        'link': {
            "Thieves' Town Surface": [],
            "Thieves' Town Southern House Entrance (I)": []}
    },
    "Thieves' Town Southern House Entrance (I)": {
        'type': 'interior',
        'link': {
            "Thieves' Town Southern House Entrance (E)": [],
            'Sealed House': []}
    },
    'Sealed House': {
        'type': 'chest', 'map': 'dark', 'coord': (67, 383),
        'link': {
            "Thieves' Town Southern House Entrance (E)": []}
    },
    "Thieves' Town Shop Entrance (E)": {
        'type': 'entrance_shop', 'map': 'dark', 'coord': (129, 353),
        'link': {
            "Thieves' Town Surface": [('item', 'hammer')],
            "Thieves' Town Shop Entrance (I)": []}
    },
    "Thieves' Town Shop Entrance (I)": {
        'type': 'interior',
        'link': {
            "Thieves' Town Shop Entrance (E)": []}
    },
    "Thieves' Town Eastern House Entrance (E)": {
        'type': 'entrance_unique', 'map': 'dark', 'coord': (131, 320),
        'link': {
            "Thieves' Town Surface": [],
            "Thieves' Town Eastern House Entrance (I)": []}
    },
    "Thieves' Town Eastern House Entrance (I)": {
        'type': 'interior',
        'link': {
            "Thieves' Town Eastern House Entrance (E)": [],
            'Deserted House': []}
    },
    'Deserted House': {
        'type': 'chest', 'map': 'dark', 'coord': (131, 314),
        'link': {
            "Thieves' Town Eastern House Entrance (I)": []}
    },
    "Thieves' Town Western House Entrance (E)": {
        'type': 'entrance_unique', 'map': 'dark', 'coord': (28, 310),
        'link': {
            "Thieves' Town Surface": [],
            "Thieves' Town Western House Entrance (I)": []}
    },
    "Thieves' Town Western House Entrance (I)": {
        'type': 'interior',
        'link': {
            "Thieves' Town Western House Entrance (E)": [],
            'Chest Game': []}
    },
    'Chest Game': {
        'type': 'chest', 'map': 'dark', 'coord': (28, 304),
        'link': {
            "Thieves' Town Western House Entrance (I)": []}
    },

    "East Thieves' Town": {
        'type': 'area',
        'link': {
            'Kakariko': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Above The Bat': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            "Thieves' Town Surface": [('item', 'titansmitts')],
            'Locked Chest': [('access', 'Blacksmiths')],
            'Stake Cave Entrance (E)': [('item', 'hammer')]}
    },
    'Locked Chest': {
        'type': 'area',
        'link': {
            "East Thieves' Town": []}
    },
    'Stake Cave Entrance (E)': {
        'type': 'entrance_unique', 'map': 'dark', 'coord': (204, 401),
        'link': {
            "East Thieves' Town": [],
            'Stake Cave Entrance (I)': []}
    },
    'Stake Cave Entrance (I)': {
        'type': 'interior',
        'link': {
            'Stake Cave Entrance (E)': [],
            'Stake Cave': []}
    },
    'Stake Cave': {
        'type': 'drop', 'map': 'dark', 'coord': (204, 401),
        'link': {
            'Stake Cave Entrance (I)': []}
    },

    "Thieves' Town Underground Entrance (E)": {
        'type': 'entrance_dungeon', 'map': 'dark', 'coord': (77, 322),
        'link': {
            "Thieves' Town Surface": [],
            "Thieves' Town Underground Entrance (I)": []}
    },
    "Thieves' Town Underground Entrance (I)": {
        'type': 'interior',
        'link': {
            "Thieves' Town Underground Entrance (E)": [],
            "Thieves' Town Underground": [
                ('settings', 'placement_advanced'),
                ('and', [
                    ('or', [
                        ('settings', 'swordless'), ('item', 'sword')]),
                    ('item', 'bottle')])]}
    },
    "Thieves' Town Underground": {
        'type': 'area', 'dungeon': "Thieves' Town",
        'link': {
            "Thieves' Town Underground Entrance (I)": [],
            "Thieves' Town Map": [('rabbitbarrier', None)],
            "Thieves' Town Rupees": [('rabbitbarrier', None)],
            "Thieves' Town Compass": [('rabbitbarrier', None)],
            "Thieves' Town Big Key": [('rabbitbarrier', None)],
            "Thieves' Town Boss Hall": [('bigkey', "Thieves' Town")]}
    },
    "Thieves' Town Map": {
        'type': 'dungeonchest', 'dungeon': "Thieves' Town",
        'link': {
            "Thieves' Town Underground": []}
    },
    "Thieves' Town Rupees": {
        'type': 'dungeonchest', 'dungeon': "Thieves' Town",
        'link': {
            "Thieves' Town Underground": []}
    },
    "Thieves' Town Compass": {
        'type': 'dungeonchest', 'dungeon': "Thieves' Town",
        'link': {
            "Thieves' Town Underground": []}
    },
    "Thieves' Town Big Key": {
        'type': 'dungeonchest', 'dungeon': "Thieves' Town",
        'link': {
            "Thieves' Town Underground": []}
    },
    "Thieves' Town Boss Hall": {
        'type': 'area', 'dungeon': "Thieves' Town",
        'link': {
            "Thieves' Town Underground": [],
            "Thieves' Town First Hidden Key": [('rabbitbarrier', None)],
            "Thieves' Town Boss": [('and', [
                ('access', "Thieves' Town Attic"),
                ('access', "Thieves' Town Blind's Cell")])],
            "Thieves' Town Gauntlet": [('smallkey', ("Thieves' Town", 4))]}
    },
    "Thieves' Town First Hidden Key": {
        'type': 'area', 'dungeon': "Thieves' Town",
        'link': {
            "Thieves' Town Boss Hall": []}
    },
    "Thieves' Town Gauntlet": {
        'type': 'area', 'dungeon': "Thieves' Town",
        'link': {
            "Thieves' Town Boss Hall": [('rabbitbarrier', None)],
            "Thieves' Town Second Hidden Key": [('rabbitbarrier', None)],
            "Thieves' Town Attic": [('smallkey', ("Thieves' Town", 4))],
            "Thieves' Town Dungeons": []}
    },
    "Thieves' Town Second Hidden Key": {
        'type': 'dungeonkey', 'dungeon': "Thieves' Town",
        'link': {
            "Thieves' Town Gauntlet": []}
    },
    "Thieves' Town Attic": {
        'type': 'area', 'dungeon': "Thieves' Town",
        'link': {
            "Thieves' Town Gauntlet": [],
            "Thieves' Town Bombs": [('rabbitbarrier', None)]}
    },
    "Thieves' Town Bombs": {
        'type': 'dungeonchest_nokey', 'dungeon': "Thieves' Town",
        'link': {
            "Thieves' Town Attic": []}
    },
    "Thieves' Town Dungeons": {
        'type': 'area', 'dungeon': "Thieves' Town",
        'link': {
            "Thieves' Town Gauntlet": [],
            "Thieves' Town Treasure Room": [('smallkey', ("Thieves' Town", 4))],
            "Thieves' Town Blind's Cell": [('bigkey', "Thieves' Town")]}
    },
    "Thieves' Town Treasure Room": {
        'type': 'area', 'dungeon': "Thieves' Town",
        'link': {
            "Thieves' Town Dungeons": [],
            "Thieves' Town Treasure": [('item', 'hammer')]}
    },
    "Thieves' Town Treasure": {
        'type': 'dungeonchest_nokey', 'dungeon': "Thieves' Town",
        'link': {
            "Thieves' Town Treasure Room": [('item', 'hammer')]}
    },
    "Thieves' Town Blind's Cell": {
        'type': 'area', 'dungeon': "Thieves' Town",
        'link': {
            "Thieves' Town Dungeons": [],
            "Thieves' Town Blind's Key": []}
    },
    "Thieves' Town Blind's Key": {
        'type': 'dungeonchest_nokey', 'dungeon': "Thieves' Town",
        'link': {
            "Thieves' Town Blind's Cell": []}
    },
    "Thieves' Town Boss": {
        'type': 'dungeonboss', 'dungeon': "Thieves' Town",
        'link': {
            "Thieves' Town Boss Item": [('and', [
                ('or', [
                    ('settings', 'placement_advanced'),
                    ('settings', 'swordless'),
                    ('and', [
                        ('item', 'sword'),
                        ('or', [
                            ('item', 'cape'), ('item', 'byrna')])])]),
                ('or', [
                    ('item', 'sword'), ('item', 'hammer'),
                    ('item', 'byrna'), ('item', 'somaria')])])]}
    },
    "Thieves' Town Boss Item": {
        'type': 'dungeonchest_nokey', 'dungeon': "Thieves' Town",
        'link': {
            "Thieves' Town Reward": []}
    },
    "Thieves' Town Reward": {
        'type': 'dungeonreward', 'dungeon': "Thieves' Town",
        'link': {
            "Thieves' Town Underground Entrance (I)": []}
    },
}
