'''
Northern Dark World
'''

__all__ = 'LOCATIONS',


LOCATIONS = {
    'North Dark World': {
        'type': 'area',
        'link': {
            'North Light World': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Graveyard Cave Entrance (E)': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            "Thieves' Town Surface": [],
            'Skull Woods Surface': [],
            "Thieves' Town Fortune Teller Entrance (E)": [],
            'South Specialty Shop Entrance (E)': [],
            'Bumper Cave Bottom Entrance Entrance (E)': [
                ('item', 'powerglove')],
            'Bumper Cave Top': [
                ('glitch', 'major'),
                ('and', [
                    ('glitch', 'overworld'), ('item', 'pegasus')])],
            'North Specialty Shop Entrance (E)': [],
            'Dark Chapel Entrance (E)': [],
            'Dark River': [
                ('item', 'flippers'),
                ('and', [
                    ('glitch', 'overworld'), ('item', 'pegasus')])]},
        'visible': {'Bumper Cave': []}
    },
    "Thieves' Town Fortune Teller Entrance (E)": {
        'type': 'entrance', 'map': 'dark', 'coord': (119, 214),
        'link': {
            'North Dark World': [],
            "Thieves' Town Fortune Teller Entrance (I)": []}
    },
    "Thieves' Town Fortune Teller Entrance (I)": {
        'type': 'interior',
        'link': {
            "Thieves' Town Fortune Teller Entrance (E)": []}
    },
    'South Specialty Shop Entrance (E)': {
        'type': 'entrance_shop', 'map': 'dark', 'coord': (214, 302),
        'link': {
            'North Dark World': [],
            'South Specialty Shop Entrance (I)': []}
    },
    'South Specialty Shop Entrance (I)': {
        'type': 'interior',
        'link': {
            'South Specialty Shop Entrance (E)': []}
    },
    'Bumper Cave Bottom Entrance Entrance (E)': {
        'type': 'entrance_unique', 'map': 'dark', 'coord': (236, 116),
        'link': {
            'North Dark World': [],
            'Bumper Cave Bottom Entrance Entrance (I)': [
                ('nosettings', 'inverted')],
            'Hebra Ascent (Bottom) Entrance (I)': [('settings', 'inverted')]}
    },
    'Bumper Cave Bottom Entrance Entrance (I)': {
        'type': 'interior',
        'link': {
            'Bumper Cave Bottom Entrance Entrance (E)': [
                ('nosettings', 'inverted')],
            'Hebra Ascent (Bottom) Entrance (E)': [('settings', 'inverted')],
            'Bumper Cave 1': []}
    },
    'Bumper Cave 1': {
        'type': 'area',
        'link': {
            'Bumper Cave Bottom Entrance Entrance (I)': [],
            'Bumper Cave 2': [
                ('and', [
                    ('settings', 'placement_advanced'),
                    ('rabbitbarrier', None)]),
                ('item', 'hookshot')]}
    },
    'Bumper Cave 2': {
        'type': 'area',
        'link': {
            'Bumper Cave 1': [],
            'Bumper Cave 3': [('item', 'cape')]}
    },
    'Bumper Cave 3': {
        'type': 'area',
        'link': {
            'Bumper Cave 2': [('item', 'cape')],
            'Bumper Cave Top Entrance Entrance (I)': []}
    },
    'Bumper Cave Top Entrance Entrance (I)': {
        'type': 'interior',
        'link': {
            'Bumper Cave 3': [],
            'Bumper Cave Top Entrance Entrance (E)': [
                ('nosettings', 'inverted')],
            'Hebra Descent (Bottom) Entrance (E)': [('settings', 'inverted')]}
    },
    'Bumper Cave Top Entrance Entrance (E)': {
        'type': 'entrance_unique', 'map': 'dark', 'coord': (238, 101),
        'link': {
            'Bumper Cave Top Entrance Entrance (I)': [
                ('nosettings', 'inverted')],
            'Hebra Descent (Bottom) Entrance (I)': [('settings', 'inverted')],
            'Bumper Cave Top': []}
    },
    'Bumper Cave Top': {
        'type': 'area',
        'link': {
            'Hebra Descent End': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Bumper Cave Top Entrance Entrance (E)': [],
            'Bumper Cave': [],
            'North Dark World': []}
    },
    'Bumper Cave': {
        'type': 'item', 'map': 'dark', 'coord': (223, 101),
        'link': {
            'Bumper Cave Top': []}
    },
    'North Specialty Shop Entrance (E)': {
        'type': 'entrance_shop', 'map': 'dark', 'coord': (217, 37),
        'link': {
            'North Dark World': [],
            'North Specialty Shop Entrance (I)': []}
    },
    'North Specialty Shop Entrance (I)': {
        'type': 'interior',
        'link': {
            'North Specialty Shop Entrance (E)': []}
    },
    'Dark Chapel Entrance (E)': {
        'type': 'entrance', 'map': 'dark', 'coord': (300, 181),
        'link': {
            'North Dark World': [],
            'Dark Chapel Entrance (I)': []}
    },
    'Dark Chapel Entrance (I)': {
        'type': 'interior',
        'link': {
            'Dark Chapel Entrance (E)': []}
    }
}
