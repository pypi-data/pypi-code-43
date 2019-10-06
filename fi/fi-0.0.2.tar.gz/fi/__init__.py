import sys


class _fi(sys.modules[__name__].__class__):
    def __call__(self, *args, **kwargs):
        print('hello world!')

# make module callable
sys.modules[__name__].__class__ = _fi
