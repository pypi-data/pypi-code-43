"""
# Readers

Contains utils functions to parse args from docopt (not always in the right format), to check if directories exist, to convert strings to int/float etc.
"""
import os
import logging

logger = logging.getLogger("preprocessor")


def readArgs(args):
    """Reads and correct docopt parsed arguments from the command-line interface.
    For instance, int, floats, booleans need to be converted back to their
    type.

    Args:
        args : dic
            docopt generated argument dictionnary
    Returns:
        params : dic
            the dictionnary of corrected arguments
    """
    params = {}
    for k in args.keys():
        k2 = k.replace("<", "").replace(">", "").replace("-", "")
        try:  # Convert strings to int or floats when required
            params[k2] = int(args[k])
        except:
            try:
                params[k2] = float(args[k])
            except:
                try:
                    params[k2] = str2bool(args[k])
                except:
                    params[k2] = args[k]
    return params


def str2bool(s):
    """Helps to convert a string representing a boolean into the boolean
    Args:
        s : str
    Returns:
        b : boolean
    """
    if s == "True":
        return True
    elif s == "False":
        return False
    else:
        raise ValueError


def checkExistenceDir(path):
    """Checks if a given path is the path of a directory, and if not, creates
    the directory.
    Args:
        path : str
            A string representing a path
    """
    path = os.path.abspath(path)
    if not os.path.isdir(path):
        logger.warning(
            "Directory {} does not seem to exist, creating one.".format(path)
        )
        os.mkdir(path)


def checkExistenceFile(path):
    """Checks if a given path is the path of a directory.
    Args:
        path : str
            A string representing a path
    """
    path = os.path.abspath(path)
    return os.path.isfile(path)


def openFile(filepath):
    """Read lines of a txt file in 'filepath' and returns a string
    Args:
        path : str
            A string representing a path
    Returns:
        text : str
            The text string
    """
    assert checkExistenceFile(filepath), "filepath does not exist"
    with open(filepath, "r", encoding="utf-8") as f:
        text = " ".join(map(lambda x: x.rstrip("\n"), f.readlines()))
    return text


def convertInt(s):
    """Tells if a string can be converted to int and converts it
    Args:
        s : str
    Returns:
        s : str
            Standardized token 'INT' if s can be turned to an int, s otherwise
    """
    try:
        int(s)
        return "INT"
    except:
        return s


def convertFloat(s):
    """Tells if a string can be converted to float and converts it
    Args:
        s : str
    Returns:
        s : str
            Standardized token 'FLOAT' if s can be turned to an float, s
            otherwise"""
    try:
        float(s)
        return "FLOAT"
    except:
        return s
