'''
World state tracker
'''

import typing

from ..config import CONFIG
from ..dungeons import lists as dungeonlists
from .. import entrances
from .. import maps
from .. import ruleset

__all__ = 'Tracker',


class _DelayCheck(Exception):
    '''
    Thrown by Tracker.parse_requirement() when a check should be delayed.
    '''

    def __init__(self, delayclass: str):
        '''
        Args:
            delayclass: 'common', 'smallkey', 'bigkey', 'reward', 'boss'
        '''

        super().__init__()
        assert delayclass in (
            'common', 'smallkey', 'bigkey', 'reward', 'maybe', 'boss')
        self.delayclass = delayclass

class _SmallKeyCheck(Exception):
    '''
    Raised when small key door is encountered.
    '''

    def __init__(self, dungeon: str, requirement: int):
        '''
        Args:
            requirement: number of required key chests
        '''

        super().__init__()
        self.dungeon = dungeon
        self.required = requirement


class _BigKeyCheck(Exception):
    '''
    Raised when big key lock is encountered.
    '''

    def __init__(self, dungeon):
        '''
        Args:
            requirement: number of required key chests
        '''

        super().__init__()
        self.dungeon = dungeon


class _RewardCheck(Exception):
    '''
    Raised when reward is required.
    '''


class Tracker(object):
    '''
    World state tracker

    Instance variables:
        items: item inventory
        dungeons: dungeon state
        maps: {'light', 'dark'} world map displays
        locationtracker: location tracker
        ruleset: location rules
        settings: game settings
        startpoint: starting locations
        entrances: entrance tracker
        crystals: crystal requirements for {'tower', 'ganon'}
        keys = {'dungeon': {'small': int, 'big': bool}}
    '''

    def __init__(self):
        self.items = {}
        self.dungeons = {}
        self.maps = {'light': None, 'dark': None}
        self.locationtracker = maps.LocationTracker()
        self.entrances = entrances.EntranceTracker(self)
        self.crystals = {'tower': -1, 'ganon': -1}
        self.keys = {}
        self.update_rules()

    def update_rules(self) -> None:
        '''
        Retrieve location rules.
        '''

        self.ruleset = ruleset.Ruleset()
        self._make_settings()
        for dungeon in self.ruleset.dungeons:
            self.keys[dungeon] = {'small': 0, 'big': False}
        self.rulecheck()

    def _make_settings(self) -> None:
        '''
        Build game settings.
        '''

        self.settings = set()
        if CONFIG['entrance_randomiser']:
            self.settings.add('entrance')
        self.settings.add(CONFIG['world_state'].lower())
        self.settings.add('glitches_{0:s}'.format(
            {'None': 'none', 'Overworld Glitches': 'overworld',
             'Major Glitches': 'major'}[CONFIG['glitch_mode']]))
        self.settings.add('placement_{0:s}'.format(
            CONFIG['item_placement'].lower()))
        if CONFIG['dungeon_items'] in (
                'Maps/Compasses', 'Maps/Compasses/Small Keys', 'Keysanity'):
            self.settings.update(('random_map', 'random_compass'))
        if CONFIG['dungeon_items'] in (
                'Maps/Compasses/Small Keys', 'Keysanity'):
            self.settings.add('random_smallkey')
        if CONFIG['dungeon_items'] == 'Keysanity':
            self.settings.add('random_bigkey')
        self.settings.add('goal_{0:s}'.format(
            {'Defeat Ganon': 'ganon', 'Fast Ganon': 'fastganon',
             'All Dungeons': 'dungeons', 'Master Sword Pedestal': 'pedestal',
             'Triforce Hunt': 'triforce'}[CONFIG['goal']]))
        if CONFIG['swords'] == 'Swordless':
            self.settings.add('swordless')
        self._set_startpoint()

    def _set_startpoint(self) -> None:
        '''
        Choose starting point.
        '''

        self.startpoint = ["Link's House"]
        if 'inverted' in self.settings:
            self.startpoint.append('Dark Chapel Entrance (I)')
        else:
            self.startpoint.append('Sanctuary')

    def reapply(self) -> None:
        '''
        Purge map and recreate with (possibly) updated settings.
        '''

        self.update_rules()
        for maptype in self.maps:
            self.maps[maptype].remove_buttons()
            self.make_buttons(maptype)
        if 'entrance' in self.settings:
            self.ruleset.disconnect_entrances()
            self.maps['light'].set_entrance()
        else:
            self.ruleset = ruleset.Ruleset()
        self.rulecheck()

    def set_item(self, itemname: str, itemnumber: int) -> None:
        '''
        Set item inventory.

        Args:
            itemname: item identifier
            inventory: new item inventory to overwrite old one
        '''

        self.items[itemname] = itemnumber
        self.rulecheck()

    def set_dungeon(self, dungeonname: str, dungeondata: dict) -> None:
        '''
        Set dungeon data.

        Args:
            dungeonname: dungeon name
            dungeondata: new dungeon data
        '''

        self.dungeons[dungeonname] = dungeondata
        self.rulecheck()

    def add_map(self, maptype: str, mapdisplay) -> None:
        '''
        Add map to tracker.

        Args:
            maptype: 'light' or 'dark'
            mapdisplay: map display object
        '''

        assert maptype in ('light', 'dark')
        self.maps[maptype] = mapdisplay
        self.maps[maptype].add_location_tracker(self.locationtracker)
        if all(m is not None for m in self.maps.values()):
            self.maps['light'].other = self.maps['dark']
            self.maps['dark'].other = self.maps['light']
        self.make_buttons(maptype)
        if 'entrance' in self.settings:
            self.ruleset.disconnect_entrances()
            if self.maps['light'] and self.maps['dark']:
                self.maps['light'].set_entrance()
        self.maps[maptype].add_entrance_tracker(self.entrances)
        self.rulecheck()

    def make_buttons(self, maptype: str) -> None:
        '''
        Send button data to map display.

        Args:
            maptype: 'light' or 'dark'
        '''

        assert maptype in ('light', 'dark')
        if CONFIG['entrance_randomiser']:
            gametype = 'entrance'
        elif CONFIG['world_state'] == 'Retro':
            gametype = 'item_retro'
        else:
            gametype = 'item'
        self.maps[maptype].place_buttons(
            self.ruleset.locations(gametype, maptype))

    def update_buttons(self, available: typing.Mapping,
                       visible: typing.Sequence[str]) -> None:
        '''
        Send updated availability info to map displays.

        Args:
            available: {'available location': 'type of availability'}
            visible: list of visible locations
        '''

        # Go through maps.
        for mapd in self.maps.values():

            # Go through buttons:
            for button in mapd.button:

                # Check dungeon status.
                if mapd.button[button]['type'] == 'dungeon':
                    dungeonchecks = []
                    for loc in self.ruleset.dungeons[button]:
                        if self.ruleset[loc].type != 'area':
                            dungeonchecks.append(loc in available)
                    if all(dungeonchecks):
                        try:
                            clearable = available[
                                '{0:s} Boss'.format(button)]
                        except KeyError:
                            clearable = available[
                                '{0:s} Entrance (I)'.format(button)]
                            if (clearable == 'available' and
                                not self._check_dungeon_state(button)):
                                clearable = 'indirect'
                    elif any(dungeonchecks):
                        clearable = 'visible'
                    else:
                        clearable = 'unavailable'
                    if not self._check_bossfight(button):
                        finishable = 'unavailable'
                    elif '{0:s} Boss'.format(button) in available:
                        finishable = available['{0:s} Boss'.format(button)]
                        if (finishable == 'available' and
                            clearable == 'indirect'):
                            finishable = 'indirect'
                    elif self.ruleset[button].bossroad in available:
                        finishable = 'visible'
                    else:
                        finishable = 'unavailable'
                    state = [clearable, finishable]
                    mapd.set_dungeon_availability(button, state)

                # Check location status.
                else:
                    if button in available:
                        state = available[button]
                    elif button in visible:
                        state = 'visible'
                    else:
                        state = 'unavailable'
                    mapd.set_availability(button, state)

    def rulecheck(self) -> None:
        '''
        Update availability of all locations.
        '''

        # Don't run if both maps aren't yet available.
        if not all(self.maps.values()):
            return

        # Create fresh rules.
        for loc in self.ruleset.values():
            loc.checked = False
        keys = {}
        for dungeon in self.ruleset.dungeons:
            if self.ruleset[dungeon].type == 'dungeon':
                keys[dungeon] = {'small': self.keys[dungeon]['small'],
                                 'big': self.keys[dungeon]['big']}
            else:
                keys[dungeon] = {'small': 1, 'big': False}

        # Prepare rulecheck.
        available = {}
        reachable = [_Connection(s) for s in self.startpoint]
        visible = set()
        delayed = {'common': [], 'smallkey': [], 'bigkey': [], 'boss': [],
                   'reward': [], 'maybe': []}

        # Go through locations.
        while reachable:

            # Retrieve next available location.
            current, state = reachable.pop(0).get()

            # Mark current location.
            if self.ruleset[current].checked is not None:
                if 'maybe' in state:
                    available[current] = 'maybe'
                elif 'boss' in state:
                    available[current] = 'indirect'
                else:
                    available[current] = 'available'
            self.ruleset[current].checked = True

            # Add fixed keys.
            if self.ruleset[current].type == 'dungeonkey':
                keys[self.ruleset[current].dungeon]['small'] += 1

            # Go through links.
            for link in self.ruleset[current].link:

                # Don't recheck already visited locations.
                if self.ruleset[link].checked:
                    continue

                # Parse requirement.
                newstate = state.copy()
                try:
                    ret, addstate = self._parse_requirement(
                        self.ruleset[current].link[link], state, None, keys)
                except _DelayCheck as err:
                    delayed[err.delayclass].append(
                        (link,
                         _Connection(self.ruleset[current].link[link], state)))
                    ret = False
                if ret:
                    for retstate in addstate:
                        s = retstate.split(';')
                        if len(s) > 1 and s[1] == 'add':
                            newstate.add(s[0])
                        elif s[0] in newstate:
                            newstate.remove(s[0])
                        elif not (len(s) > 1 and s[1] == 'dis'):
                            newstate.add(s[0])
                    reachable.append(_Connection(link, newstate))

            # Check visible locations.
            for link in self.ruleset[current].visible:
                if self._parse_requirement(
                        self.ruleset[current].visible[link], state, None,
                        keys)[0]:
                    visible.add(link)

            # Go though delayed checks.
            ret = False
            addstate = []
            if not reachable:
                for delayclass in delayed:
                    for idx, loc in enumerate(delayed[delayclass]):
                        current, state = loc[1].get()
                        newstate = state.copy()
                        try:
                            ret, addstate = self._parse_requirement(
                                current, state, available, keys)
                        except _SmallKeyCheck as err:
                            ret = self._check_smallkeys(
                                available, err.dungeon, err.required)
                        except _BigKeyCheck as err:
                            ret = self._check_bigkey(available, err.dungeon)
                        if ret:
                            for retstate in addstate:
                                s = retstate.split(';')
                                if len(s) > 1 and s[1] == 'add':
                                    newstate.add(s[0])
                                elif s[0] in state:
                                    newstate.remove(s[0])
                                elif not (len(s) > 1 and s[1] == 'dis'):
                                    newstate.add(s[0])
                            reachable.append(_Connection(
                                delayed[delayclass].pop(idx)[0], newstate))
                            break
                    if reachable:
                        break

        # Send updated availability to map displays.
        self.update_buttons(available, visible)

    def _parse_requirement(
            self, req: typing.Sequence[typing.Sequence], state: typing.Sequence,
            nodelay: typing.Sequence[str], keys: dict = {},
            collector=any) -> (bool, list):
        '''
        Parse generic link requirement object.

        Args:
            req: [('requirement type', requirement object)]
            state: current connection state
            nodelay: don't throw DelayCheck when encountering access
               requirement, instead check against this list of locations
            keys: current number of available keys
            collector: something like any() or all()
        Returns:
            bool: True if requirements are met
            list: list of state flags to toggle
        '''

        if not req:
            return True, []
        result = []
        addstate = []

        for rtype, robj in req:

            # OR
            if rtype == 'or':
                sub = self._parse_requirement(robj, state, nodelay, keys)
                result.append(sub[0])
                if sub[0]:
                    addstate.extend(sub[1])

            # AND
            elif rtype == 'and':
                sub = self._parse_requirement(robj, state, nodelay, keys, all)
                result.append(sub[0])
                if sub[0]:
                    addstate.extend(sub[1])

            # settings
            elif rtype == 'settings':
                result.append(robj in self.settings)

            # nosettings
            elif rtype == 'nosettings':
                result.append(robj not in self.settings)

            # item
            elif rtype == 'item':
                rabbititems = (
                    'mushroom', 'lantern', 'mudora', 'bottle', 'mirror')
                if ('rabbit' in state and (
                        not 'pearl' in self.items or self.items['pearl'] == 0)
                    and robj not in rabbititems):
                    result.append(False)
                else:
                    result.append(robj in self.items and self.items[robj] > 0)
                    if robj == 'mirror':
                        addstate.append('rabbit;dis')

            # access
            elif rtype == 'access':
                if not nodelay:
                    raise _DelayCheck('common')
                result.append(robj in nodelay)
                if result[-1] and nodelay[robj] in ('maybe', 'boss'):
                    addstate.append('{0:s};add'.format(nodelay[robj]))

            # glitch
            elif rtype == 'glitch':
                if robj == 'overworld':
                    result.append('glitches_overworld' in self.settings or
                                  'glitches_major' in self.settings)
                elif robj == 'major':
                    result.append('glitches_major' in self.settings)

            # medallion
            elif rtype == 'medallion':
                if 'rabbit' in state and not 'pearl' in self.items:
                    result.append(False)
                res, maybe = self._check_medallion(robj)
                result.append(res)
                if maybe:
                    addstate.append('maybe;add')

            # mudora
            elif rtype == 'mudora':
                assert robj in ('take', 'see')
                result.append(
                    'mudora' in self.items and self.items['mudora'] > 0 and
                    (('swordless' in self.settings and
                      'hammer' in self.items and self.items['hammer'] > 0) or
                     'mastersword' in self.items and
                     self.items['mastersword'] > 0))

            # pendant/crystals
            elif rtype in ('pendant', 'crystals'):
                if not nodelay:
                    raise _DelayCheck('reward')
                res, flag = self._reward_locations(robj, nodelay)
                result.append(res)
                if flag:
                    addstate.append('{0:s};add'.format(flag))

            # smallkey
            elif rtype == 'smallkey':
                if 'retro' in self.settings:
                    result.append(True)
                elif not nodelay:
                    raise _DelayCheck('smallkey')
                else:
                    if 'random_smallkey' in self.settings:
                        if keys[robj[0]]['small'] > 0:
                            keys[robj[0]]['small'] -= 1
                            result.append(True)
                        else:
                            result.append(False)
                    else:
                        raise _SmallKeyCheck(*robj)

            # bigkey
            elif rtype == 'bigkey':
                if not nodelay:
                    raise _DelayCheck('bigkey')
                else:
                    if 'random_bigkey' in self.settings:
                        if keys[robj]['big']:
                            result.append(True)
                        else:
                            result.append(False)
                    else:
                        raise _BigKeyCheck(robj)

            # macro
            elif rtype == 'macro':
                if robj == 'ganon':
                    if 'goal_ganon' in self.settings:
                        sub = self._parse_requirement(
                                [('crystals', 'ganon'),
                                 ('access', "Ganon's Tower Reward")],
                                state, nodelay, keys, all)
                    elif 'goal_fastganon' in self.settings:
                        sub = self._parse_requirement(
                                [('crystals', 'ganon')], state, nodelay, keys)
                    elif 'goal_dungeons' in self.settings:
                        sub = self._parse_requirement(
                                [('crystals', 'ganon'), ('pendant', 'courage'),
                                 ('pendant', 'power'), ('pendant', 'wisdom')],
                                state, nodelay, keys, all)
                    elif 'goal_pedestal' in self.settings:
                        sub = self._parse_requirement(
                                [('pendant', 'courage'), ('pendant', 'power'),
                                 ('pendant', 'wisdom')],
                                state, nodelay, keys, all)
                    elif 'goal_triforce' in self.settings:
                        sub = self._parse_requirement(
                                [('crystals', 'ganon'), ('pendant', 'courage'),
                                 ('pendant', 'power'), ('pendant', 'wisdom')],
                                state, nodelay, keys, all)
                    else:
                        assert False
                elif robj == 'ganonstower':
                    sub = self._parse_requirement(
                        [('crystals', 'ganonstower')], state, nodelay, keys)
                else:
                    print(rtype, robj)
                    assert False
                result.append(sub[0])
                if sub[0]:
                    addstate.extend(sub[1])

            # state
            elif rtype == 'state':
                statestr = robj.split(';')
                assert statestr[0] in ('rabbit', 'maybe')
                if statestr[0] == 'maybe' and not nodelay:
                    raise _DelayCheck('maybe')
                addstate.append(statestr[0])
                result.append(True)

            # rabbitbarrier
            elif rtype == 'rabbitbarrier':
                if 'rabbit' in state and not self._parse_requirement(
                        [('item', 'pearl')], state, nodelay)[0]:
                    result.append(False)
                else:
                    result.append(True)

            # boss
            elif rtype == 'boss':
                if not nodelay:
                    raise _DelayCheck('boss')
                if not self._check_dungeon_state(robj):
                    addstate.append('boss;add')
                result.append(True)

            # error
            else:
                print(rtype, robj)
                assert False

        return collector(result), addstate

    def _check_smallkeys(
            self, availability: typing.Sequence[str], dungeon: str,
            requirement: int) -> bool:
        '''
        Check number of available small keys.

        Args:
            availability: list of already available locations
            dungeon: dungeon name
            requirement: number of required key chests
        Returns:
            bool: True if key requirement is met
        '''

        keychests = 0
        for loc in self.ruleset.dungeons[dungeon].keylocations():
            if loc in availability:
                keychests += 1
        if keychests < requirement:
            return False
        return True

    def _check_bigkey(
            self, availability: typing.Sequence[str], dungeon: str) -> bool:
        '''
        Check number of available small keys.

        Args:
            availability: list of already available locations
            dungeon: dungeon name
        Returns:
            bool: True if key requirement is met
        '''

        return self._check_smallkeys(
            availability, dungeon,
            len(self.ruleset.dungeons[dungeon].keylocations()))

    def _check_bossfight(self, dungeon: str) -> bool:
        '''
        Check whether a bossfight can be finished with current equipment.

        Args:
            dungeon: name of dungeon
        Returns:
            bool: True if fight is finishable
        '''

        requirement = self.ruleset[
            '{0:s} Boss'.format(dungeon)].link[
                '{0:s} Boss Item'.format(dungeon)]
        return self._parse_requirement(requirement, [], None)

    def _check_medallion(self, dungeon) -> (bool, bool):
        '''
        Check whether medallion requirement is sattisfied.

        Args:
            dungeon: 'Misery Mire' or 'Turtle Rock'
        Returns:
            bool: True if fight is finishable
            bool: True if 'maybe' state should be added
        '''

        assert dungeon in ('Misery Mire', 'Turtle Rock')
        req = self.dungeons[dungeon]['medallion']
        if req == 'unknown':
            res = (self.items['bombos'] > 0, self.items['ether'] > 0,
                   self.items['quake'] > 0)
            if all(res):
                res = True, False
            elif any(res):
                res = True, True
            else:
                res = False, False
        else:
            res = self.items[req] > 0, False
        if not 'swordless' in self.settings and self.items['sword'] == 0:
            res = False, False
        return res

    def _reward_locations(
            self, reward: str, available: typing.Sequence[str]) -> (bool, str):
        '''
        Retrieve required locations for reward.

        Args:
            reward: 'courage', 'power', 'wisdom', 'fairy', 'ganonstower',
                'ganon'
            available: list of available locations
        Returns:
            bool: True if all required locations are available
            str: '', 'maybe' or 'boss'
        '''

        assert reward in (
            'courage', 'power', 'wisdom', 'fairy', 'ganonstower', 'ganon')
        conversion = {
            'courage': 'courage', 'power': 'powerwisdom',
            'wisdom': 'powerwisdom', 'fairy': '56crystal',
            'ganonstower': 'crystal', 'ganon': 'crystal'}
        rewarddungeons = []
        for dungeon in self.dungeons:
            if not 'reward' in self.dungeons[dungeon]['features']:
                continue
            if self.dungeons[dungeon]['reward'] == conversion[reward]:
                rewarddungeons.append(dungeon)
            if (reward.startswith('ganon') and
                self.dungeons[dungeon]['reward'] == '56crystal'):
                rewarddungeons.append(dungeon)
        required = {
            'courage': 1, 'power': 2, 'wisdom': 2, 'fairy': 2,
            'ganonstower': self.crystals['tower'],
            'ganon': self.crystals['ganon']}
        if required[reward] < 0:
            unknown_number = True
        else:
            unknown_number = False
        total = dict.fromkeys(
            ('courage', 'powerwisdom', '56crystal', 'crystal'), 0)
        for dungeon in self.dungeons:
            if self.dungeons[dungeon]['reward'] != 'unknown':
                total[self.dungeons[dungeon]['reward']] += 1
                if self.dungeons[dungeon]['reward'] == '56crystal':
                    total['crystal'] += 1
        enough = len(rewarddungeons) >= required[reward]
        if not enough:
            rewarddungeons = []
            for dungeon in self.dungeons:
                if not 'reward' in self.dungeons[dungeon]['features']:
                    continue
                if self.dungeons[dungeon]['reward'] in (
                        conversion[reward], 'unknown'):
                    rewarddungeons.append(dungeon)
                if (reward.startswith('ganon') and
                    self.dungeons[dungeon]['reward'] == '56crystal'):
                    rewarddungeons.append(dungeon)
        locations = []
        maybes = 0
        boss_required = 0
        for dungeon in rewarddungeons:
            res, add = self._parse_requirement(
                [('access', '{0:s} Reward'.format(dungeon))], [], available)
            locations.append(res)
            for retstate in add:
                if retstate.split(';')[0] == 'maybe':
                    maybes += 1
                    break
            if not self._check_dungeon_state(dungeon):
                boss_required += 1
        addflag = ''
        if enough:
            ret = sum(locations) >= required[reward]
            if required[reward] + boss_required > total[conversion[reward]]:
                addflag = 'boss'
            if required[reward] + maybes > total[conversion[reward]]:
                addflag = 'maybe'
            if sum(locations) < total[conversion[reward]] and unknown_number:
                addflag = 'maybe'
        else:
            ret = all(locations)
            if not ret:
                ret = unknown_number
                addflag = 'maybe'
        return ret, addflag

    def total_chests(self, dungeon: str) -> int:
        '''
        Retrieve number of chests available in dungeon.

        Args:
            dungeon: name of dungeon
        Returns:
            int: number of non-dungeon-specific items
        '''

        total_chests = 0
        for loc in self.ruleset.dungeons[dungeon].values():
            if loc.type.startswith('dungeonchest'):
                total_chests += 1
        return total_chests

    def set_dungeon_state(self, dungeon: str, state: [bool, bool]) -> None:
        '''
        Set whether dungeon has been checked or not.

        Args:
            dungeon: name of dungeon
            state: (all items collected, boss defeated)
        '''

        assert isinstance(state, list)
        assert len(state) == 2
        if dungeon in self.maps['light'].button:
            mapd = 'light'
        else:
            mapd = 'dark'
        self.maps[mapd].tracker[dungeon] = state
        self.rulecheck()

    def _check_dungeon_state(self, dungeon: str) -> bool:
        '''
        Check whether dungeon reward has been collected or not.

        Args:
            dungeon: name of dungeon
        Returns:
            bool: True if dungeon reward has been picked up
        '''

        try:
            ret = self.maps['dark'].tracker[dungeon][1]
        except KeyError:
            ret = self.maps['light'].tracker[dungeon][1]
        return not ret

    def set_crystal_requirement(self, tower: int, ganon: int) -> None:
        '''
        Set crystal requirements for Tower and Ganon Fight access.

        Args:
            tower: crystals required for Ganon's Tower access
            ganon: crystals required for the Ganon Fight
        '''

        self.crystals['tower'] = tower
        self.crystals['ganon'] = ganon
        self.rulecheck()


class _Connection(object):
    '''
    Connected location

    Instance variables:
        name: name of connected location
        state: list of states linked to connection
    '''

    def __init__(self, init: str = '', state: typing.Sequence = set()):
        '''
        Args:
            init: name of connected location
            state: list of states linked to connection
        '''

        super().__init__()
        self.name = init
        self.state = state

    def get(self) -> (str, tuple):
        '''
        Unpack data.

        Returns:
            str: name of connected location
            state: list of states linked to connection
        '''

        return self.name, self.state
