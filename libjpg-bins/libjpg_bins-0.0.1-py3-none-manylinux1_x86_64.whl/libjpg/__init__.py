def init_libpython():
    import ctypes
    import pkg_resources
    t = pkg_resources.resource_filename(__name__, "libjpg.so.62.3.0")
    ctypes.CDLL(t)
