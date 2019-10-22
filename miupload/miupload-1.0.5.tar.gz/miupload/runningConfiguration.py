'''

This is a module with persistent attributes

the attributes of this module are spread all over all instances of this module

To set attributes:
    import runningConfiguration
    runningConfiguration.x = y


to get attributes:
    runningConfiguration.x


Source: https://gist.github.com/niccokunzmann/5262590
'''

import os

import types


fn = fileName = fileName = os.path.splitext(__file__)[0] + '.conf'

try:
    FileNotFoundError

except NameError:

    FileNotFoundError = OSError


class RunningConfiguration(types.ModuleType):
    fileName = fn

    def __init__(self, *args, **kw):

        types.ModuleType.__init__(self, *args, **kw)

        import sys

        sys.modules[__name__] = self

        self.load()

    def save(self):

        import pickle

        pickle.dump(self.__dict__, open(self.fileName, 'wb'))

    def load(self):

        import pickle

        try:

            dict = pickle.load(open(self.fileName, 'rb'))

        except (EOFError, FileNotFoundError):

            pass

        except:

            import traceback

            traceback.print_exc()

        else:

            self.__dict__.update(dict)

    def __setattr__(self, name, value):

        ##        print 'set', name, value,

        l = []

        v1 = self.__dict__.get(name, l)

        self.__dict__[name] = value

        try:

            self.save()

        ##            print 'ok'

        except:

            if v1 is not l:
                self.__dict__[name] = v1

            raise

    def __getattribute__(self, name):

        import types

        if name in ('__dict__', '__class__', 'save', 'load', '__setattr__', \
 \
                    '__delattr__', 'fileName'):
            return types.ModuleType.__getattribute__(self, name)

        ##        print 'get', name

        self.load()

        l = []

        ret = self.__dict__.get(name, l)

        if ret is l:

            if hasattr(self.__class__, name):
                return getattr(self.__class__, name)

            if name in globals():
                return globals()[name]

            raise AttributeError('%s object has no attribute %r' % \
 \
                                 (self.__class__.__name__, name))

        return ret

    def __delattr__(self, name):

        del self.__dict__[name]

        self.save()


RunningConfiguration(__name__)
