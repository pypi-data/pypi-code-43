'''
Kakariko
'''

__all__ = 'LOCATIONS',


LOCATIONS = {
    'Kakariko': {
        'type': 'area',
        'link': {
            "Thieves' Town Surface": [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            "East Thieves' Town": [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'Light Bottle Ocarina': [],
            "Blacksmiths' House Entrance (E)": [],
            'Above The Bat': [
                ('item', 'hammer'),
                ('and', [
                    ('glitch', 'overworld'), ('item', 'pegasus')])],
            "Mad Batter's Cave Entrance Entrance (E)": [],
            'South Light World': [],
            'Tavern Front Entrance (E)': [],
            'Kakariko Shop Entrance (E)': [],
            'Secret House Entrance (E)': [('item', 'bombs')],
            'Cucco House Entrance (E)': [],
            "Bug Child's House Entrance (E)": [],
            'Tavern Back Entrance': [('rabbitbarrier', None)],
            'Kakariko Blue House Entrance (E)': [('rabbitbarrier', None)],
            'Kakariko East Red House Entrance (E)': [],
            'Bottle Vendor': [],
            'Kakariko West Red House Entrance (E)': [],
            'Kakariko Cave Entrance Entrance (E)': [],
            'Kakariko Cave Drop Entrance (E)': [],
            'Lost Woods': [('rabbitbarrier', None)],
            'Kakariko Portal (LW)': [('item', 'titansmitts')],
            "Blind's House Entrance (E)": [],
            "Sahasrahla's House West Entrance Entrance (E)": [],
            "Sahasrahla's House East Entrance Entrance (E)": [],
            'North Light World': []}
    },
    "Blacksmiths' House Entrance (E)": {
        'type': 'entrance_unique', 'map': 'light', 'coord': (202, 353),
        'link': {
            'Kakariko': [],
            "Blacksmiths' House Entrance (I)": []}
    },
    "Blacksmiths' House Entrance (I)": {
        'type': 'interior',
        'link': {
            "Blacksmiths' House Entrance (E)": [],
            'Blacksmiths': [('and', [
                ('access', 'Frog Prison'),
                ('or', [
                    ('settings', 'placement_advanced'), ('item', 'mirror')])])]}
    },
    'Blacksmiths': {
        'type': 'chest', 'map': 'light', 'coord': (202, 347),
        'link': {
            "Blacksmiths' House Entrance (I)": []}
    },
    'Above The Bat': {
        'type': 'area',
        'link': {
            'Kakariko': [('item', 'hammer')],
            "Mad Batter's Cave Drop Entrance (E)": []}
    },
    "Mad Batter's Cave Drop Entrance (E)": {
        'type': 'entrance_drop', 'map': 'light', 'coord': (224, 365),
        'link': {
            "Mad Batter's Cave Drop Entrance (I)": []}
    },
    "Mad Batter's Cave Drop Entrance (I)": {
        'type': 'interior',
        'link': {
            "Mad Batter's Cave": []}
    },
    "Mad Batter's Cave": {
        'type': 'area',
        'link': {
            'Mad Batter': [('item', 'powder')],
            "Mad Batter's Cave Front": []}
    },
    'Mad Batter': {
        'type': 'drop', 'map': 'light', 'coord': (215, 373),
        'link': {
            "Mad Batter's Cave": []}
    },
    "Mad Batter's Cave Front": {
        'type': 'area',
        'link': {
            "Mad Batter's Cave Entrance Entrance (I)": []}
    },
    "Mad Batter's Cave Entrance Entrance (I)": {
        'type': 'interior',
        'link': {
            "Mad Batter's Cave Front": [],
            "Mad Batter's Cave Entrance Entrance (E)": []},
    },
    "Mad Batter's Cave Entrance Entrance (E)": {
        'type': 'entrance_unique', 'map': 'light', 'coord': (210, 368),
        'link': {
            "Mad Batter's Cave Entrance Entrance (I)": [],
            'Kakariko': []}
    },
    'Tavern Front Entrance (E)': {
        'type': 'entrance', 'map': 'light', 'coord': (106, 395),
        'link': {
            'Kakariko': [],
            'Tavern Front Entrance (I)': []}
    },
    'Tavern Front Entrance (I)': {
        'type': 'interior',
        'link': {
            'Tavern Front Entrance (E)': []}
    },
    'Kakariko Shop Entrance (E)': {
        'type': 'entrance_shop', 'map': 'light', 'coord': (73, 387),
        'link': {
            'Kakariko': [],
            'Kakariko Shop Entrance (I)': []}
    },
    'Kakariko Shop Entrance (I)': {
        'type': 'interior',
        'link': {
            'Kakariko Shop Entrance (E)': []}
    },
    'Secret House Entrance (E)': {
        'type': 'entrance', 'map': 'light', 'coord': (18, 394),
        'link': {
            'Kakariko': [],
            'Cucco House Entrance (I)': []}
    },
    'Secret House Entrance (I)': {
        'type': 'interior',
        'link': {
            'Secret House Entrance (E)': []}
    },
    'Cucco House Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (65, 358),
        'link': {
            'Kakariko': [],
            'Cucco House Entrance (E)': []}
    },
    'Cucco House Entrance (I)': {
        'type': 'interior',
        'link': {
            'Cucco House Entrance (E)': [],
            'Cucco House': [('item', 'bombs')]}
    },
    'Cucco House': {
        'type': 'chest', 'map': 'light', 'coord': (65, 350),
        'link': {
            'Cucco House Entrance (I)': []}
    },
    "Bug Child's House Entrance (E)": {
        'type': 'entrance_unique', 'map': 'light', 'coord': (104, 356),
        'link': {
            'Kakariko': [],
            "Bug Child's House Entrance (I)": []}
    },
    "Bug Child's House Entrance (I)": {
        'type': 'interior',
        'link': {
            "Bug Child's House Entrance (E)": [],
            'Bug Child': [('item', 'bottle')]}
    },
    'Bug Child': {
        'type': 'chest', 'map': 'light', 'coord': (104, 351),
        'link': {
            "Bug Child's House Entrance (I)": []}
    },
    'Tavern Back Entrance': {
        'type': 'item', 'map': 'light', 'coord': (106, 376),
        'link': {
            'Kakariko': []}
    },
    'Kakariko Blue House Entrance (E)': {
        'type': 'entrance', 'map': 'light', 'coord': (135, 353),
        'link': {
            'Kakariko': [],
            'Kakariko Blue House Entrance (I)': []}
    },
    'Kakariko Blue House Entrance (I)': {
        'type': 'interior',
        'link': {
            'Kakariko Blue House Entrance (E)': []}
    },
    'Kakariko East Red House Entrance (E)': {
        'type': 'entrance', 'map': 'light', 'coord': (137, 319),
        'link': {
            'Kakariko': [],
            'Kakariko East Red House Entrance (I)': []}
    },
    'Kakariko East Red House Entrance (I)': {
        'type': 'interior',
        'link': {
            'Kakariko East Red House Entrance (E)': []}
    },
    'Bottle Vendor': {
        'type': 'item', 'map': 'light', 'coord': (63, 308),
        'link': {
            'Kakariko': []}
    },
    'Kakariko West Red House Entrance (E)': {
        'type': 'entrance', 'map': 'light', 'coord': (33, 309),
        'link': {
            'Kakariko': [],
            'Kakariko West Red House Entrance (I)': []}
    },
    'Kakariko West Red House Entrance (I)': {
        'type': 'interior',
        'link': {
            'Kakariko West Red House Entrance (E)': []}
    },
    'Kakariko Cave Drop Entrance (E)': {
        'type': 'entrance_drop', 'map': 'light', 'coord': (15, 282),
        'link': {
            'Kakariko Cave Drop Entrance (I)': []}
    },
    'Kakariko Cave Drop Entrance (I)': {
        'type': 'interior',
        'link': {
            'Kakariko Cave': [('item', 'bombs')],
            'Kakariko Cave Bottom': []}
    },
    'Kakariko Cave': {
        'type': 'drop', 'map': 'light', 'coord': (15, 282),
        'link': {
            'Kakariko Cave Bottom': []}
    },
    'Kakariko Cave Bottom': {
        'type': 'area',
        'link': {
            'Kakariko Cave Entrance Entrance (I)': []}
    },
    'Kakariko Cave Entrance Entrance (I)': {
        'type': 'interior',
        'link': {
            'Kakariko Cave Bottom': [],
            'Kakariko Cave Entrance Entrance (E)': []}
    },
    'Kakariko Cave Entrance Entrance (E)': {
        'type': 'entrance_unique', 'map': 'light', 'coord': (31, 283),
        'link': {
            'Kakariko Cave Entrance Entrance (I)': [],
            'Kakariko': []}
    },
    'Kakariko Portal (LW)': {
        'type': 'area',
        'link': {
            'Kakariko Portal (DW)': [('and', [
                ('settings', 'inverted'), ('item', 'mirror')])],
            'Kakariko Portal': [('item', 'powerglove')],
            'Kakariko': [('item', 'titansmitts')],
            'Lost Woods': [('item', 'hammer')]}
    },
    'Kakariko Portal': {
        'type': 'area',
        'link': {
            'Kakariko Portal (LW)': [('and', [
                ('settings', 'inverted'), ('state', 'rabbit')])],
            'Kakariko Portal (DW)': [('and', [
                ('nosettings', 'inverted'), ('state', 'rabbit')])]}
    },
    "Blind's House Entrance (E)": {
        'type': 'entrance_unique', 'map': 'light', 'coord': (85, 279),
        'link': {
            'Kakariko': [],
            "Blind's House Entrance (I)": []}
    },
    "Blind's House Entrance (I)": {
        'type': 'interior',
        'link': {
            "Blind's House Entrance (E)": [],
            "Blind's House": [('item', 'bombs')]}
    },
    "Blind's House": {
        'type': 'chest', 'map': 'light', 'coord': (85, 272),
        'link': {
            "Blind's House Entrance (I)": []}
    },
    "Sahasrahla's House East Entrance Entrance (E)": {
        'type': 'entrance_unique', 'map': 'light', 'coord': (115, 279),
        'link': {
            'Kakariko': [],
            "Sahasrahla's House East Entrance Entrance (I)": []}
    },
    "Sahasrahla's House East Entrance Entrance (I)": {
        'type': 'interior',
        'link': {
            "Sahasrahla's House East Entrance Entrance (E)": [],
            "Sahasrahla's House West Entrance Entrance (I)": []}
    },
    "Sahasrahla's House West Entrance Entrance (I)": {
        'type': 'interior',
        'link': {
            "Sahasrahla's House East Entrance Entrance (I)": [],
            "Sahasrahla's House West Entrance Entrance (E)": []}
    },
    "Sahasrahla's House West Entrance Entrance (E)": {
        'type': 'entrance_unique', 'map': 'light', 'coord': (101, 279),
        'link': {
            "Sahasrahla's House West Entrance Entrance (I)": [],
            'Kakariko': []}
    },
}
