'''
Single dungeon tracker
'''

import typing

from ..config.images import image

__all__ = 'DungeonObj',


class DungeonObj(object):
    '''
    Dungeon object

    Instance variables:
        identifier: name of dungeon
        location: (column, row) on dungeon display
        totalkeys: total number of small keys available for this dungeon
        icon: name of dungeon image
        features: additional features of dungeon
        tracker: world state tracker
        smallkeys: number of collected small keys
        bigkey: whether big key is collected or not
        chests: number of collected chests
        reward: dungeon reward
        completed: True if dungeon has been completed
        medallion: medallion requirement
    '''

    import_data = (
        'smallkeys', 'bigkey', 'chests', 'reward', 'completed', 'medallion')

    def __init__(self, name: str, location: (int, int), totalkeys: int,
                 icon: str, features: typing.Sequence[str], tracker):
        '''
        Args:
            name: name of dungeon
            location: (column, row) on dungeon display
            totalkeys: total number of randomly placed small keys
            icon: icon image of dungeon
            features: list of features of dungeon
            tracker: world state tracker
        '''

        self.identifier = name
        self.location = location
        self.totalkeys = totalkeys
        self.icon = image(icon)
        self.features = features
        self.tracker = tracker
        self.reset()

    def reset(self) -> None:
        '''
        Reset all values to default.
        '''

        self.smallkeys = 0
        self.bigkey = False
        self.chests = 0
        self.reward = 'unknown'
        self.completed = False
        self.medallion = 'unknown'
        self.tracker.set_dungeon(self.identifier, self.export())

    def restore(self, data: dict) -> None:
        '''
        Rebuild dungeon info from save.

        Args:
            data: dungeon save data
        '''
        for attr in self.import_data:
            if attr in ('smallkeys', 'chests'):
                data[attr] = int(data[attr])
            self.set(attr, data[attr])

    def save(self) -> dict:
        '''
        Return non-static dungeon info.

        Returns:
            dict: dungeon save data
        '''

        data = {}
        for attr in self.import_data:
            data[attr] = self.get(attr)
        return data

    def export(self) -> dict:
        '''
        Retrieve dungeon info for world state tracker.

        Returns:
            dict: dungeon info
        '''

        data = self.save()
        data['features'] = self.features
        return data

    def set(self, variable: str, value) -> None:
        '''
        Set dungeon variable.

        Args:
            variable: name of dungeon variable to change
            value: value to set variable to
        '''

        self.__setattr__(variable, value)
        self.tracker.set_dungeon(self.identifier, self.export())

    def get(self, variable: str) -> object:
        '''
        Get dungeon variable.

        Args:
            variable: name of dungeon variable
        Returns:
            object: current value of variable
        '''

        return self.__getattribute__(variable)

    def total_items(self) -> int:
        '''
        Retrieve number of items available in dungeon.

        Returns:
            int: number of non-dungeon-specific items
        '''

        total_chests = self.tracker.total_chests(self.identifier)
        if 'random_map' not in self.tracker.settings and 'map' in self.features:
            total_chests -= 1
        if ('random_compass' not in self.tracker.settings and
            'compass' in self.features):
            total_chests -= 1
        if ('random_bigkey' not in self.tracker.settings and
            'bigkey' in self.features):
            total_chests -= 1
        if ('random_smallkey' not in self.tracker.settings and
            'retro' not in self.tracker.settings):
            total_chests -= self.totalkeys
        return total_chests

    def remaining(self) -> int:
        '''
        Retrieve number of remaining items in dungeon.

        Returns:
            int: number of remaining items
        '''

        return self.total_items() - self.chests

    def cycle_reward(self, direction: bool) -> None:
        '''
        Cycle through dungeon reward.

        Args:
            direction: cycling direction
        '''

        circle = ('unknown', 'courage', 'powerwisdom', 'crystal', '56crystal')
        newidx = circle.index(self.reward)
        newidx += 1 if direction else -1
        if newidx >= len(circle):
            newidx = 0
        self.set('reward', circle[newidx])

    def mark_complete(self, complete: bool) -> None:
        '''
        Mark dungeon as (in)complete.

        Args:
            complete: False if dungeon is to be marked as completed
        '''

        self.set('completed', complete)
        self.tracker.set_dungeon_state(
            self.identifier, [bool(self.remaining()), not complete])

    def cycle_medallion(self, direction) -> None:
        '''
        Cycle through medallion requirement.

        Args:
            direction: cycling direction
        '''

        circle = ('unknown', 'bombos', 'ether', 'quake')
        newidx = circle.index(self.medallion)
        newidx += 1 if direction else -1
        if newidx >= len(circle):
            newidx = 0
        self.set('medallion', circle[newidx])

    def toggle_bigkey(self, *args) -> None:
        '''
        Toggle possession of the Big Key.
        '''

        self.tracker.keys[self.identifier]['big'] = not self.bigkey
        self.set('bigkey', not self.bigkey)

    def key_up(self, *args) -> None:
        '''
        Add one small key.
        '''

        before = self.get('smallkeys')
        after = min(self.smallkeys + 1, self.totalkeys)
        self.tracker.keys[self.identifier]['small'] += (after - before)
        self.set('smallkeys', after)

    def key_down(self, *args) -> None:
        '''
        Remove one small key.
        '''

        before = self.get('smallkeys')
        after = max(self.smallkeys - 1, 0)
        self.tracker.keys[self.identifier]['small'] += (after - before)
        self.set('smallkeys', after)

    def item_up(self, *args) -> None:
        '''
        Add one collected item.
        '''

        self.set('chests', min(self.chests + 1, self.total_items()))
        self.tracker.set_dungeon_state(
            self.identifier, [bool(self.remaining()), not self.completed])

    def item_down(self, *args) -> None:
        '''
        Remove one collected item.
        '''

        self.set('chests', max(self.chests - 1, 0))
        self.tracker.set_dungeon_state(
            self.identifier, [bool(self.remaining()), not self.completed])
