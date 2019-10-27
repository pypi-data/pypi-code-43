'''
Dark South World
'''

__all__ = 'LOCATIONS',


LOCATIONS = {
    'South Dark World': {
        'type': 'area',
        'link': {
            'South Light World': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Southern Shores': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Running Game': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Cave Near Haunted Grove Entrance (E)': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Bombos Stone Mountain': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Dark Bottle Ocarina': [],
            'Digging Game': [('rabbitbarrier', None)],
            'Shooting Game Entrance (E)': [],
            "Thieves' Town Surface": [('item', 'titansmitts')],
            'Ocarina Boy': [('rabbitbarrier', None)],
            'Fairy Pond Under Rocks (DW) Entrance (E)': [('item', 'pegasus')],
            'Portal Ersatz': [('and', [
                ('settings', 'inverted'), ('access', 'Castle Tower Reward'),
                ('rabbitbarrier', None)])],
            'Bomb Shop Entrance (E)': [],
            'East Dark World': [('item', 'hammer')],
            'Frozen Lake Shop Entrance (E)': [],
            'Frozen Lake': [('item', 'flippers')],
            'South Portal (DW)': [('item', 'hammer')],
            'Hiding Thief Cave Entrance (E)': [('item', 'bombs')],
            'Swamp Palace Entrance (E)': [],
            'Misery Mire Surface': [('and', [
                ('glitch', 'overworld'), ('item', 'pegasus')])]}
    },
    'Digging Game': {
        'type': 'item', 'map': 'dark', 'coord': (32, 459),
        'link': {
            'South Dark World': []}
    },
    'Shooting Game Entrance (E)': {
        'type': 'entrance', 'map': 'dark', 'coord': (137, 464),
        'link': {
            'South Dark World': [],
            'Shooting Game Entrance (I)': []}
    },
    'Shooting Game Entrance (I)': {
        'type': 'interior',
        'link': {
            'Shooting Game Entrance (E)': []}
    },
    'Ocarina Boy': {
        'type': 'item', 'map': 'dark', 'coord': (199, 452),
        'link': {
            'South Dark World': []}
    },
    'Fairy Pond Under Rocks (DW) Entrance (E)': {
        'type': 'entrance', 'map': 'dark', 'coord': (307, 433),
        'link': {
            'South Dark World': [],
            'Fairy Pond Under Rocks (DW) Entrance (I)': []}
    },
    'Fairy Pond Under Rocks (DW) Entrance (I)': {
        'type': 'interior',
        'link': {
            'Fairy Pond Under Rocks (DW) Entrance (E)': []}
    },
    'Portal Ersatz': {
        'type': 'area',
        'link': {
            'South Light World': [('state', 'rabbit')]}
    },
    'Bomb Shop Entrance (E)': {
        'type': 'entrance_unique', 'map': 'dark', 'coord': (363, 456),
        'link': {
            'South Dark World': [],
            'Bomb Shop Entrance (I)': [('nosettings', 'inverted')],
            "Link's House Entrance (I)": [('settings', 'inverted')]}
    },
    'Bomb Shop Entrance (I)': {
        'type': 'interior',
        'link': {
            'Bomb Shop Entrance (E)': [('nosettings', 'inverted')],
            "Link's House Entrance (E)": [('settings', 'inverted')]}
    },
    'Frozen Lake Shop Entrance (E)': {
        'type': 'entrance_shop', 'map': 'dark', 'coord': (424, 532),
        'link': {
            'South Dark World': [],
            'Frozen Lake Shop Entrance (I)': []}
    },
    'Frozen Lake Shop Entrance (I)': {
        'type': 'interior',
        'link': {
            'Frozen Lake Shop Entrance (E)': []}
    },
    'South Portal (DW)': {
        'type': 'area',
        'link': {
            'South Portal (LW)': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'South Dark World': [('item', 'hammer')],
            'South Portal': [('item', 'powerglove')]}
    },
    'Hiding Thief Cave Entrance (E)': {
        'type': 'entrance_unique', 'map': 'dark', 'coord': (391, 515),
        'link': {
            'South Dark World': [],
            'Hiding Thief Cave Entrance (I)': []}
    },
    'Hiding Thief Cave Entrance (I)': {
        'type': 'interior',
        'link': {
            'Hiding Thief Cave Entrance (E)': [],
            'Hiding Thief Cave': []}
    },
    'Hiding Thief Cave': {
        'type': 'cave', 'map': 'dark', 'coord': (391, 515),
        'link': {
            'Hiding Thief Cave Entrance (I)': []}
    },

    'Frozen Lake': {
        'type': 'area',
        'link': {
            'Lake Hylia': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Small Lake Hylia Island': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Ice Palace Exterior': [('settings', 'inverted')],
            'East Dark World': [],
            'Dark World Waterway': [],
            'Eastern Shores': []}
    },
    'Ice Palace Exterior': {
        'type': 'area',
        'link': {
            'Large Lake Hylia Island': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Ice Palace Portal': [('item', 'titansmitts')],
            'Frozen Lake': [('and', [
                ('settings', 'inverted'), ('item', 'flippers')])],
            'Ice Palace Entrance (E)': []}
    },
    'Dark World Waterway': {
        'type': 'area',
        'link': {
            'Frozen Lake': [],
            'Dark River': []}
    },

    'Eastern Shores': {
        'type': 'area',
        'link': {
            'Southern Shores': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Frozen Lake': [('item', 'flippers')],
            'Eastern Shores Under Rock Entrance (E)': [('item', 'powerglove')],
            'Eastern Shores Fairy Entrance (E)': [('item', 'bombs')],
            'Eastern Shores Cave Entrance (E)': []}
    },
    'Eastern Shores Under Rock Entrance (E)': {
        'type': 'entrance', 'map': 'dark', 'coord': (592, 521),
        'link': {
            'Eastern Shores': [],
            'Eastern Shores Under Rock Entrance (I)': []}
    },
    'Eastern Shores Under Rock Entrance (I)': {
        'type': 'interior',
        'link': {
            'Eastern Shores Under Rock Entrance (I)': []}
    },
    'Eastern Shores Fairy Entrance (E)': {
        'type': 'entrance', 'map': 'dark', 'coord': (588, 507),
        'link': {
            'Eastern Shores': [],
            'Eastern Shores Fairy Entrance (I)': []}
    },
    'Eastern Shores Fairy Entrance (I)': {
        'type': 'interior',
        'link': {
            'Eastern Shores Fairy Entrance (E)': []}
    },
    'Eastern Shores Cave Entrance (E)': {
        'type': 'entrance', 'map': 'dark', 'coord': (600, 507),
        'link': {
            'Eastern Shores': [],
            'Eastern Shores Cave Entrance (I)': []}
    },
    'Eastern Shores Cave Entrance (I)': {
        'type': 'interior',
        'link': {
            'Eastern Shores Cave Entrance (E)': []}
    },
}
