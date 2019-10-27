'''
Death Mountain
'''

__all__ = 'LOCATIONS',


LOCATIONS = {
    'West Lower Death Mountain': {
        'type': 'area',
        'link': {
            'West Lower Mount Hebra': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Heart Rock': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Dark Bottle Ocarina': [],
            'West Death Mountain Fairy Entrance (E)': [],
            'Cave of Byrna Entrance (E)': [],
            'Hebra Portal': [],
            'West Upper Death Mountain': [('settings', 'inverted')],
            'East Lower Death Mountain': [
                ('and', [
                    ('glitch', 'overworld'), ('item', 'pegasus'),
                    ('or', [
                        ('item', 'pearl'), ('item', 'hammer')])]),
                ('glitch', 'major')],
            'East Dark World': [('and', [
                ('glitch', 'overworld'),
                ('item', 'mirror'),
                ('item', 'pegasus'),
                ('or', [
                    ('item', 'sword'),
                    ('item', 'hookshot')])])]}
    },
    'West Death Mountain Fairy Entrance (E)': {
        'type': 'entrance', 'map': 'dark', 'coord': (264, 125),
        'link': {
            'West Lower Death Mountain': [],
            'West Death Mountain Fairy Entrance (I)': [
                ('nosettings', 'inverted')],
            'Hebra Ascent (Top) Entrance (I)': [('settings', 'inverted')]}
    },
    'West Death Mountain Fairy Entrance (I)': {
        'type': 'interior',
        'link': {
            'West Death Mountain Fairy Entrance (E)': [
                ('nosettings', 'inverted')],
            'Hebra Ascent (Top) Entrance (E)': [('settings', 'inverted')]}
    },
    'Cave of Byrna Entrance (E)': {
        'type': 'entrance_unique', 'map': 'dark', 'coord': (375, 96),
        'link': {
            'West Lower Death Mountain': [],
            'Cave of Byrna Entrance (I)': []}
    },
    'Cave of Byrna Entrance (I)': {
        'type': 'interior',
        'link': {
            'Cave of Byrna Entrance (E)': [],
            'Cave of Byrna': [('and', [
                ('item', 'hammer'),
                ('or', [
                    ('and', [
                        ('item', 'cape'), ('or', [
                            ('item', 'halfmagic'), ('item', 'bottle')])]),
                    ('item', 'byrna')]),
                ('item', 'powerglove')])]}
    },
    'Cave of Byrna': {
        'type': 'cave', 'map': 'dark', 'coord': (375, 96),
        'link': {
            'Cave of Byrna Entrance (I)': [('and', [
                ('item', 'hammer'),
                ('or', [
                    ('and', [
                        ('item', 'cape'), ('or', [
                            ('item', 'halfmagic'), ('item', 'bottle')])]),
                    ('item', 'byrna')]),
                ('item', 'powerglove')])]}
    },

    'West Upper Death Mountain': {
        'type': 'area',
        'link': {
            'West Upper Mount Hebra': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'West Lower Death Mountain': [],
            "Ganon's Tower Entrance (E)": [
                ('and', [
                    ('nosettings', 'inverted'), ('macro', 'ganonstower')]),
                ('settings', 'inverted')],
            'East Upper Death Mountain': []}
    },
    "Ganon's Tower Entrance (E)": {
        'type': 'entrance_dungeon', 'map': 'dark', 'coord': (367, 35),
        'link': {
            'West Upper Death Mountain': [],
            "Ganon's Tower Entrance (I)": [('nosettings', 'inverted')],
            'Castle Tower Entrance (I)': [('settings', 'inverted')]}
    },

    'East Lower Death Mountain': {
        'type': 'area',
        'link': {
            'East Lower Mount Hebra': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Death Mountain Shop Entrance (E)': [],
            'Death Mountain Cave Bottom Entrance Entrance (E)': [],
            'East Hebra Portal': [('item', 'titansmitts')]}
    },
    'Death Mountain Shop Entrance (E)': {
        'type': 'entrance_shop', 'map': 'dark', 'coord': (571, 96),
        'link': {
            'East Lower Death Mountain': [],
            'Death Mountain Shop Entrance (I)': []}
    },
    'Death Mountain Shop Entrance (I)': {
        'type': 'interior',
        'link': {
            'Death Mountain Shop Entrance (E)': []}
    },
    'Death Mountain Cave Bottom Entrance Entrance (E)': {
        'type': 'entrance_unique', 'map': 'dark', 'coord': (557, 96),
        'link': {
            'East Lower Death Mountain': [],
            'Death Mountain Cave Bottom Entrance Entrance (I)': []}
    },
    'Death Mountain Cave Bottom Entrance Entrance (I)': {
        'type': 'interior',
        'link': {
            'Death Mountain Cave Bottom Entrance Entrance (E)': [],
            'Death Mountain Cave': [('rabbitbarrier', None)],
            'Death Mountain Cave Top Entrance Entrance (I)': []}
    },
    'Death Mountain Cave': {
        'type': 'cave', 'map': 'dark', 'coord': (557, 96),
        'link': {
            'Death Mountain Cave Top Entrance Entrance (I)': []}
    },
    'Death Mountain Cave Top Entrance Entrance (I)': {
        'type': 'interior',
        'link': {
            'Death Mountain Cave': [('rabbitbarrier', None)],
            'Death Mountain Cave Top Entrance Entrance (E)': []}
    },
    'Death Mountain Cave Top Entrance Entrance (E)': {
        'type': 'entrance_unique', 'map': 'dark', 'coord': (564, 41),
        'link': {
            'Death Mountain Cave Top Entrance Entrance (I)': [],
            'East Upper Death Mountain': []}
    },

    'East Upper Death Mountain': {
        'type': 'area',
        'link': {
            'East Upper Mount Hebra': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Dark Bottle Ocarina': [],
            'West Upper Death Mountain': [],
            'East Lower Death Mountain': [],
            'Death Mountain Cave Top Entrance Entrance (E)': [],
            'Pit Cave Entrance (E)': [('item', 'powerglove')],
            'Turtle Rock Portal (DW)': [('settings', 'inverted')],
            'Turtle Rock Entrance Entrance (E)': [
                ('access', 'Open Turtle Rock')],
            'Pit Cave Peak': [('and', [
                ('glitch', 'overworld'), ('item', 'pegasus')])],
            'Turtle Rock Balcony': [
                ('and', [
                    ('glitch', 'overworld'),
                    ('or', [
                        ('item', 'mirror'), ('item', 'pegasus')])])],
            'Turtle Rock Fairy Exit': [
                ('and', [
                    ('glitch', 'overworld'),
                    ('or', [
                        ('item', 'mirror'), ('item', 'pegasus')])]),
                ('glitch', 'major')]}
    },
    'Pit Cave Entrance (E)': {
        'type': 'entrance_unique', 'map': 'dark', 'coord': (546, 44),
        'link': {
            'East Upper Death Mountain': [],
            'Pit Cave Entrance (I)': []}
    },
    'Pit Cave Entrance (I)': {
        'type': 'interior',
        'link': {
            'Pit Cave Entrance (E)': [],
            'Pit Cave': []}
    },
    'Pit Cave': {
        'type': 'area',
        'link': {
            'Pit Cave Entrance (I)': [],
            'Pit Cave Pegasus Chest': [
                ('and', [
                    ('item', 'pegasus'), ('settings', 'placement_advanced')]),
                ('item', 'hookshot')],
            'Pit Cave Hookshot Chests': [('item', 'hookshot')],
            'Pit Cave Back Exit Entrance (I)': [('item', 'bombs')]}
    },
    'Pit Cave Pegasus Chest': {
        'type': 'drop', 'map': 'dark', 'coord': (546, 51),
        'link': {
            'Pit Cave': []}
    },
    'Pit Cave Hookshot Chests': {
        'type': 'drop', 'map': 'dark', 'coord': (546, 37),
        'link': {
            'Pit Cave': []}
    },
    'Pit Cave Back Exit Entrance (I)': {
        'type': 'interior',
        'link': {
            'Pit Cave': [('item', 'bombs')],
            'Pit Cave Back Exit Entrance (E)': []}
    },
    'Pit Cave Back Exit Entrance (E)': {
        'type': 'entrance_unique', 'map': 'dark', 'coord': (524, 10),
        'link': {
            'Pit Cave Back Exit Entrance (I)': [],
            'Pit Cave Peak': []}
    },
    'Pit Cave Peak': {
        'type': 'area',
        'link': {
            'Heart Peak': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Pit Cave Back Exit Entrance (E)': [],
            'East Upper Death Mountain': []}
    },
    'Turtle Rock Portal (DW)': {
        'type': 'area',
        'link': {
            'Turtle Rock Portal (LW)': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'East Upper Death Mountain': [],
            'Turtle Rock Portal': [('item', 'titansmitts')],
            'Open Turtle Rock': [('medallion', 'Turtle Rock')]}
    },
    'Open Turtle Rock': {
        'type': 'area',
        'link': {
            'Turtle Rock Portal (DW)': []}
    },
}
