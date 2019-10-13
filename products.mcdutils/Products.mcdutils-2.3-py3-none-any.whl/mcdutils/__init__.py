""" Product:  mcdutils

Implement Zope sessions using memcached as the backing store.
"""


class MemCacheError(IOError):
    pass


def initialize(context):

    from .proxy import MemCacheProxy
    from .proxy import addMemCacheProxyForm
    from .proxy import addMemCacheProxy
    context.registerClass(MemCacheProxy,
                          constructors=(addMemCacheProxyForm,
                                        addMemCacheProxy),
                          icon='www/proxy.gif')

    from .sessiondata import MemCacheSessionDataContainer
    from .sessiondata import addMemCacheSessionDataContainerForm
    from .sessiondata import addMemCacheSessionDataContainer
    context.registerClass(MemCacheSessionDataContainer,
                          constructors=(addMemCacheSessionDataContainerForm,
                                        addMemCacheSessionDataContainer),
                          icon='www/sdc.gif')

    from .zcache import MemCacheZCacheManager
    from .zcache import addMemCacheZCacheManagerForm
    from .zcache import addMemCacheZCacheManager
    context.registerClass(MemCacheZCacheManager,
                          constructors=(addMemCacheZCacheManagerForm,
                                        addMemCacheZCacheManager),
                          icon='www/zcm.gif')
