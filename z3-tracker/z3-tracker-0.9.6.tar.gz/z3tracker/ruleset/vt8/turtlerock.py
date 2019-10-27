'''
Turtle Rock
'''

__all__ = 'LOCATIONS',


LOCATIONS = {
    'Turtle Rock Entrance Entrance (E)': {
        'type': 'entrance_dungeon', 'map': 'dark', 'coord': (618, 54),
        'link': {
            'East Upper Death Mountain': [],
            'Turtle Rock Entrance Entrance (I)': [
                ('settings', 'placement_advanced'),
                ('and', [
                    ('or', [
                        ('settings', 'swordless'), ('item', 'mastersword')]),
                    ('or', [
                        ('settings', 'bottle'), ('item', 'bluemail')])])]}
    },
    'Turtle Rock Entrance Entrance (I)': {
        'type': 'interior',
        'link': {
            'Turtle Rock Entrance Entrance (E)': [],
            'Turtle Rock Big Hole': [('item', 'somaria')]}
    },
    'Turtle Rock Big Hole': {
        'type': 'area', 'dungeon': 'Turtle Rock',
        'link': {
            'Turtle Rock Entrance Entrance (I)': [('item', 'somaria')],
            'Turtle Rock Compass': [('item', 'somaria')],
            'Turtle Rock Rolling Spikes': [('and', [
                ('item', 'somaria'), ('item', 'firerod')])],
            'Turtle Rock Hokkubokku Key Room': [('item', 'somaria')]}
    },
    'Turtle Rock Compass': {
        'type': 'dungeonchest', 'dungeon': 'Turtle Rock',
        'link': {
            'Turtle Rock Big Hole': []}
    },
    'Turtle Rock Rolling Spikes': {
        'type': 'area', 'dungeon': 'Turtle Rock',
        'link': {
            'Turtle Rock Big Hole': [],
            'Turtle Rock Map': [],
            'Turtle Rock Map Key': []}
    },
    'Turtle Rock Map': {
        'type': 'dungeonchest', 'dungeon': 'Turtle Rock',
        'link': {
            'Turtle Rock Rolling Spikes': []}
    },
    'Turtle Rock Map Key': {
        'type': 'dungeonchest', 'dungeon': 'Turtle Rock',
        'link': {
            'Turtle Rock Rolling Spikes': []}
    },
    'Turtle Rock Hokkubokku Key Room': {
        'type': 'area', 'dungeon': 'Turtle Rock',
        'link': {
            'Turtle Rock Big Hole': [],
            'Turtle Rock Chain Chomp Room': [('smallkey', ('Turtle Rock', 0))],
            'Turtle Rock First Hokkubokku Key': []}
    },
    'Turtle Rock First Hokkubokku Key': {
        'type': 'dungeonkey', 'dungeon': 'Turtle Rock',
        'link': {
            'Turtle Rock Hokkubokku Key Room': []}
    },
    'Turtle Rock Chain Chomp Room': {
        'type': 'area', 'dungeon': 'Turtle Rock',
        'link': {
            'Turtle Rock Hokkubokku Key Room': [],
            'Turtle Rock Chain Chomp Key': [],
            'Turtle Rock Pipe Rooms': [('smallkey', ('Turtle Rock', 0))]}
    },
    'Turtle Rock Chain Chomp Key': {
        'type': 'dungeonchest', 'dungeon': 'Turtle Rock',
        'link': {
            'Turtle Rock Chain Chomp Room': []}
    },
    'Turtle Rock Pipe Rooms': {
        'type': 'area', 'dungeon': 'Turtle Rock',
        'link': {
            'Turtle Rock Chain Chomp Room': [],
            'Turtle Rock Second Hokkubokku Key': [],
            'Turtle Rock Big Key': [('smallkey', ('Turtle Rock', 0))],
            'Turtle Rock Hokkubokku Room': []}
    },
    'Turtle Rock Second Hokkubokku Key': {
        'type': 'dungeonkey', 'dungeon': 'Turtle Rock',
        'link': {
            'Turtle Rock Pipe Rooms': []}
    },
    'Turtle Rock Big Key': {
        'type': 'dungeonchest', 'dungeon': 'Turtle Rock',
        'link': {
            'Turtle Rock Pipe Rooms': []}
    },
    'Turtle Rock Hokkubokku Room': {
        'type': 'area', 'dungeon': 'Turtle Rock',
        'link': {
            'Turtle Rock Pipe Rooms': [],
            'Turtle Rock Laser Eye Exit Entrance (I)': [],
            'Turtle Rock Zoro Room': [('bigkey', 'Turtle Rock')]}
    },
    'Turtle Rock Laser Eye Exit Entrance (I)': {
        'type': 'interior',
        'link': {
            'Turtle Rock Hokkubokku Room': [('and', [
                ('rabbitbarrier', None),
                ('or', [
                    ('settings', 'placement_advanced'),
                    ('and', [
                        ('or', [
                            ('settings', 'swordless'),
                            ('item', 'mastersword')]),
                        ('or', [
                            ('settings', 'bottle'),
                            ('item', 'bluemail')])])])])],
            'Turtle Rock Laser Eye Exit Entrance (E)': []}
    },
    'Turtle Rock Laser Eye Exit Entrance (E)': {
        'type': 'entrance_dungeon', 'map': 'dark', 'coord': (522, 60),
        'link': {
            'Turtle Rock Laser Eye Exit Entrance (I)': [],
            'Turtle Rock Balcony': []}
    },
    'Turtle Rock Balcony': {
        'type': 'area',
        'link': {
            'Spiral Cave Top Entrance Entrance (E)': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Goriya Cave Entrance (E)': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Turtle Rock Laser Eye Exit Entrance (E)': [],
            'Turtle Rock Big Chest Exit Entrance (E)': []}
    },
    'Turtle Rock Big Chest Exit Entrance (E)': {
        'type': 'entrance_dungeon', 'map': 'dark', 'coord': (553, 60),
        'link': {
            'Turtle Rock Balcony': [],
            'Turtle Rock Big Chest Exit Entrance (I)': []}
    },
    'Turtle Rock Big Chest Exit Entrance (I)': {
        'type': 'interior',
        'link': {
            'Turtle Rock Big Chest Exit Entrance (E)': [],
            'Turtle Rock Treasure': [('and', [
                ('or', [
                    ('item', 'hookshot'), ('item', 'somaria')]),
                ('or', [
                    ('settings', 'placement_advanced'),
                    ('and', [
                        ('or', [
                            ('settings', 'swordless'),
                            ('item', 'mastersword')]),
                        ('or', [
                            ('settings', 'bottle'),
                            ('item', 'bluemail')])])])])],
            'Turtle Rock Hokkubokku Room': [('and', [
                ('item', 'pegasus'),
                ('or', [
                    ('settings', 'placement_advanced'),
                    ('and', [
                        ('or', [
                            ('settings', 'swordless'),
                            ('item', 'mastersword')]),
                        ('or', [
                            ('settings', 'bottle'),
                            ('item', 'bluemail')])])])])]}
    },
    'Turtle Rock Treasure': {
        'type': 'dungeonchest_nokey', 'dungeon': 'Turtle Rock',
        'link': {
            'Turtle Rock Big Chest Exit Entrance (I)': [('item', 'somaria')],
            'Turtle Rock Hokkubokku Room': []}
    },
    'Turtle Rock Zoro Room': {
        'type': 'area', 'dungeon': 'Turtle Rock',
        'link': {
            'Turtle Rock Hokkubokku Room': [],
            'Turtle Rock Switch Room': [('item', 'bombs'), ('item', 'pegasus')]}
    },
    'Turtle Rock Switch Room': {
        'type': 'area', 'dungeon': 'Turtle Rock',
        'link': {
            'Turtle Rock Zoro Room': [],
            'Turtle Rock Switch Key': [],
            'Turtle Rock Dark Room': [('smallkey', ('Turtle Rock', 0))]}
    },
    'Turtle Rock Switch Key': {
        'type': 'dungeonchest_nokey', 'dungeon': 'Turtle Rock',
        'link': {
            'Turtle Rock Switch Room': []}
    },
    'Turtle Rock Dark Room': {
        'type': 'area', 'dungeon': 'Turtle Rock',
        'link': {
            'Turtle Rock Switch Room': [('and', [
                ('item', 'lantern'), ('item', 'somaria')])],
            'Turtle Rock Treasury': [('and', [
                ('item', 'lantern'), ('item', 'somaria')])]}
    },
    'Turtle Rock Treasury': {
        'type': 'area', 'dungeon': 'Turtle Rock',
        'link': {
            'Turtle Rock Dark Room': [],
            'Turtle Rock Treasury Chest 1': [
                ('item', 'mirrorshield'), ('item', 'byrna'), ('item', 'cape'),
                ('settings', 'placement_advanced')],
            'Turtle Rock Treasury Chest 2': [
                ('item', 'mirrorshield'), ('item', 'byrna'), ('item', 'cape'),
                ('settings', 'placement_advanced')],
            'Turtle Rock Treasury Chest 3': [
                ('item', 'mirrorshield'), ('item', 'byrna'), ('item', 'cape'),
                ('settings', 'placement_advanced')],
            'Turtle Rock Treasury Chest 4': [
                ('item', 'mirrorshield'), ('item', 'byrna'), ('item', 'cape'),
                ('settings', 'placement_advanced')],
            'Turtle Rock Fairy Exit Entrance (I)': [('item', 'bombs')],
            'Turtle Rock Boss Maze': [('smallkey', ('Turtle Rock', 0))]}
    },
    'Turtle Rock Treasury Chest 1': {
        'type': 'dungeonchest_nokey', 'dungeon': 'Turtle Rock',
        'link': {
            'Turtle Rock Treasury': []}
    },
    'Turtle Rock Treasury Chest 2': {
        'type': 'dungeonchest_nokey', 'dungeon': 'Turtle Rock',
        'link': {
            'Turtle Rock Treasury': []}
    },
    'Turtle Rock Treasury Chest 3': {
        'type': 'dungeonchest_nokey', 'dungeon': 'Turtle Rock',
        'link': {
            'Turtle Rock Treasury': []}
    },
    'Turtle Rock Treasury Chest 4': {
        'type': 'dungeonchest_nokey', 'dungeon': 'Turtle Rock',
        'link': {
            'Turtle Rock Treasury': []}
    },
    'Turtle Rock Fairy Exit Entrance (I)': {
        'type': 'interior',
        'link': {
            'Turtle Rock Treasury': [('and', [
                ('rabbitbarrier', None),
                ('or', [
                    ('settings', 'placement_advanced'),
                    ('and', [
                        ('or', [
                            ('settings', 'swordless'),
                            ('item', 'mastersword')]),
                        ('or', [
                            ('settings', 'bottle'),
                            ('item', 'bluemail')])])])])],
            'Turtle Rock Fairy Exit Entrance (E)': []}
    },
    'Turtle Rock Fairy Exit Entrance (E)': {
        'type': 'entrance_dungeon', 'map': 'dark', 'coord': (538, 76),
        'link': {
            'Turtle Rock Fairy Exit Entrance (I)': [],
            'Turtle Rock Fairy Exit': []}
    },
    'Turtle Rock Fairy Exit': {
        'type': 'area',
        'link': {
            'Fairy Maze Top Entrance Entrance (E)': [('and', [
                ('nosettings', 'inverted'), ('item', 'mirror')])],
            'Turtle Rock Fairy Exit Entrance (E)': []}
    },
    'Turtle Rock Boss Maze': {
        'type': 'area', 'dungeon': 'Turtle Rock',
        'link': {
            'Turtle Rock Treasury': [],
            'Turtle Rock Boss Door': [('item', 'somaria')]}
    },
    'Turtle Rock Boss Door': {
        'type': 'area', 'dungeon': 'Turtle Rock',
        'link': {
            'Turtle Rock Boss Maze': [('item', 'somaria')],
            'Turtle Rock Boss': [('bigkey', 'Turtle Rock')]}
    },
    'Turtle Rock Boss': {
        'type': 'dungeonboss', 'dungeon': 'Turtle Rock',
        'link': {
            'Turtle Rock Boss Item': [('and', [
                ('item', 'firerod'),
                ('item', 'icerod'),
                ('or', [
                    ('settings', 'placement_advanced'),
                    ('settings', 'swordless'),
                    ('settings', 'mastersword2'),
                    ('and', [
                        ('or', [
                            ('item', 'bottle'), ('item', 'halfmagic')]),
                        ('item', 'mastersword')])]),
                ('or', [
                    ('item', 'mastersword3'), ('item', 'hammer'),
                    ('and', [
                        ('or', [
                            ('item', 'bottle'), ('item', 'halfmagic')]),
                        ('item', 'sword')])])])]}
    },
    'Turtle Rock Boss Item': {
        'type': 'dungeonchest_nokey', 'dungeon': 'Turtle Rock',
        'link': {
            'Turtle Rock Reward': []}
    },
    'Turtle Rock Reward': {
        'type': 'dungeonreward', 'dungeon': 'Turtle Rock',
        'link': {
            'Turtle Rock Entrance Entrance (I)': []}
    },
}
