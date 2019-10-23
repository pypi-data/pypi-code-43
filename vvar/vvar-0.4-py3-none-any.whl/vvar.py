from pathlib import Path
import platform
import os

def _get_path():
    location = str(Path.home())
    if platform.system() == "Linux":
        location += "/.vvar/"
    else:
        location += "\\.vvar\\"
    try:
        os.makedirs(location)
    except:
        pass
    return location

class VVarEnvironment():

    def __getattribute__(self, name):
        content = ""
        try:
            with open(_get_path() + name, "r") as f:
                content = f.read()
        except:
            raise AttributeError(name)
        return content
    
    def __setattr__(self, name, value):
        with open(_get_path() + name, "w") as f:
            f.write(value)

    def __delattr__(self, name):
        try:
            os.remove(_get_path() + name)
        except:
            raise AttributeError(name)

env = VVarEnvironment()

