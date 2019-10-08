def init_lib():
    import ctypes
    import pkg_resources
    t = pkg_resources.resource_filename(__name__, "libjpeg.so.62.3.0")
    ctypes.CDLL(t)
