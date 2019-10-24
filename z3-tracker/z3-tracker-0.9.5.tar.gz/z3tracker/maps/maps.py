'''
Location tracker
'''

from . import storage

__all__ = 'LocationTracker',


class LocationTracker(dict):
    '''
    Location tracker
    '''

    def __init__(self):
        super().__init__(storage.load_locations())

    def save(self) -> None:
        '''
        Save current location states.
        '''

        storage.store_locations(self)

    def reset(self) -> None:
        '''
        Reset tracker.
        '''

        for loc in self:
            if isinstance(self[loc], list):
                self[loc] = [True, True]
            else:
                self[loc] = True
