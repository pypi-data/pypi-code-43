import os
from mcutk.debugger import jlink
from mcutk.debugger import pyocd
from mcutk.debugger import redlink
from mcutk.debugger import ide
from mcutk.debugger import blhost

__all__ = ["getdebugger", 'jlink', 'pyocd', 'redlink']



def getdebugger(type, *args, **kwargs):
    """Return debugger instance."""
    supported = {
        "jlink": jlink.JLINK,
        "pyocd": pyocd.PYOCD,
        "redlink": redlink.RedLink,
        'ide': ide.IDE,
        'blhost': blhost.Blhost
    }
    try:
        return supported[type](*args, **kwargs)
    except KeyError:
        raise ValueError("not supported debugger: %s"%type)

