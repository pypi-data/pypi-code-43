'''
Python Extensions for objects

History:
04-05-2018 - 1.0.0 - Stephen Funkhouser
    Created
'''
__version__ = '1.0.0'


class ObjectDict(dict):
    ''' Class to provide an object like interface for a dictionary
    while allowing it to still be used like a dictionary
    '''

    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError('No such attribute: ' + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError('No such attribute: ' + name)
