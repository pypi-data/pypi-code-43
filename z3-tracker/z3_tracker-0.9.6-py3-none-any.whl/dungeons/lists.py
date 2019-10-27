'''
General dungeon info
'''

__all__ = 'DUNGEONS',


DUNGEONS = {
    'East Palace': (
        (0, 0), 0, 'eastpalace',
        ('map', 'compass', 'bigkey', 'reward')
    ),
    'Desert Palace': (
        (1, 0), 1, 'desertpalace',
        ('map', 'compass', 'bigkey', 'reward')
    ),
    'Mountain Tower': (
        (2, 0), 1, 'mountaintower',
        ('map', 'compass', 'bigkey', 'reward')
    ),
    'Castle Tower': (
        (3, 0), 2, 'castletower',
        ()
    ),
    'Dark Palace': (
        (0, 1), 6, 'darkpalace',
        ('map', 'compass', 'bigkey', 'reward')
    ),
    'Swamp Palace': (
        (1, 1), 1, 'swamppalace',
        ('map', 'compass', 'bigkey', 'reward')
    ),
    'Skull Woods': (
        (2, 1), 3, 'skullwoods',
        ('map', 'compass', 'bigkey', 'reward')
    ),
    "Thieves' Town": (
        (3, 1), 1, 'thievestown',
        ('map', 'compass', 'bigkey', 'reward')
    ),
    'Ice Palace': (
        (0, 2), 2, 'icepalace',
        ('map', 'compass', 'bigkey', 'reward')
    ),
    'Misery Mire': (
        (1, 2), 3, 'miserymire',
        ('map', 'compass', 'bigkey', 'reward', 'medallion')
    ),
    'Turtle Rock': (
        (2, 2), 4, 'turtlerock',
        ('map', 'compass', 'bigkey', 'reward', 'medallion')
    ),
    "Ganon's Tower": (
        (3, 2), 4, 'ganonstower',
        ('map', 'compass', 'bigkey')
    )
}
