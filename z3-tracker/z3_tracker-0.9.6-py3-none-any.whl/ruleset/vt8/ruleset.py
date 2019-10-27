'''
Rules management
'''

import importlib
import typing

LOCATIONIMPORTS = (
    'castle', 'darkpalace', 'darkworld_east', 'darkworld_north',
    'darkworld_south', 'deathmountain', 'desert', 'dungeons', 'ganonstower',
    'hebra', 'icepalace', 'kakariko', 'lightworld_east', 'lightworld_north',
    'lightworld_south', 'miserymire', 'mountaintower', 'ocarina', 'swamppalace',
    'skullwoods', 'thievestown', 'turtlerock')
LOCATIONS = {}
for locimp in LOCATIONIMPORTS:
    addloc = importlib.import_module(
        '.{0:s}'.format(locimp), package=__package__)
    LOCATIONS.update(addloc.LOCATIONS)
del addloc, locimp

__all__ = 'Ruleset',


class Ruleset(dict):
    '''
    Placement ruleset
    '''

    def __init__(self):
        super().__init__()
        self.dungeons = {}
        self.parse_locations()

    def parse_locations(self) -> None:
        '''
        Create location database.
        '''

        for loc in LOCATIONS:
            self[loc] = Location(LOCATIONS[loc])
            if 'dungeon' in LOCATIONS[loc]:
                if self[loc].dungeon not in self.dungeons:
                    self.dungeons[self[loc].dungeon] = Dungeon()
                self.dungeons[self[loc].dungeon][loc] = self[loc]

    def locations(self, gametype: str, maptype: str) -> dict:
        '''
        Return a list of locations to be displayed on a map.

        Args:
            gametype: 'item' or 'entrance'
            maptype: 'light' or 'dark'
        Returns:
            dict: {
                'location name': {'map': str, 'coord': (int, int), 'type': str}}
        '''

        assert gametype in ('item', 'item_retro', 'entrance')
        assert maptype in ('light', 'dark')
        if gametype == 'item':
            valid = 'chest', 'item', 'cave', 'drop', 'dungeon', 'ganon'
        elif gametype == 'item_retro':
            valid = (
                'chest', 'item', 'cave', 'drop', 'dungeon', 'ganon', 'entrance',
                'entrance_shop')
        else:
            valid = ('entrance', 'entrance_unique', 'entrance_shop',
                     'entrance_drop', 'entrance_dungeon', 'item', 'dungeon',
                     'ganon')
        ret = {}
        for loc in self:
            if self[loc].type in valid and self[loc].map == maptype:
                ret[loc] = {
                    'map': self[loc].map, 'coord': self[loc].coord,
                    'type': self[loc].type}
        return ret

    def disconnect_entrances(self) -> None:
        '''
        Disconnect all entrances from each other.
        '''

        for loc in self:
            for link in tuple(self[loc].link.keys()):
                if ((self[loc].type.startswith('entrance') and
                     self[link].type == 'interior') or
                    (self[loc].type == 'interior' and
                     self[link].type.startswith('entrance'))):
                    del self[loc].link[link]


class Location(object):
    '''
    Location object

    Instance variables:
        type:
            - 'chest': chest in house or in the open
            - 'interior': interior connector; always has 'entrance' counterpart
            - 'entrance': exterior connector shuffable by entrance randomiser
            - 'entrance_unique': like entrance, but no take-any cave
            - 'area': generic area linking other locations
            - 'item': item in the open (or semi-hidden, e.g. buried)
            - 'cave': open or chested item in a cave
            - 'drop': drophole or downstairs cave
            - 'dungeonchest': generic randomised item found in dungeon
            - 'dungeonchest_nokey': can't hold a key
            - 'dungeonkey': fixed small key found in dungeon
            - 'dungeonboss': dungeon boss
            - 'dungeonreward': pendant or crystal
            - 'dungeon': the overall dungeon itself
            - 'ganon': only used for the final bossfight
        map: map on which location is displayed (not for 'area' or 'interior')
        coord: coordinates of location on map (not for 'area' or 'interior')
        dungeon: parent dungeon (only for dungeon locations)
        link: locations to which this location connects, following the format
            {'linked location': {'requirement type': 'requirement', ...}};
            possible requirements are:
            - 'settings': required settings
            - 'nosettings': only if given setting is not active
            - 'item': item in possession
            - 'access': name of another location which needs to be available
            - 'medallion': dynamic medallion requirement for two dungeons
            - 'pendant': pendant in posession
            - 'crystals': certain crystals in posession
            - 'smallkeys': given number of dungeon chests being available
            - 'bigkey': all dungeon chests being available
            - 'macro': more complex requirements
        visible: list of locations visible from here
        checked: boolean always set to False or None
    '''

    def __init__(self, location: dict):
        '''
        Args:
            location: location info; if None then object is uninitialised
        '''

        assert location['type'] in (
            'chest', 'interior', 'entrance', 'entrance_unique', 'entrance_shop',
            'entrance_drop', 'entrance_dungeon', 'area', 'item', 'cave', 'drop',
            'dungeonchest', 'dungeonchest_nokey', 'dungeonkey', 'dungeonboss',
            'dungeonreward', 'dungeon', 'ganon')
        self.type = location['type']
        if (
                self.type not in ('area', 'interior') and
                not self.type.startswith('dungeon')):
            self.map = location['map']
            self.coord = location['coord']
        if self.type == 'dungeon':
            self.map = location['map']
            self.coord = location['coord']
            self.bossroad = location['bossroad']
        if self.type.startswith('dungeon') and len(self.type) > 7:
            self.dungeon = location['dungeon']
        if self.type == 'area' and 'dungeon' in location:
            self.dungeon = location['dungeon']
        self.link = location['link'].copy()
        self.visible = (
            location['visible'].copy() if 'visible' in location else {})
        if self.type not in ('area', 'interior'):
            self.checked = False
        else:
            self.checked = None


class Dungeon(dict):
    '''
    Dungeon object
    '''

    def keylocations(self) -> dict:
        '''
        Retrieve list oc locations possibly holding a small key.

        Returns:
            dict: {'location name': location object}
        '''

        ret = {}
        for loc in self:
            if self[loc].type  == 'dungeonchest':
                ret[loc] = self[loc]
        return ret
