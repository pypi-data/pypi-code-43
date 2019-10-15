#!/usr/bin/env python
# coding: utf-8
'''Initialize the namespace de Iydon.
'''
__all__ = ('deploy', 'info', 'sites', 'symbols')
def __dir__() -> list: return __all__


from . import deploy
from . import info
from . import sites
from . import symbols


logo = '''
██╗██╗   ██╗██████╗  ██████╗ ███╗   ██╗
██║╚██╗ ██╔╝██╔══██╗██╔═══██╗████╗  ██║
██║ ╚████╔╝ ██║  ██║██║   ██║██╔██╗ ██║
██║  ╚██╔╝  ██║  ██║██║   ██║██║╚██╗██║
██║   ██║   ██████╔╝╚██████╔╝██║ ╚████║
╚═╝   ╚═╝   ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝
'''
print(logo)
