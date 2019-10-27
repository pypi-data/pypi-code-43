'''
Eastern Dark World
'''

__all__ = 'LOCATIONS',


LOCATIONS = {
    'Dark River': {
        'type': 'area',
        'link': {
            'Little River': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Witch Hut River': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'River Shop Area': [],
            'Dark World Waterway': []}
    },
    'River Shop Area': {
        'type': 'area',
        'link': {
            'East Light World': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'East Dark World': [('item', 'hammer'), ('item', 'powerglove')],
            'Dark River': [('item', 'flippers')],
            'North Dark World': [('item', 'hookshot')],
            'River Shop Entrance (E)': [],
            'Catfish Approach': [('item', 'powerglove')]}
    },
    'River Shop Entrance (E)': {
        'type': 'entrance_shop', 'map': 'dark', 'coord': (528, 224),
        'link': {
            'River Shop Area': [],
            'River Shop Entrance (I)': []}
    },
    'River Shop Entrance (I)': {
        'type': 'interior',
        'link': {
            'River Shop Entrance (E)': []}
    },
    'Catfish Approach': {
        'type': 'area',
        'link': {
            "Zora's River": [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'River Shop Area': [('item', 'powerglove')],
            'Dark River': [('item', 'flippers')],
            'Catfish': [('rabbitbarrier', None)]}
    },
    'Catfish': {
        'type': 'item', 'map': 'dark', 'coord': (587, 114),
        'link': {
            'Catfish Approach': []}
    },

    'East Dark World': {
        'type': 'area',
        'link': {
            'East Light World': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Dark Bottle Ocarina': [],
            'River Shop Area': [
                ('item', 'hammer'), ('item', 'powerglove'),
                ('and', [
                    ('glitch', 'overworld'), ('item', 'pegasus')])],
            'Dark River': [('item', 'flippers')],
            'Pyramid': [],
            'South Dark World': [('item', 'hammer')],
            'Frozen Lake': [('item', 'flippers')],
            'Dark Fairy Cave Entrance (E)': [],
            'Fake Dark Palace Entrance (E)': [],
            'East Portal (DW)': [('item', 'hammer')],
            'Dark Fairy Pond Entrance (E)': [],
            'Dark Palace Entrance (E)': [('rabbitbarrier', None)]}
    },
    'Dark Fairy Cave Entrance (E)': {
        'type': 'entrance', 'map': 'dark', 'coord': (540, 427),
        'link': {
            'East Dark World': [],
            'Dark Fairy Cave Entrance (I)': []}
    },
    'Dark Fairy Cave Entrance (I)': {
        'type': 'interior',
        'link': {
            'Dark Fairy Cave Entrance (E)': []}
    },
    'Fake Dark Palace Entrance (E)': {
        'type': 'entrance', 'map': 'dark', 'coord': (557, 332),
        'link': {
            'East Dark World': [],
            'Fake Dark Palace Entrance (I)': []}
    },
    'Fake Dark Palace Entrance (I)': {
        'type': 'interior',
        'link': {
            'Fake Dark Palace Entrance (E)': []}
    },
    'East Portal (DW)': {
        'type': 'area',
        'link': {
            'East Portal (LW)': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'East Portal': [('item', 'powerglove')],
            'East Dark World': [('item', 'hammer')]}
    },
    'Dark Fairy Pond Entrance (E)': {
        'type': 'entrance', 'map': 'dark', 'coord': (644, 464),
        'link': {
            'East Dark World': [],
            'Dark Fairy Pond Entrance (I)': []}
    },
    'Dark Fairy Pond Entrance (I)': {
        'type': 'interior',
        'link': {
            'Dark Fairy Pond Entrance (I)': []}
    },

    'Pyramid': {
        'type': 'area',
        'link': {
            'Hyrule Castle': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Castle Walls': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Dark Bottle Ocarina': [],
            'East Dark World': [],
            'Pyramid Item': [],
            'Pyramid Fairy Entrance (E)': [('and', [
                ('access', 'Bomb Shop Entrance (I)'),
                ('crystals', 'fairy'),
                ('rabbitbarrier', None),
                ('or', [
                    ('and', [
                        ('or', [
                            ('settings', 'open'), ('settings', 'standard')]),
                        ('nosettings', 'entrance'),
                        ('item', 'hammer')]),
                    ('and', [
                        ('settings', 'inverted'),
                        ('nosettings', 'entrance'),
                        ('item', 'mirror')]),
                    ('and', [
                        ('or', [
                            ('and', [
                                ('nosettings', 'open'),
                                ('nosettings', 'standard'),
                                ('nosettings', 'inverted')]),
                            ('settings', 'entrance')]),
                        ('state', 'maybe;add')])])])],
            'Ganon Drop Entrance (E)': [('and', [
                ('nosettings', 'inverted'), ('macro', 'ganon')])]}
    },
    'Pyramid Item': {
        'type': 'item', 'map': 'dark', 'coord': (379, 297),
        'link': {
            'Pyramid': []}
    },
    'Pyramid Fairy Entrance (E)': {
        'type': 'entrance_unique', 'map': 'dark', 'coord': (305, 321),
        'link': {
            'Pyramid': [],
            'Pyramid Fairy Entrance (I)': []}
    },
    'Pyramid Fairy Entrance (I)': {
        'type': 'interior',
        'link': {
            'Pyramid Fairy Entrance (E)': [],
            'Pyramid Fairy': []}
    },
    'Pyramid Fairy': {
        'type': 'cave', 'map': 'dark', 'coord': (305, 321),
        'link': {
            'Pyramid Fairy Entrance (I)': []}
    },
    'Ganon Drop Entrance (E)': {
        'type': 'entrance_drop', 'map': 'dark', 'coord': (324, 270),
        'link': {
            'Ganon Drop Entrance (I)': []}
    },
    'Ganon Drop Entrance (I)': {
        'type': 'interior',
        'link': {
            'Ganon': [('and', [
                ('item', 'mastersword'),
                ('item', 'bow'),
                ('or', [
                    ('item', 'silverarrows'),
                    ('settings', 'placement_advanced')])])]}
    },
    'Ganon': {
        'type': 'ganon', 'map': 'dark', 'coord': (324, 240),
        'link': {}
    },
}
