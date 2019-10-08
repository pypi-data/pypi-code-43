def init_lib():
    import ctypes
    import pkg_resources
    ctypes.CDLL(pkg_resources.resource_filename(__name__, "ld-musl-x86_64.so.1"))
    ctypes.CDLL(pkg_resources.resource_filename(__name__, "libjpeg.so.62.3.0"))
    ctypes.CDLL(pkg_resources.resource_filename(__name__, "libjpeg-3b10b538.so.9.3.0"))
