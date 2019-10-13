import os
import re

def get_root_path(anchor, path = os.getcwd(), prev = ""):
    if (path == prev):
        return None
    if (os.path.exists(os.path.join(path, anchor))):
        return path
    else:
        prev = path
        path = os.path.realpath(os.path.join(path, ".."))
        return get_root_path(anchor, path, prev)

def chdiranchor(anchor, path):
    """
    Changes the working directory to the directory that contains the anchor file
    plus the path specified as a regular expression.
    
    Parameters:

        anchor: file name which will be used as a reference to locate the root directory

        path: path to move to on top of the root directory

    Usage:
        
        from othertools.path import chdiranchor
        chdiranchor("environment.yaml", "src/.+")
        chdiranchor("environment.yaml", "src\.+")

    """
    path_elems = re.findall("[^\\\/]+", path)
    path_root = get_root_path(anchor)
    path_current = path_root
    for elem in path_elems:
        files = os.listdir(path_current)
        for file in files:
            if (bool(re.match(elem, file))):
                path_current = os.path.realpath(os.path.join(path_current, file))
                break
    os.chdir(path_current)
