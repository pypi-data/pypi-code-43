'''
Entrance tracker
'''

from . import storage

__all__ = 'EntranceTracker',


class EntranceTracker(dict):
    '''
    Entrance tracker

    Instance variables:
        self: {'location': 'linked locations'}
        armed: True if entrance connection is armed
        worldtracker: world state tracker
    '''

    def __init__(self, worldtracker):
        '''
        Args:
            worldtracker: world state tracker
        '''

        super().__init__(storage.load_entrances())
        self.armed = False
        self.worldtracker = worldtracker

    def event(self, button: str) -> bool:
        '''
        Entrance connection event

        Connection happens in two steps: first it's armed, then it's connected.

        Args:
            button: name of location
        Returns:
            bool: True if new connection was made
        '''

        if ('retro' in self.worldtracker.settings and
            not 'entrance' in self.worldtracker.settings):
            return False
        if not self.armed:
            if button not in self:
                self.armed = button
            return False
        if button.replace(' (E)', ' (I)') in self.values():
            self.armed = False
            return False
        interior = button.replace(' (E)', ' (I)')
        self[self.armed] = interior
        self[interior] = self.armed
        self.armed = False
        self.save()
        return True

    def abort(self, button: str = None) -> bool:
        '''
        Abort or delete connection.

        Args:
            button: name of location
        '''

        if ('retro' in self.worldtracker.settings and
            not 'entrance' in self.worldtracker.settings):
            return False
        self.armed = False
        if button is not None and button in self:
            del self[self[button]]
            del self[button]
        self.save()

    def update(self) -> None:
        '''
        Update world tracker with new entrance information.
        '''

        self.worldtracker.ruleset.disconnect_entrances()
        for location in self:
            self.worldtracker.ruleset[location].link[self[location]] = []
            self.worldtracker.ruleset[self[location]].link[location] = []
        self.worldtracker.rulecheck()

    def reset(self) -> None:
        '''
        Remove all established connections.
        '''

        for loc in tuple(self.keys()):
            del self[loc]
        self.armed = False

    def find_remote(self, start: str) -> list:
        '''
        Find other interior conections.

        Args:
            start: starting entrance
        Returns:
            list: entrances connected via interiors
        '''

        if start not in self:
            return []
        reachable = [self[start]]
        done = {start}
        entrances = set()
        while reachable:
            loc = reachable.pop(0)
            done.add(loc)
            for link in self.worldtracker.ruleset[loc].link:
                if link in ('Ocarina', 'Pyramid', 'Castle Walls'):
                    continue
                if not self.worldtracker.ruleset[link].type.startswith(
                        'entrance') and link not in done:
                    reachable.append(link)
                elif self.worldtracker.ruleset[link].type.startswith(
                        'entrance') and link != start:
                    entrances.add(link)
        return entrances

    def save(self) -> None:
        '''
        Save current connections to file.
        '''

        storage.store_entrances(self)
