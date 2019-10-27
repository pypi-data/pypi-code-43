'''
Northern Light World
'''

__all__ = 'LOCATIONS',


LOCATIONS= {
    'Lost Woods': {
        'type': 'area',
        'link': {
            'Skull Woods': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'Hidden Skull Woods': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'Light Bottle Ocarina': [],
            'Kakariko': [('rabbitbarrier', None)],
            'Kakariko Portal (LW)': [('item', 'hammer')],
            'North Light World': [],
            'Master Sword Pedestal': [('and', [
                ('pendant', 'courage'),
                ('pendant', 'power'),
                ('pendant', 'wisdom'),
                ('or', [
                    ('settings', 'placement_advanced'), ('item', 'mudora')])])],
            'Mushroom': [('rabbitbarrier', None)],
            "Thief's Cave Drop Entrance (E)": [('rabbitbarrier', None)],
            "Thief's Cave Entrance Entrance (E)": [],
            'Northern Chest Game Entrance (E)': []},
        'visible': {
            'Master Sword Pedestal': [('item', 'mudora')]}
    },
    'Master Sword Pedestal': {
        'type': 'item', 'map': 'light', 'coord': (27, 33),
        'link': {
            'Lost Woods': []}
    },
    'Mushroom': {
        'type': 'item', 'map': 'light', 'coord': (79, 57),
        'link': {
            'Lost Woods': [('rabbitbarrier', None)]}
    },
    "Thief's Cave Drop Entrance (E)": {
        'type': 'entrance_drop', 'map': 'light', 'coord': (125, 84),
        'link': {
            "Thief's Cave Drop Entrance (I)": []}
    },
    "Thief's Cave Drop Entrance (I)": {
        'type': 'interior',
        'link': {
            "Thief's Cave": []}
    },
    "Thief's Cave": {
        'type': 'drop', 'map': 'light', 'coord': (125, 87),
        'link': {
            "Thief's Cave Entrance": []}
    },
    "Thief's Cave Entrance": {
        'type': 'area',
        'link': {
            "Thief's Cave Entrance Entrance (I)": []},
        'visible': {"Thief's Cave": []}
    },
    "Thief's Cave Entrance Entrance (I)": {
        'type': 'interior',
        'link': {
            "Thief's Cave Entrance": [],
            "Thief's Cave Entrance Entrance (I)": []}
    },
    "Thief's Cave Entrance Entrance (E)": {
        'type': 'entrance_unique', 'map': 'light', 'coord': (122, 99),
        'link': {
            "Thief's Cave Entrance": [],
            'Lost Woods': []}
    },
    'Northern Chest Game Entrance (E)': {
        'type': 'entrance', 'map': 'light', 'coord': (123, 10),
        'link': {
            'Lost Woods': [],
            'Northern Chest Game Entrance (I)': []}
    },
    'Northern Chest Game Entrance (I)': {
        'type': 'interior',
        'link': {
            'Northern Chest Game Entrance (E)': []}
    },


    'North Light World': {
        'type': 'area',
        'link': {
            'North Dark World': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'Kakariko': [],
            'Lost Woods': [],
            'Kakariko Fortune Teller Entrance (E)': [],
            'Hyrule Castle': [],
            'Crossworld Waterway': [('item', 'flippers')],
            "Lumberjacks' House Entrance (E)": [],
            'Cut Tree Drop Entrance (E)': [('and', [
                ('access', 'Castle Tower Reward'), ('item', 'pegasus')])],
            'Cut Tree Cave Entrance (E)': [],
            'Hebra Ascent (Bottom) Entrance (E)': [('item', 'powerglove')],
            'Pegasus Cave Entrance (E)': [('item', 'pegasus')],
            'Sanctuary Entrance Entrance (E)': [],
            'Sanctuary Drop Entrance (E)': [('item', 'powerglove')],
            'Graveyard Cave Entrance': [
                ('settings', 'inverted'),
                ('and', [
                    ('glitch', 'overworld'), ('item', 'pegasus')])],
            "King's Tomb Entrance (E)": [('and', [
                ('item', 'titansmitts'), ('item', 'pegasus')])],
            'North Fairy Pond Drop Entrance (E)': [('rabbitbarrier', None)],
            'North Fairy Pond Cave Entrance (E)': [],
            'Witch Hut River': [('item', 'flippers')],
            'Little River': [('item', 'flippers')],
            'East Light World': [],
            'West Lower Mount Hebra': [
                ('glitch', 'major'),
                ('and', [
                    ('glitch', 'overworld'), ('item', 'pegasus')])]}
    },
    'Kakariko Fortune Teller Entrance (E)': {
        'type': 'entrance', 'map': 'light', 'coord': (125, 214),
        'link': {
            'North Light World': [],
            'Kakariko Fortune Teller Entrance (I)': []}
    },
    'Kakariko Fortune Teller Entrance (I)': {
        'type': 'interior',
        'link': {
            'Kakariko Fortune Teller Entrance (E)': []}
    },
    'Crossworld Waterway': {
        'type': 'area',
        'link': {
            'Lake Hylia': [],
            'North Light World': []}
    },
    "Lumberjacks' House Entrance (E)": {
        'type': 'entrance', 'map': 'light', 'coord': (223, 40),
        'link': {
            'North Light World': [],
            "Lumberjacks' House Entrance (I)": []}
    },
    "Lumberjacks' House Entrance (I)": {
        'type': 'interior',
        'link': {
            "Lumberjacks' House Entrance (E)": []}
    },
    'Cut Tree Drop Entrance (E)': {
        'type': 'entrance_drop', 'map': 'light', 'coord': (200, 49),
        'link': {
            'Cut Tree Drop Entrance (I)': []}
    },
    'Cut Tree Drop Entrance (I)': {
        'type': 'interior',
        'link': {
            'Cut Tree': []}
    },
    'Cut Tree': {
        'type': 'drop', 'map': 'light', 'coord': (200, 49),
        'link': {
            'Cut Tree Viewpoint': []}
    },
    'Cut Tree Cave Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (220, 21),
        'link': {
            'North Light World': [],
            'Cut Tree Cave Entrance (I)': []}
    },
    'Cut Tree Cave Entrance (I)': {
        'type': 'interior',
        'link': {
            'Cut Tree Cave Entrance (E)': [],
            'Cut Tree Viewpoint': []}
    },
    'Cut Tree Viewpoint': {
        'type': 'area',
        'link': {
            'Cut Tree Cave Entrance (I)': []},
        'visible': {'Cut Tree': []}
    },
    'Hebra Ascent (Bottom) Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (236, 116),
        'link': {
            'North Light World': [],
            'Hebra Ascent (Bottom) Entrance (I)': [('nosettings', 'inverted')],
            'Bumper Cave Bottom Entrance Entrance (I)': [
                ('settings', 'inverted')]}
    },
    'Hebra Ascent (Bottom) Entrance (I)': {
        'type': 'interior',
        'link': {
            'Hebra Ascent (Bottom) Entrance (E)': [('nosettings', 'inverted')],
            'Bumper Cave Bottom Entrance Entrance (E)': [
                ('settings', 'inverted')],
            'Hebra Ascent': []}
    },
    'Hebra Descent (Bottom) Entrance (I)': {
        'type': 'interior',
        'link': {
            'Hebra Descent': [],
            'Hebra Descent (Bottom) Entrance (E)': [('nosettings', 'inverted')],
            'Bumper Cave Bottom Entrance Entrance (E)': [
                ('settings', 'inverted')]}
    },
    'Hebra Descent (Bottom) Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (238, 101),
        'link': {
            'Hebra Descent (Bottom) Entrance (I)': [('nosettings', 'inverted')],
            'Bumper Cave Top Entrance Entrance (I)': [
                ('settings', 'inverted')],
            'Hebra Descent End': []}
    },
    'Hebra Descent End': {
        'type': 'area',
        'link': {
            'Bumper Cave Top': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'Hebra Descent (Bottom) Entrance (E)': [],
            'North Light World': []}
    },
    'Pegasus Cave Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (259, 194),
        'link': {
            'North Light World': [],
            'Pegasus Cave Entrance (I)': []}
    },
    'Pegasus Cave Entrance (I)': {
        'type': 'interior',
        'link': {
            'Pegasus Cave Entrance (E)': [],
            'Pegasus Cave': []}
    },
    'Pegasus Cave': {
        'type': 'drop', 'map': 'light', 'coord': (259, 194),
        'link': {
            'Pegasus Cave Entrance (I)': []}
    },
    'Sanctuary Entrance Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (306, 176),
        'link': {
            'North Light World': [],
            'Sanctuary Entrance Entrance (I)': []}
    },
    'Sanctuary Entrance Entrance (I)': {
        'type': 'interior',
        'link': {
            'Sanctuary Entrance Entrance (E)': [],
            'Sanctuary': [('rabbitbarrier', None)]}
    },
    'Sanctuary Drop Entrance (E)': {
        'type': 'entrance_drop', 'map': 'light', 'coord': (345, 194),
        'link': {
            'Sanctuary Drop Entrance (I)': []}
    },
    'Sanctuary Drop Entrance (I)': {
        'type': 'interior',
        'link': {
            'Sewers Last Hall': []}
    },
    'Graveyard Cave Entrance': {
        'type': 'area',
        'link': {
            'North Light World': [],
            'Graveyard Cave Entrance (E)': []}
    },
    'Graveyard Cave Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (378, 181),
        'link': {
            'Graveyard Cave Entrance': [],
            'Graveyard Cave Entrance (I)': []}
    },
    'Graveyard Cave Entrance (I)': {
        'type': 'interior',
        'link': {
            'Graveyard Cave Entrance (E)': [],
            'Graveyard Cave Front': []}
    },
    'Graveyard Cave Front': {
        'type': 'area',
        'link': {
            'Graveyard Cave Entrance (I)': [],
            'Graveyard Cave': [('item', 'bombs')]}
    },
    'Graveyard Cave': {
        'type': 'cave', 'map': 'light', 'coord': (378, 181),
        'link': {
            'Graveyard Cave Front': []}
    },
    "King's Tomb Entrance (E)": {
        'type': 'entrance_unique', 'map': 'light', 'coord': (399, 197),
        'link': {
            'North Light World': [('item', 'titansmitts')],
            "King's Tomb Entrance (I)": []}
    },
    "King's Tomb Entrance (I)": {
        'type': 'interior',
        'link': {
            "King's Tomb Entrance (E)": [],
            "King's Tomb": []}
    },
    "King's Tomb": {
        'type': 'drop', 'map': 'light', 'coord': (399, 197),
        'link': {
            "King's Tomb Entrance (I)": []}
    },
    'North Fairy Pond Drop Entrance (E)': {
        'type': 'entrance_drop', 'map': 'light', 'coord': (426, 206),
        'link': {
            'North Fairy Pond Drop Entrance (I)': []}
    },
    'North Fairy Pond Drop Entrance (I)': {
        'type': 'interior',
        'link': {
            'North Fairy Pond': []}
    },
    'North Fairy Pond': {
        'type': 'area',
        'link': {
            'North Fairy Pond Cave': []}
    },
    'North Fairy Pond Cave Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (443, 181),
        'link': {
            'North Light World': [],
            'North Fairy Pond Cave Entrance (I)': []}
    },
    'North Fairy Pond Cave Entrance (I)': {
        'type': 'interior',
        'link': {
            'North Fairy Pond Cave Entrance (E)': [],
            'North Fairy Pond Cave': []}
    },
    'North Fairy Pond Cave': {
        'type': 'area',
        'link': {
            'North Fairy Pond Cave Entrance (I)': []}
    },
    'Little River': {
        'type': 'area',
        'link': {
            'Dark River': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'North Light World': []}
    },
}
