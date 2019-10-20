import os

from ctypes import *

def find_file(name, path):
    """Search for file within specific dir and any child dirs.
    Args:
    name (str): Filename to be searched for.
    path (str): Dir path to search for file.
    Returns:
    str: Full path of found file (if found).
    bool: If file not found, returns false.
    """
    for root, _, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)
    return False

lib = cdll.LoadLibrary(find_file("display_status_bin.so", "../"))

# define class GoString to map:
# C type struct { const char *p; GoInt n; }
class GoString(Structure):
    _fields_ = [("p", c_char_p), ("n", c_longlong)]

# define class GoSlice to map to:
# C type struct { void *data; GoInt len; GoInt cap; }
class GoSlice(Structure):
    _fields_ = [("data", POINTER(GoString)), ("len", c_longlong), ("cap", c_longlong)]

def to_go_string(url):
    url = bytes(url, 'utf-8')
    return GoString(url, len(url.decode()))

def to_go_slice(*urls):
    return GoSlice((GoString * len(urls))(*urls), len(urls), len(urls))

lib.DisplayLinks.argtypes = [GoSlice]
lib.DisplayLinks.restype = c_longlong
def display(*urls):
    urls = [to_go_string(url) for url in urls]
    lib.DisplayLinks(to_go_slice(*urls))
