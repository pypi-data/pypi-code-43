import time
import importlib
import subprocess
import sys


def getthat(module, name, pypi_pack=None):

    try:
        mdl = importlib.import_module(module)
        cls = getattr(mdl, name)
        return cls
    except ModuleNotFoundError:

        if pypi_pack is not None:
            pack = pypi_pack
        else:
            pack = module.split(".")[0]
        sys.stdout = sys.__stderr__
        subprocess.call(
            ["pip3", "install", "--upgrade", pack],
            stdout=subprocess.DEVNULL,
        )
        sys.stdout = sys.__stdout__

        try:
            mdl = importlib.import_module(module)
            cls = getattr(mdl, name)
            return cls
        except Exception as e:
            raise e
