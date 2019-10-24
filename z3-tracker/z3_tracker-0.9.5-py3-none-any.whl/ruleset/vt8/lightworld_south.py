'''
Southern Light World
'''

__all__ = 'LOCATIONS',


LOCATIONS = {
    'South Light World': {
        'type': 'area',
        'link': {
            'South Dark World': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'Light Bottle Ocarina': [],
            "Link's House Entrance (E)": [],
            'Hyrule Castle': [],
            'Fairy Pond Under Rocks (LW) Entrance (E)': [('item', 'pegasus')],
            'Haunted Grove': [('item', 'shovel')],
            'Southern Chest Game Entrance (E)': [],
            'Kakariko': [],
            "Thieves' Town Surface": [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'Frog Prison': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'Library Entrance (E)': [],
            "Quarrelling Brothers' House East Entrance (E)": [],
            'Cave Near Haunted Grove Entrance (E)': [
                ('settings', 'inverted'),
                ('glitch', 'major'),
                ('and', [
                    ('glitch', 'overworld'), ('item', 'pegasus')])],
            'Southern Shores': [],
            'Lake Hylia Fortune Teller Entrance (E)': [],
            'Lake Hylia': [('item', 'flippers')],
            'Lake Hylia Shop Entrance (E)': [],
            'East Light World': [],
            'Small Lake Hylia Island': [
                ('glitch', 'major'),
                ('and', [
                    ('glitch', 'overworld'), ('item', 'pegasus')])]},
        'visible': {'Running Game': [], 'Small Lake Hylia Island': []}
    },
    "Link's House Entrance (E)": {
        'type': 'entrance_unique', 'map': 'light', 'coord': (363, 456),
        'link': {
            'South Light World': [],
            "Link's House Entrance (I)": [('nosettings', 'inverted')],
            'Bomb Shop Entrance (I)': [('settings', 'inverted')]}
    },
    "Link's House Entrance (I)": {
        'type': 'interior',
        'link': {
            "Link's House Entrance (E)": [('nosettings', 'inverted')],
            'Bomb Shop Entrance (E)': [('settings', 'inverted')],
            "Link's House": [('rabbitbarrier', None)]}
    },
    "Link's House": {
        'type': 'chest', 'map': 'light', 'coord': (363, 448),
        'link': {
            "Link's House Entrance (I)": [],
            'Ocarina': [('and', [
                ('item', 'ocarina'), ('access', 'Kakariko')])]}
    },
    'Fairy Pond Under Rocks (LW) Entrance (E)': {
        'type': 'entrance', 'map': 'light', 'coord': (313, 433),
        'link': {
            'South Light World': [],
            'Fairy Pond Under Rocks (LW) Entrance (I)': []}
    },
    'Fairy Pond Under Rocks (LW) Entrance (I)': {
        'type': 'interior',
        'link': {
            'Fairy Pond Under Rocks (LW) Entrance (E)': []}
    },
    'Haunted Grove': {
        'type': 'item', 'map': 'light', 'coord': (190, 438),
        'link': {
            'South Light World': []}
    },
    'Southern Chest Game Entrance (E)': {
        'type': 'entrance', 'map': 'light', 'coord': (143, 465),
        'link': {
            'South Light World': [],
            'Southern Chest Game Entrance (I)': []}
    },
    'Southern Chest Game Entrance (I)': {
        'type': 'interior',
        'link': {
            'Southern Chest Game Entrance (E)': []}
    },
    'Library Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (104, 436),
        'link': {
            'South Light World': [],
            'Library Entrance (I)': []}
    },
    'Library Entrance (I)': {
        'type': 'interior',
        'link': {
            'Library Entrance (E)': [],
            'Library': [('item', 'pegasus')]},
        'visible': {'Library': []}
    },
    'Library': {
        'type': 'chest', 'map': 'light', 'coord': (104, 432),
        'link': {
            'Library Entrance (I)': []}
    },
    "Quarrelling Brothers' House East Entrance (E)": {
        'type': 'entrance_unique', 'map': 'light', 'coord': (93, 476),
        'link': {
            'South Light World': [],
            "Quarrelling Brothers' House East Entrance (I)": []}
    },
    "Quarrelling Brothers' House East Entrance (I)": {
        'type': 'interior',
        'link': {
            "Quarrelling Brothers' House East Entrance (E)": [],
            "Quarrelling Brothers' House West Entrance (I)": [
                ('item', 'bombs')]}
    },
    "Quarrelling Brothers' House West Entrance (I)": {
        'type': 'interior',
        'link': {
            "Quarrelling Brothers' House East Entrance (I)": [
                ('item', 'bombs')],
            "Quarrelling Brothers' House West Entrance (E)": []}
    },
    "Quarrelling Brothers' House West Entrance (E)": {
        'type': 'entrance_unique', 'map': 'light', 'coord': (73, 476),
        'link': {
            "Quarrelling Brothers' House West Entrance (I)": [],
            'Running Game': [('rabbitbarrier', None)]}
    },
    'Running Game': {
        'type': 'item', 'map': 'light', 'coord': (22, 463),
        'link': {
            "Quarrelling Brothers' House West Entrance (E)": [],
            'South Light World': []},
    },
    'Cave Near Haunted Grove Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (177, 546),
        'link': {
            'South Light World': [],
            'Cave Near Haunted Grove Entrance (I)': []}
    },
    'Cave Near Haunted Grove Entrance (I)': {
        'type': 'interior',
        'link': {
            'Cave Near Haunted Grove Entrance (E)': [],
            'Cave Near Haunted Grove': [('rabbitbarrier', None)]}
    },
    'Cave Near Haunted Grove': {
        'type': 'cave', 'map': 'light', 'coord': (177, 546),
        'link': {
            'Cave Near Haunted Grove Entrance (I)': []}
    },
    'Lake Hylia Fortune Teller Entrance (E)': {
        'type': 'entrance', 'map': 'light', 'coord': (433, 530),
        'link': {
            'South Light World': [],
            'Lake Hylia Fortune Teller Entrance (I)': []}
    },
    'Lake Hylia Fortune Teller Entrance (I)': {
        'type': 'interior',
        'link': {
            'Lake Hylia Fortune Teller Entrance (E)': []}
    },
    'Lake Hylia Shop Entrance (E)': {
        'type': 'entrance_shop', 'map': 'light', 'coord': (482, 508),
        'link': {
            'South Light World': [],
            'Lake Hylia Shop Entrance (I)': []}
    },
    'Lake Hylia Shop Entrance (I)': {
        'type': 'interior',
        'link': {
            'Lake Hylia Shop Entrance (E)': []}
    },

    'Southern Shores': {
        'type': 'area',
        'link': {
            'South Dark World': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'Light Bottle Ocarina': [],
            'South Light World': [],
            'South Portal (LW)': [('item', 'hammer')],
            'Witch Hut Waterway': [('item', 'flippers')],
            'Locksmith': [('access', 'Locked Chest')],
            'Desert Fairy Entrance (E)': [],
            'Bombos Stone Mountain': [
                ('settings', 'inverted'),
                ('glitch', 'major'),
                ('and', [
                    ('glitch', 'overworld'), ('item', 'pegasus')])],
            'Desert': [],
            'Rich Thief Entrance (E)': [('item', 'powerglove')],
            'Item Under Water': [('access', 'Water Drain')],
            'Water Drain Entrance (E)': [],
            'South Fairy Entrance (E)': [('item', 'bombs')],
            'Moldorm Cave Entrance (E)': [('item', 'bombs')],
            'Lake Hylia': [
                ('item', 'flippers'),
                ('and', [('glitch', 'overworld'), ('rabbitbarrier', None)])],
            'Poor Thief Entrance (E)': [('item', 'powerglove')],
            'Ice Cave Main Entrance Entrance (E)': [],
            'Ice Cave Secret Entrance Entrance (E)': [('item', 'bombs')],
            'Eastern Shores': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])]}
    },
    'South Portal (LW)': {
        'type': 'area',
        'link': {
            'South Portal (DW)': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'Southern Shores': [('item', 'hammer')],
            'South Portal': [('item', 'powerglove')]},
    },
    'South Portal': {
        'type': 'area',
        'link': {
            'South Portal (LW)': [('and', [
                ('settings', 'inverted'), ('state', 'rabbit')])],
            'South Portal (DW)': [('and', [
                ('nosettings', 'inverted'), ('state', 'rabbit')])]}
    },
    'Witch Hut Waterway': {
        'type': 'area',
        'link': {
            'Southern Shores': [],
            'Witch Hut River': []}
    },
    'Locksmith': {
        'type': 'chest', 'map': 'light', 'coord': (224, 594),
        'link': {
            'Southern Shores': []}
    },
    'Desert Fairy Entrance (E)': {
        'type': 'entrance', 'map': 'light', 'coord': (184, 590),
        'link': {
            'Southern Shores': [],
            'Desert Fairy Entrance (I)': []}
    },
    'Desert Fairy Entrance (I)': {
        'type': 'interior',
        'link': {
            'Desert Fairy Entrance (E)': []}
    },
    'Bombos Stone Mountain': {
        'type': 'area',
        'link': {
            'Southern Shores': [],
            'Desert': [],
            'Bombos Stone': [('mudora', 'take')]},
        'visible': {'Bombos Stone': [('item', 'mudora')]}
    },
    'Bombos Stone': {
        'type': 'item', 'map': 'light', 'coord': (145, 610),
        'link': {
            'Bombos Stone Mountain': []}
    },
    'Rich Thief Entrance (E)': {
        'type': 'entrance', 'map': 'light', 'coord': (207, 634),
        'link': {
            'Southern Shores': [],
            'Rich Thief Entrance (I)': []}
    },
    'Rich Thief Entrance (I)': {
        'type': 'interior',
        'link': {
            'Rich Thief Entrance (E)': []}
    },
    'Item Under Water': {
        'type': 'item', 'map': 'light', 'coord': (296, 616),
        'link': {
            'Southern Shores': []}
    },
    'Water Drain Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (311, 620),
        'link': {
            'Southern Shores': [],
            'Water Drain Entrance (I)': []}
    },
    'Water Drain Entrance (I)': {
        'type': 'interior',
        'link': {
            'Water Drain Entrance (E)': [],
            'Water Drain': [('rabbitbarrier', None)]}
    },
    'Water Drain': {
        'type': 'chest', 'map': 'light', 'coord': (311, 616),
        'link': {
            'Water Drain Entrance (I)': []},
    },
    'South Fairy Entrance (E)': {
        'type': 'entrance', 'map': 'light', 'coord': (396, 517),
        'link': {
            'Southern Shores': [],
            'South Fairy Entrance (I)': []}
    },
    'South Fairy Entrance (I)': {
        'type': 'interior',
        'link': {
            'South Fairy Entrance (E)': []}
    },
    'Moldorm Cave Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (433, 621),
        'link': {
            'Southern Shores': [],
            'Moldorm Cave Entrance (I)': []}
    },
    'Moldorm Cave Entrance (I)': {
        'type': 'interior',
        'link': {
            'Moldorm Cave Entrance (E)': [],
            'Moldorm Cave': [('rabbitbarrier', None)]}
    },
    'Moldorm Cave': {
        'type': 'cave', 'map': 'light', 'coord': (433, 621),
        'link': {
            'Moldorm Cave Entrance (I)': []}
    },
    'Poor Thief Entrance (E)': {
        'type': 'entrance', 'map': 'light', 'coord': (599, 525),
        'link': {
            'Southern Shores': [],
            'Poor Thief Entrance (I)': []}
    },
    'Poor Thief Entrance (I)': {
        'type': 'interior',
        'link': {
            'Poor Thief Entrance (E)': []}
    },
    'Ice Cave Main Entrance Entrance (E)': {
        'type': 'entrance', 'map': 'light', 'coord': (607, 511),
        'link': {
            'Southern Shores': [],
            'Ice Cave Main Entrance Entrance (I)': []}
    },
    'Ice Cave Main Entrance Entrance (I)': {
        'type': 'interior',
        'link': {
            'Ice Cave Main Entrance Entrance (E)': []}
    },
    'Ice Cave Secret Entrance Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (593, 511),
        'link': {
            'Southern Shores': [],
            'Ice Cave Secret Entrance Entrance (I)': []}
    },
    'Ice Cave Secret Entrance Entrance (I)': {
        'type': 'interior',
        'link': {
            'Ice Cave Secret Entrance Entrance (E)': [],
            'Ice Cave': []}
    },
    'Ice Cave': {
        'type': 'cave', 'map': 'light', 'coord': (593, 511),
        'link': {
            'Ice Cave Secret Entrance Entrance (I)': []}
    },

    'Lake Hylia': {
        'type': 'area',
        'link': {
            'Frozen Lake': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'Southern Shores': [],
            'Crossworld Waterway': [],
            'Zora River Waterway': [],
            'Large Lake Hylia Island': [],
            'Small Lake Hylia Island': [('settings', 'inverted')],
            'South Light World': [],
            'East Light World': [],
            'Under The Bridge': []},
        'visible': {'Small Lake Hylia Island': []}
    },
    'Zora River Waterway': {
        'type': 'area',
        'link': {
            'Lake Hylia': [],
            'Waterfall Lake': []}
    },
    'Under The Bridge': {
        'type': 'item', 'map': 'light', 'coord': (469, 462),
        'link': {
            'Lake Hylia': []}
    },
    'Small Lake Hylia Island': {
        'type': 'item', 'map': 'light', 'coord': (483, 552),
        'link': {
            'Frozen Lake': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'Lake Hylia': [('item', 'flippers')]}
    },
    'Large Lake Hylia Island': {
        'type': 'area',
        'link': {
            'Ice Palace Exterior': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'Ice Palace Portal': [('item', 'titansmitts')],
            'Fairy Queen Cave Entrance (E)': []},
    },
    'Ice Palace Portal': {
        'type': 'area',
        'link': {
            'Ice Palace Exterior': [('and', [
                ('nosettings', 'inverted'), ('state', 'rabbit')])],
            'Large Lake Hylia Island': [('and', [
                ('settings', 'inverted'), ('state', 'rabbit')])]}
    },
    'Fairy Queen Cave Entrance (E)': {
        'type': 'entrance_shop', 'map': 'light', 'coord': (526, 564),
        'link': {
            'Large Lake Hylia Island': [],
            'Fairy Queen Cave Entrance (I)': []}
    },
    'Fairy Queen Cave Entrance (I)': {
        'type': 'interior',
        'link': {
            'Fairy Queen Cave Entrance (E)': []}
    },
}
