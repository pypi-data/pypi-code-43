def load_ipython_extension(shell):
    with __import__('importnb').Notebook(): from . import jschema, ainteractive
    jschema.load_ipython_extension(shell)
    ainteractive.load_ipython_extension(shell)
def unload_ipython_extension(shell):
    with __import__('importnb').Notebook(): from . import jschema, ainteractive
    jschema.unload_ipython_extension(shell)
    ainteractive.unload_ipython_extension(shell)
    

with __import__('importnb').Notebook(): from . import articles