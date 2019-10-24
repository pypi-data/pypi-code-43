'''
Mount Hebra
'''

__all__ = 'LOCATIONS',


LOCATIONS = {
    'Hebra Ascent': {
        'type': 'area',
        'link': {
            'Hebra Ascent (Bottom) Entrance (I)': [('item', 'lantern')],
            'Finding The Lost Man': [('item', 'lantern')],
            'Hebra Ascent (Top) Entrance (I)': [('item', 'lantern')]}
    },
    'Finding The Lost Man': {
        'type': 'area',
        'link': {
            'Hebra Ascent': []}
    },
    'Hebra Ascent (Top) Entrance (I)': {
        'type': 'interior',
        'link': {
            'Hebra Ascent': [],
            'Hebra Ascent (Top) Entrance (E)': [('nosettings', 'inverted')],
            'West Death Mountain Fairy Entrance (E)': [
                ('settings', 'inverted')]}
    },
    'Hebra Ascent (Top) Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (269, 125),
        'link': {
            'Hebra Ascent (Top) Entrance (I)': [('nosettings', 'inverted')],
            'West Death Mountain Fairy Entrance (I)': [
                ('settings', 'inverted')],
            'West Lower Mount Hebra': []}
    },
    'West Lower Mount Hebra': {
        'type': 'area',
        'link': {
            'West Lower Death Mountain': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'Light Bottle Ocarina': [],
            'Hebra Ascent (Top) Entrance (E)': [],
            "Lost Man's Cave Front Entrance Entrance (E)": [],
            "Lost Man's Cave Back Entrance Entrance (E)": [],
            'East Lower Mount Hebra': [
                ('item', 'hookshot'),
                ('glitch', 'major'),
                ('and', [
                    ('glitch', 'overworld'),
                    ('or', [
                        ('item', 'mirror'), ('item', 'pegasus')])])],
            'Hebra Descent (Top) Entrance (E)': [],
            'Heart Rock Cave Top Entrance Entrance (E)': [],
            'West Hebra Fairy Cave Entrance (E)': [],
            'Heart Rock Cave Bottom Entrance Entrance (E)': [],
            'Hebra Portal': [],
            'Pyramid Fairy Entrance (E)': [('and', [
                ('glitch', 'overworld'), ('item', 'mirror'),
                ('item', 'pegasus'),
                ('or', [
                    ('item', 'sword'), ('item', 'hookshot')])])],
            'Heart Rock': [
                ('and', [
                    ('glitch', 'overworld'), ('item', 'pegasus')]),
                ('glitch', 'major')],
            "King's Tomb Entrance (E)": [('and', [
                ('glitch', 'overworld'), ('item', 'pegasus')])]},
        'visible': {'Heart Rock': []}
    },
    "Lost Man's Cave Front Entrance Entrance (E)": {
        'type': 'entrance_unique', 'map': 'light', 'coord': (298, 155),
        'link': {
            'West Lower Mount Hebra': [],
            "Lost Man's Cave Front Entrance Entrance (I)": []}
    },
    "Lost Man's Cave Front Entrance Entrance (I)": {
        'type': 'interior',
        'link': {
            "Lost Man's Cave Front Entrance Entrance (E)": [],
            "Lost Man's Cave Front": []}
    },
    "Lost Man's Cave Front": {
        'type': 'area',
        'link': {
            "Lost Man's Cave Front Entrance Entrance (I)": [],
            'Lost Man': [('access', 'Finding The Lost Man')],
            "Lost Man's Cave Back": [('item', 'lantern')]}
    },
    'Lost Man': {
        'type': 'chest', 'map': 'light', 'coord': (298, 150),
        'link': {
            "Lost Man's Cave Front": []}
    },
    "Lost Man's Cave Back": {
        'type': 'area',
        'link': {
            "Lost Man's Cave Front": [],
            "Lost Man's Cave Back Entrance Entrance (I)": []}
    },
    "Lost Man's Cave Back Entrance Entrance (I)": {
        'type': 'interior',
        'link': {
            "Lost Man's Cave Front": [('item', 'lantern')],
            "Lost Man's Cave Back Entrance Entrance (E)": []}
    },
    "Lost Man's Cave Back Entrance Entrance (E)": {
        'type': 'entrance_unique', 'map': 'light', 'coord': (355, 106),
        'link': {
            "Lost Man's Cave Back Entrance Entrance (I)": [],
            'West Lower Mount Hebra': []}
    },
    'Hebra Descent (Top) Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (262, 91),
        'link': {
            'West Lower Mount Hebra': [],
            'Hebra Descent (Top) Entrance (I)': []}
    },
    'Hebra Descent (Top) Entrance (I)': {
        'type': 'interior',
        'link': {
            'Hebra Descent (Top) Entrance (E)': [],
            'Hebra Descent': []}
    },
    'Hebra Descent': {
        'type': 'area',
        'link': {
            'Hebra Descent (Bottom) Entrance (I)': [],
            'Hebra Descent (Top) Entrance (I)': []}
    },
    'Heart Rock Cave Top Entrance Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (324, 68),
        'link': {
            'West Lower Mount Hebra': [],
            'Heart Rock Cave Top Entrance Entrance (I)': []}
    },
    'Heart Rock Cave Top Entrance Entrance (I)': {
        'type': 'interior',
        'link': {
            'Heart Rock Cave Top Entrance Entrance (E)': [],
            'Heart Rock Cave Top': []}
    },
    'Heart Rock Cave Top': {
        'type': 'area',
        'link': {
            'Heart Rock Cave Top Entrance Entrance (I)': [],
            'West Hebra Fairy Cave': []}
    },
    'West Hebra Fairy Cave Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (302, 91),
        'link': {
            'West Lower Mount Hebra': [],
            'West Hebra Fairy Cave Entrance (I)': []}
    },
    'West Hebra Fairy Cave Entrance (I)': {
        'type': 'interior',
        'link': {
            'West Hebra Fairy Cave Entrance (E)': [],
            'West Hebra Fairy Cave': []}
    },
    'West Hebra Fairy Cave': {
        'type': 'area',
        'link': {
            'West Hebra Fairy Cave Entrance (I)': []}
    },
    'Heart Rock Cave Bottom Entrance Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (324, 96),
        'link': {
            'West Lower Mount Hebra': [],
            'Heart Rock Cave Bottom Entrance Entrance (I)': []}
    },
    'Heart Rock Cave Bottom Entrance Entrance (I)': {
        'type': 'interior',
        'link': {
            'Heart Rock Cave Bottom Entrance Entrance (E)': [],
            'Heart Rock Cave Bottom': []}
    },
    'Heart Rock Cave Bottom': {
        'type': 'area',
        'link': {
            'Heart Rock Cave Bottom Entrance Entrance (E)': [],
            'Heart Rock Cave Heart': [],
            'West Hebra Fairy Cave': []}
    },
    'Heart Rock Cave Heart': {
        'type': 'cave', 'map': 'light', 'coord': (324, 88),
        'link': {
            'Heart Rock Cave Bottom': []}
    },
    'Hebra Portal': {
        'type': 'area',
        'link': {
            'West Lower Death Mountain': [('and', [
                ('nosettings', 'inverted'), ('state', 'rabbit')])],
            'West Lower Mount Hebra': [('and', [
                ('settings', 'inverted'), ('state', 'rabbit')])]}
    },

    'Heart Rock': {
        'type': 'item', 'map': 'light', 'coord': (337, 55),
        'link': {
            'West Lower Death Mountain': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'West Lower Mount Hebra': [],
            'West Upper Mount Hebra': []}
    },
    'West Upper Mount Hebra': {
        'type': 'area',
        'link': {
            'West Upper Death Mountain': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'West Lower Mount Hebra': [],
            'Heart Rock': [('settings', 'inverted')],
            'Ether Rock': [('mudora', 'take')],
            'Mountain Tower Entrance (E)': [],
            'East Upper Mount Hebra': [('item', 'hammer')]},
        'visible': {'Heart Rock': [], 'Ether Rock': [('item', 'mudora')]}
    },
    'Ether Rock': {
        'type': 'item', 'map': 'light', 'coord': (278, 13),
        'link': {
            'West Upper Mount Hebra': []}
    },

    'East Lower Mount Hebra': {
        'type': 'area',
        'link': {
            'West Lower Death Mountain': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'West Lower Mount Hebra': [('item', 'hookshot')],
            'Spiral Cave Bottom Entrance Entrance (E)': [],
            'Fairy Maze Bottom Entrance Entrance (E)': [
                ('item', 'titansmitts')],
            'East Hebra Fairy Cave Entrance Entrance (E)': [],
            'Hebra Shop Cave Entrance (E)': [],
            'East Hebra Portal': [('item', 'titansmitts')],
            'East Hebra Cave Bottom Entrance Entrance (E)': []}
    },
    'Spiral Cave Bottom Entrance Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (530, 86),
        'link': {
            'East Lower Mount Hebra': [],
            'Spiral Cave Bottom Entrance Entrance (I)': []}
    },
    'Spiral Cave Bottom Entrance Entrance (I)': {
        'type': 'interior',
        'link': {
            'Spiral Cave Bottom Entrance Entrance (E)': [],
            'Spiral Cave Bottom': []}
    },
    'Spiral Cave Bottom': {
        'type': 'area',
        'link': {
            'Spiral Cave Bottom Entrance Entrance (I)': []}
    },
    'Fairy Maze Bottom Entrance Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (544, 91),
        'link': {
            'East Lower Mount Hebra': [],
            'Fairy Maze Bottom Entrance Entrance (I)': []}
    },
    'Fairy Maze Bottom Entrance Entrance (I)': {
        'type': 'interior',
        'link': {
            'Fairy Maze Bottom Entrance Entrance (E)': [],
            'Fairy Maze Top Entrance Entrance (I)': []}
    },
    'East Hebra Fairy Cave Entrance Entrance (E)': {
        'type': 'entrance', 'map': 'light', 'coord': (558, 96),
        'link': {
            'East Lower Mount Hebra': [],
            'East Hebra Fairy Cave Entrance Entrance (I)': []}
    },
    'East Hebra Fairy Cave Entrance Entrance (I)': {
        'type': 'interior',
        'link': {
            'East Hebra Fairy Cave Entrance Entrance (E)': []}
    },
    'Hebra Shop Cave Entrance (E)': {
        'type': 'entrance_shop', 'map': 'light', 'coord': (572, 96),
        'link': {
            'East Lower Mount Hebra': [],
            'Hebra Shop Cave Entrance (I)': []}
    },
    'Hebra Shop Cave Entrance (I)': {
        'type': 'interior',
        'link': {
            'Hebra Shop Cave Entrance (E)': [],
            'Hebra Shop Cave': []}
    },
    'Hebra Shop Cave': {
        'type': 'area',
        'link': {
            'Hebra Shop Cave Entrance (I)': []}
    },
    'East Hebra Portal': {
        'type': 'area',
        'link': {
            'East Lower Death Mountain': [('and', [
                ('nosettings', 'inverted'), ('state', 'rabbit')])],
            'East Lower Mount Hebra': [('and', [
                ('settings', 'inverted'), ('state', 'rabbit')])]}
    },
    'East Hebra Cave Bottom Entrance Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (573, 142),
        'link': {
            'East Lower Mount Hebra': [],
            'East Hebra Cave Bottom Entrance Entrance (I)': []}
    },
    'East Hebra Cave Bottom Entrance Entrance (I)': {
        'type': 'interior',
        'link': {
            'East Hebra Cave Bottom Entrance Entrance (E)': [],
            'East Hebra Cave (area)': []}
    },
    'East Hebra Cave (area)': {
        'type': 'area',
        'link': {
            'East Hebra Cave Bottom Entrance Entrance (I)': [],
            'Hebra Shop Cave': [('rabbitbarrier', None)],
            'East Hebra Cave': [('item', 'bombs')],
            'East Hebra Cave Top Entrance Entrance (I)': []}
    },
    'East Hebra Cave': {
        'type': 'cave', 'map': 'light', 'coord': (573, 142),
        'link': {
            'Hebra Shop Cave': []}
    },
    'East Hebra Cave Top Entrance Entrance (I)': {
        'type': 'interior',
        'link': {
            'East Hebra Cave (area)': [],
            'East Hebra Cave Top Entrance Entrance (E)': []}
    },
    'East Hebra Cave Top Entrance Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (569, 41),
        'link': {
            'East Hebra Cave (area)': [],
            'East Upper Mount Hebra': []}
    },

    'East Upper Mount Hebra': {
        'type': 'area',
        'link': {
            'East Upper Death Mountain': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'Turtle Rock Balcony': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'Turtle Rock Fairy Exit': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'Light Bottle Ocarina': [],
            'West Upper Mount Hebra': [('item', 'hammer')],
            'East Lower Mount Hebra': [],
            'Spiral Cave Top Entrance Entrance (E)': [],
            'Fairy Maze Top Entrance Entrance (E)': [],
            'Goriya Cave Entrance (E)': [('settings', 'inverted')],
            'East Hebra Cave Top Entrance Entrance (E)': [],
            'Heart Peak': [
                ('settings', 'inverted'),
                ('and', [
                    ('glitch', 'overworld'), ('item', 'mirror')])],
            'Turtle Rock Portal (LW)': [('item', 'titansmitts')]},
        'visible': {'Heart Peak': []}
    },
    'Spiral Cave Top Entrance Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (529, 59),
        'link': {
            'East Lower Mount Hebra': [],
            'Spiral Cave Top Entrance Entrance (I)': []}
    },
    'Spiral Cave Top Entrance Entrance (I)': {
        'type': 'interior',
        'link': {
            'Spiral Cave Top Entrance Entrance (E)': [],
            'Spiral Cave Top': []}
    },
    'Spiral Cave Top': {
        'type': 'area',
        'link': {
            'Spiral Cave Top Entrance Entrance (I)': [],
            'Spiral Cave': [('rabbitbarrier', None)]}
    },
    'Spiral Cave': {
        'type': 'cave', 'map': 'light', 'coord': (529, 59),
        'link': {
            'Spiral Cave Bottom': []}
    },
    'Fairy Maze Top Entrance Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (544, 75),
        'link': {
            'East Lower Mount Hebra': [],
            'Fairy Maze Top Entrance Entrance (I)': [],
            'Fairy Maze Bottom Entrance Entrance (E)': []}
    },
    'Fairy Maze Top Entrance Entrance (I)': {
        'type': 'interior',
        'link': {
            'Fairy Maze Top Entrance Entrance (E)': [],
            'Fairy Maze Bottom Entrance Entrance (I)': []}
    },
    'Goriya Cave Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (559, 59),
        'link': {
            'East Lower Mount Hebra': [],
            'Goriya Cave Entrance (I)': []}
    },
    'Goriya Cave Entrance (I)': {
        'type': 'interior',
        'link': {
            'Goriya Cave Entrance (E)': [],
            'Goriya Cave': [('item', 'hammer')]}
    },
    'Goriya Cave': {
        'type': 'cave', 'map': 'light', 'coord': (559, 59),
        'link': {
            'Goriya Cave Entrance (I)': [('item', 'hammer')]}
    },
    'Heart Peak': {
        'type': 'item', 'map': 'light', 'coord': (539, 14),
        'link': {
            'Pit Cave Peak': [
                ('nosettings', 'inverted'),
                ('item', 'mirror')],
            'East Upper Mount Hebra': [('settings', 'inverted')]}
    },
    'Turtle Rock Portal (LW)': {
        'type': 'area',
        'link': {
            'Turtle Rock Portal (DW)': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'East Upper Mount Hebra': [
                ('nosettings', 'inverted'), ('item', 'hammer')],
            'Turtle Rock Portal': [('item', 'hammer')]}
    },
    'Turtle Rock Portal': {
        'type': 'area',
        'link': {
            'Turtle Rock Portal (DW)': [('and', [
                ('nosettings', 'inverted'), ('state', 'rabbit')])],
            'Turtle Rock Portal (LW)': [('and', [
                ('settings', 'inverted'), ('state', 'rabbit')])]}
    },
}
