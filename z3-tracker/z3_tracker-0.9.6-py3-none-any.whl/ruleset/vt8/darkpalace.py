'''
Dark Palace
'''

__all__ = 'LOCATIONS',


LOCATIONS = {
    'Dark Palace Entrance (E)': {
        'type': 'entrance_dungeon', 'map': 'dark', 'coord': (629, 262),
        'link': {
            'East Dark World': [],
            'Dark Palace Entrance (I)': [
                ('settings', 'placement_advanced'),
                ('and', [
                    ('or', [
                        ('settings', 'swordless'), ('item', 'sword')]),
                    ('item', 'bottle')])]}
    },
    'Dark Palace Entrance (I)': {
        'type': 'interior',
        'link': {
            'Dark Palace Entrance (E)': [],
            'Dark Palace Front': [('and', [
                ('rabbitbarrier', None),
                ('or', [
                    ('settings', 'placement_advanced'),
                    ('and', [
                        ('or', [
                            ('settings', 'swordless'), ('item', 'sword')]),
                        ('item', 'bottle')])])])]}
    },
    'Dark Palace Front': {
        'type': 'area', 'dungeon': 'Dark Palace',
        'link': {
            'Dark Palace Entrance (E)': [],
            'Dark Palace First Key': [],
            'Dark Palace Centre': [('smallkey', ('Dark Palace', 6))],
            'Dark Palace Hidden Path': [
                ('item', 'bombs'), ('item', 'pegasus')]}
    },
    'Dark Palace First Key': {
        'type': 'dungeonchest', 'dungeon': 'Dark Palace',
        'link': {
            'Dark Palace Front': []}
    },
    'Dark Palace Hidden Path': {
        'type': 'area', 'dungeon': 'Dark Palace',
        'link': {
            'Dark Palace Front': [('item', 'bombs'), ('item', 'pegasus')],
            'Dark Palace Moving Floor': [('item', 'bow')]}
    },
    'Dark Palace Moving Floor': {
        'type': 'area', 'dungeon': 'Dark Palace',
        'link': {
            'Dark Palace Hidden Path': [],
            'Dark Palace Key With A View': [('item', 'bombs')],
            'Dark Palace Map': [],
            'Dark Palace Centre': [('item', 'hammer')]}
    },
    'Dark Palace Key With A View': {
        'type': 'dungeonchest', 'dungeon': 'Dark Palace',
        'link': {
            'Dark Palace Moving Floor': []}
    },
    'Dark Palace Map': {
        'type': 'dungeonchest', 'dungeon': 'Dark Palace',
        'link': {
            'Dark Palace Moving Floor': []}
    },
    'Dark Palace Centre': {
        'type': 'area', 'dungeon': 'Dark Palace',
        'link': {
            'Dark Palace Front': [],
            'Dark Palace Gauntlet Entrance': [('bigkey', 'Dark Palace')],
            'Dark Palace Big Key Drop': [('item', 'bombs')],
            'Dark Palace Stalfos Arena': [],
            'Dark Palace Targetting Chest': [],
            'Dark Palace Back': [('smallkey', ('Dark Palace', 5))]}
    },
    'Dark Palace Big Key Drop': {
        'type': 'area', 'dungeon': 'Dark Palace',
        'link': {
            'Dark Palace Stalfos Arena': [],
            'Dark Palace Big Key': [('smallkey', ('Dark Palace', 6))]}
    },
    'Dark Palace Big Key': {
        'type': 'dungeonchest', 'dungeon': 'Dark Palace',
        'link': {
            'Dark Palace Big Key Drop': [],
            'Dark Palace Big Key': []}
    },
    'Dark Palace Stalfos Arena': {
        'type': 'area', 'dungeon': 'Dark Palace',
        'link': {
            'Dark Palace Stalfos Key': [],
            'Dark Palace Front': []}
    },
    'Dark Palace Stalfos Key': {
        'type': 'dungeonchest', 'dungeon': 'Dark Palace',
        'link': {
            'Dark Palace Stalfos Arena': []}
    },
    'Dark Palace Targetting Chest': {
        'type': 'dungeonchest', 'dungeon': 'Dark Palace',
        'link': {
            'Dark Palace Centre': []}
    },
    'Dark Palace Back': {
        'type': 'area', 'dungeon': 'Dark Palace',
        'link': {
            'Dark Palace Maze Entrance': [('smallkey', ('Dark Palace', 8))],
            'Dark Palace Treasury': [
                ('item', 'lantern'),
                ('and', [
                    ('settings', 'placement_advanded'), ('item', 'firerod')])],
            'Dark Palace Compass': [],
            'Dark Palace Return Path': []}
    },
    'Dark Palace Maze Entrance': {
        'type': 'area', 'dungeon': 'Dark Palace',
        'link': {
            'Dark Palace Back': [],
            'Dark Palace Maze': [('item', 'lantern')]}
    },
    'Dark Palace Maze': {
        'type': 'area', 'dungeon': 'Dark Palace',
        'link': {
            'Dark Palace Maze Entrance': [],
            'Dark Palace Maze Bombs': [],
            'Dark Palace Maze Key': [],
            'Dark Palace Treasure': [('item', 'bombs')]},
    },
    'Dark Palace Maze Bombs': {
        'type': 'dungeonchest', 'dungeon': 'Dark Palace',
        'link': {
            'Dark Palace Maze': []}
    },
    'Dark Palace Maze Key': {
        'type': 'dungeonchest', 'dungeon': 'Dark Palace',
        'link': {
            'Dark Palace Maze': []}
    },
    'Dark Palace Treasure': {
        'type': 'dungeonchest_nokey', 'dungeon': 'Dark Palace',
        'link': {
            'Dark Palace Maze': [('item', 'lantern')]}
    },
    'Dark Palace Treasury': {
        'type': 'area', 'dungeon': 'Dark Palace',
        'link': {
            'Dark Palace Back': [],
            'Dark Palace Treasury Left Chest': [],
            'Dark Palace Treasury Right Chest': []}
    },
    'Dark Palace Treasury Left Chest': {
        'type': 'dungeonchest', 'dungeon': 'Dark Palace',
        'link': {
            'Dark Palace Treasury': []}
    },
    'Dark Palace Treasury Right Chest': {
        'type': 'dungeonchest', 'dungeon': 'Dark Palace',
        'link': {
            'Dark Palace Treasury': []}
    },
    'Dark Palace Compass': {
        'type': 'dungeonchest', 'dungeon': 'Dark Palace',
        'link': {
            'Dark Palace Back': []}
    },
    'Dark Palace Return Path': {
        'type': 'area', 'dungeon': 'Dark Palace',
        'link': {
            'Dark Palace Back': [],
            'Dark Palace Return Chest': [],
            'Dark Palace Centre': []}
    },
    'Dark Palace Return Chest': {
        'type': 'dungeonchest', 'dungeon': 'Dark Palace',
        'link': {
            'Dark Palace Return Path': []}
    },
    'Dark Palace Gauntlet Entrance': {
        'type': 'area', 'dungeon': 'Dark Palace',
        'link': {
            'Dark Palace Centre': [],
            'Dark Palace Gauntlet Door': [('item', 'bow')]}
    },
    'Dark Palace Gauntlet Door': {
        'type': 'area', 'dungeon': 'Dark Palace',
        'link': {
            'Dark Palace Gauntlet Entrance': [],
            'Dark Palace Gauntlet': [('and', [
                ('item', 'lantern'), ('item', 'hammer')])]}
    },
    'Dark Palace Gauntlet': {
        'type': 'area', 'dungeon': 'Dark Palace',
        'link': {
            'Dark Palace Gauntlet Door': [('item', 'hammer')],
            'Dark Palace Boss': [('smallkey', ('Dark Palace', 8))]}
    },
    'Dark Palace Boss': {
        'type': 'dungeonboss', 'dungeon': 'Dark Palace',
        'link': {
            'Dark Palace Boss Item': [('and', [
                ('or', [
                    ('item', 'bombs'), ('item', 'hammer')]),
                ('or', [
                    ('item', 'mastersword'), ('item', 'bow')])])]}
    },
    'Dark Palace Boss Item': {
        'type': 'dungeonchest_nokey', 'dungeon': 'Dark Palace',
        'link': {
            'Dark Palace Reward': []}
    },
    'Dark Palace Reward': {
        'type': 'dungeonreward', 'dungeon': 'Dark Palace',
        'link': {
            'Dark Palace Entrance (I)': []}
    },
}
