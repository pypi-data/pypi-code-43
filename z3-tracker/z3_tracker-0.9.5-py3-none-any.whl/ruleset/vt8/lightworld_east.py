'''
Eastern Light World
'''

__all__ = 'LOCATIONS',


LOCATIONS = {
    'East Light World': {
        'type': 'area',
        'link': {
            'River Shop Area': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'East Dark World': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'Light Bottle Ocarina': [],
            'Witch Hut River': [
                ('item', 'flippers'),
                ('and', [('glitch', 'overworld'), ('rabbitbarrier', None)])],
            'Witch Hut Entrance (E)': [('rabbitbarrier', None)],
            'Witch': [('rabbitbarrier', None)],
            "Zora's River": [
                ('item', 'powerglove'),
                ('and', [
                    ('glitch', 'overworld'), ('item', 'pegasus')])],
            'North Light World': [],
            'Hyrule Castle': [('item', 'powerglove')],
            'South Light World': [],
            'East Fairy Cave Entrance (E)': [],
            'Lake Hylia': [('item', 'flippers')],
            'East Fairy Pond Entrance (E)': [],
            'East Portal (LW)': [('item', 'hammer')],
            "Sahasrahla's Hideout Entrance (E)": [],
            'East Palace Entrance (E)': []}
    },
    'Witch Hut River': {
        'type': 'area',
        'link': {
            'Dark River': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'East Light World': [],
            'North Light World': [],
            'Witch Hut Waterway': []}
    },
    'Witch Hut Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (531, 224),
        'link': {
            'East Light World': [('rabbitbarrier', None)],
            'Witch Hut Entrance (I)': []}
    },
    'Witch Hut Entrance (I)': {
        'type': 'interior',
        'link': {
            'Witch Hut Entrance (E)': [],
            'Witch Hut': [('and', [('access', 'Witch'), ('item', 'mushroom')])]}
    },
    'Witch Hut': {
        'type': 'chest', 'map': 'light', 'coord': (531, 215),
        'link': {
            'Witch Hut Entrance (I)': []}
    },
    'Witch': {
        'type': 'area',
        'link': {
            'East Light World': [('rabbitbarrier', None)]}
    },
    'East Fairy Cave Entrance (E)': {
        'type': 'entrance', 'map': 'light', 'coord': (546, 428),
        'link': {
            'East Light World': [],
            'East Fairy Cave Entrance (I)': []}
    },
    'East Fairy Cave Entrance (I)': {
        'type': 'interior',
        'link': {
            'East Fairy Cave Entrance (E)': []}
    },
    'East Fairy Pond Entrance (E)': {
        'type': 'entrance', 'map': 'light', 'coord': (650, 464),
        'link': {
            'East Light World': [],
            'East Fairy Pond Entrance (I)': []}
    },
    'East Fairy Pond Entrance (I)': {
        'type': 'interior',
        'link': {
            'East Fairy Pond Entrance (E)': []}
    },
    'East Portal (LW)': {
        'type': 'area',
        'link': {
            'East Portal (DW)': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'East Light World': [('item', 'hammer')], 
            'East Portal': [('item', 'powerglove')]}
    },
    'East Portal': {
        'type': 'area',
        'link': {
            'East Portal (DW)': [('and', [
                ('nosettings', 'inverted'), ('state', 'rabbit')])],
            'East Portal (LW)': [('and', [
                ('settings', 'inverted'), ('state', 'rabbit')])]}
    },
    "Sahasrahla's Hideout Entrance (E)": {
        'type': 'entrance_unique', 'map': 'light', 'coord': (537, 300),
        'link': {
            'East Light World': [],
            "Sahasrahla's Hideout Entrance (I)": []}
    },
    "Sahasrahla's Hideout Entrance (I)": {
        'type': 'interior',
        'link': {
            "Sahasrahla's Hideout Entrance (E)": [],
            "Sahasrahla's Hideout": []}
    },
    "Sahasrahla's Hideout": {
        'type': 'area',
        'link': {
            "Sahasrahla's Hideout Entrance (I)": [],
            "Sahasrahla's Reward": [('pendant', 'courage')],
            "Sahasrahla's Treasure": [('item', 'bombs'), ('item', 'pegasus')]}
    },
    "Sahasrahla's Reward": {
        'type': 'chest', 'map': 'light', 'coord': (537, 300),
        'link': {
            "Sahasrahla's Hideout": []}
    },
    "Sahasrahla's Treasure": {
        'type': 'cave', 'map': 'light', 'coord': (537, 284),
        'link': {
            "Sahasrahla's Hideout": []}
    },

    "Zora's River": {
        'type': 'area',
        'link': {
            'Catfish Approach': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'East Light World': [('item', 'powerglove')],
            'Waterfall Lake': [('item', 'flippers')],
            'King Zora': [],
            'Zora River Viewpoint': [
                ('item', 'flippers'),
                ('and', [
                    ('glitch', 'overworld'), ('item', 'pegasus')])]},
        'visible': {'Zora River Viewpoint': []}
    },
    'Waterfall Lake': {
        'type': 'area',
        'link': {
            'Zora River Waterway': [],
            "Zora's River": [],
            'Waterfall Fairy Entrance (E)': [
                ('item', 'flippers'),
                ('and', [
                    ('glitch', 'overworld'),
                    ('or', [
                        ('item', 'pearl'), ('item', 'pegasus')])])]}
    },
    'Waterfall Fairy Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (597, 89),
        'link': {
            'Waterfall Lake': [('item', 'flippers')],
            'Waterfall Fairy Entrance (I)': []}
    },
    'Waterfall Fairy Entrance (I)': {
        'type': 'interior',
        'link': {
            'Waterfall Fairy Entrance (E)': [],
            'Waterfall Fairy': []}
    },
    'Waterfall Fairy': {
        'type': 'cave', 'map': 'light', 'coord': (597, 89),
        'link': {
            'Waterfall Fairy Entrance (E)': []}
    },
    'King Zora': {
        'type': 'item', 'map': 'light', 'coord': (640, 100),
        'link': {
            "Zora's River": []}
    },
    'Zora River Viewpoint': {
        'type': 'item', 'map': 'light', 'coord': (640, 120),
        'link': {
            "Zora's River": [('item', 'flippers')]}
    },

    'East Palace Entrance (E)': {
        'type': 'entrance_dungeon', 'map': 'light', 'coord': (636, 272),
        'link': {
            'East Palace Entrance (E)': [],
            'East Palace Entrance (I)': []}
    },
    'East Palace Entrance (I)': {
        'type': 'interior',
        'link': {
            'East Palace Entrance (E)': [],
            'East Palace Interior': [('rabbitbarrier', None)]}
    },
    'East Palace Interior': {
        'type': 'area', 'dungeon': 'East Palace',
        'link': {
            'East Palace Entrance (I)': [],
            'East Palace Rupee': [],
            'East Palace Map': [],
            'East Palace Compass': [],
            'East Palace Treasure': [('bigkey', 'East Palace')],
            'East Palace Dark Room': [('item', 'lantern')],
            'East Palace Boss Door': [('bigkey', 'East Palace')]}
    },
    'East Palace Rupee': {
        'type': 'dungeonchest', 'dungeon': 'East Palace',
        'link': {
            'East Palace Interior': []}
    },
    'East Palace Map': {
        'type': 'dungeonchest', 'dungeon': 'East Palace',
        'link': {
            'East Palace Interior': []}
    },
    'East Palace Compass': {
        'type': 'dungeonchest', 'dungeon': 'East Palace',
        'link': {
            'East Palace Interior': []}
    },
    'East Palace Treasure': {
        'type': 'dungeonchest_nokey', 'dungeon': 'East Palace',
        'link': {
            'East Palace Interior': []}
    },
    'East Palace Dark Room': {
        'type': 'area', 'dungeon': 'East Palace',
        'link': {
            'East Palace Interior': [],
            'East Palace Hidden Key': [],
            'East Palace Big Key': [('smallkey', ('East Palace', 0))]}
    },
    'East Palace Hidden Key': {
        'type': 'dungeonkey', 'dungeon': 'East Palace',
        'link': {
            'East Palace Dark Room': []}
    },
    'East Palace Big Key': {
        'type': 'dungeonchest', 'dungeon': 'East Palace',
        'link': {
            'East Palace Dark Room': []}
    },
    'East Palace Boss Door': {
        'type': 'area', 'dungeon': 'East Palace',
        'link': {
            'East Palace Interior': [],
            'East Palace Gauntlet Entrance': [
                ('item', 'lantern'),
                ('and', [
                    ('settings', 'placement_advanced'), ('item', 'firerod')])]}
    },
    'East Palace Gauntlet Entrance': {
        'type': 'area', 'dungeon': 'East Palace',
        'link': {
            'East Palace Boss Door': [],
            'East Palace Eyegore Key': [],
            'East Palace Gauntlet': [('smallkey', ('East Palace', 0))]}
    },
    'East Palace Eyegore Key': {
        'type': 'dungeonkey', 'dungeon': 'East Palace',
        'link': {
            'East Palace Gauntlet Entrance': []}
    },
    'East Palace Gauntlet': {
        'type': 'area', 'dungeon': 'East Palace',
        'link': {
            'East Palace Gauntlet Entrance': [
                ('item', 'lantern'),
                ('and', [
                    ('settings', 'placement_advanced'), ('item', 'firerod')])],
            'East Palace Boss': [('item', 'bow')]}
    },
    'East Palace Boss': {
        'type': 'dungeonboss', 'dungeon': 'East Palace',
        'link': {
            'East Palace Boss Item': [
                ('item', 'sword'), ('item', 'hammer'), ('item', 'bow'),
                ('item', 'boomerang'),
                ('and', [
                    ('or', [
                        ('item', 'bottle'), ('item', 'halfmagic')]),
                    ('or', [
                        ('item', 'firerod'), ('item', 'icerod'),
                        ('item', 'byrna'), ('item', 'somaria')])])]}
    },
    'East Palace Boss Item': {
        'type': 'dungeonchest_nokey', 'dungeon': 'East Palace',
        'link': {
            'East Palace Reward': []}
    },
    'East Palace Reward': {
        'type': 'dungeonreward', 'dungeon': 'East Palace',
        'link': {
            'East Palace Entrance (I)': []}
    },
}
