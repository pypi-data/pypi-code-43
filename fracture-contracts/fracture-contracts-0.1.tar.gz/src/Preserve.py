from .Contract import *

def passPreservers(inner, func):
    setattr(inner, PRESERVER_ATTRIBUTE, getattr(func, PRESERVER_ATTRIBUTE, []))

class preserve(Contract):
    def __init__(self, preserver):
        super().__init__(lambda : True)
        self.preserver = preserver

    def __call__(self, func):
        inner = super().__call__(func)
        if not hasattr(func, PRESERVER_ATTRIBUTE):
            setattr(func, PRESERVER_ATTRIBUTE, [])
        getattr(func, PRESERVER_ATTRIBUTE).append(self.preserver)
        passPreservers(inner, func)
        return inner