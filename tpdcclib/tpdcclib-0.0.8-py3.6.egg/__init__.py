#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Initialization module for tpDccLib
"""

from __future__ import print_function, division, absolute_import

import os
import sys
import inspect

from tpPyUtils import importer
from tpDccLib.abstract import dcc as abstract_dcc, shelf as abstract_shelf, menu as abstract_menu,  callback as abstract_callback

main = __import__('__main__')

# =================================================================================

logger = None
Dcc = abstract_dcc.AbstractDCC()
Menu = abstract_menu.AbstractMenu
Shelf = abstract_shelf.AbstractShelf

# =================================================================================


class DccCallbacks(object):
    Shutdown = ('Shutdown', {'type': 'simple'})
    Tick = ('Tick', {'type': 'simple'})
    ScenePreCreated = ('ScenePreCreated', {'type': 'simple'})
    ScenePostCreated = ('ScenePreCreated', {'type': 'simple'})
    SceneNewRequested = ('SceneNewRequested', {'type': 'simple'})
    SceneNewFinished = ('SceneNewFinished', {'type': 'simple'})
    SceneSaveRequested = ('SceneSaveRequested', {'type': 'simple'})
    SceneSaveFinished = ('SceneSaveFinished', {'type': 'simple'})
    SceneOpenRequested = ('SceneOpenRequested', {'type': 'simple'})
    SceneOpenFinished = ('SceneOpenFinished', {'type': 'simple'})
    UserPropertyPreChanged = ('UserPropertyPreChanged', {'type': 'filter'})
    UserPropertyPostChanged = ('UserPropertyPostChanged', {'type': 'filter'})
    NodeSelect = ('NodeSelect', {'type': 'filter'})
    NodeAdded = ('NodeAdded', {'type': 'filter'})
    NodeDeleted = ('NodeDeleted', {'type': 'filter'})


# =================================================================================


class Dccs(object):
    Unknown = 'unknown'
    Houdini = 'houdini'
    Maya = 'maya'
    Max = 'max'
    Nuke = 'nuke'

# =================================================================================


class tpDccLib(importer.Importer, object):
    def __init__(self):
        super(tpDccLib, self).__init__(module_name='tpDccLib')

    def get_module_path(self):
        """
        Returns path where tpDccLib module is stored
        :return: str
        """

        try:
            mod_dir = os.path.dirname(inspect.getframeinfo(inspect.currentframe()).filename)
        except Exception:
            try:
                mod_dir = os.path.dirname(__file__)
            except Exception:
                try:
                    import tpDccLib
                    mod_dir = tpDccLib.__path__[0]
                except Exception:
                    return None

        return mod_dir


def init(do_reload=False):
    """
    Initializes module
    :param do_reload: bool, Whether to reload modules or not
    """

    dcclib_importer = importer.init_importer(importer_class=tpDccLib, do_reload=False)

    global logger
    logger = dcclib_importer.logger

    dcclib_importer.import_modules()
    dcclib_importer.import_packages(only_packages=True, order=['tpDccLib.core'])
    if do_reload:
        dcclib_importer.reload_all()

    init_dcc(do_reload=do_reload)

    from tpDccLib.core import callbackmanager
    callbackmanager.CallbacksManager.initialize()


def init_dcc(do_reload=False):
    """
    Checks DCC we are working on an initializes proper variables
    """

    if 'cmds' in main.__dict__:
        import tpMayaLib
        tpMayaLib.init_dcc(do_reload=do_reload)
    elif 'MaxPlus' in main.__dict__:
        import tpMaxLib
        tpMaxLib.init_dcc(do_reload=do_reload)
    elif 'hou' in main.__dict__:
        import tpHoudiniLib
        tpHoudiniLib.init_dcc(do_reload=do_reload)
    elif 'nuke' in main.__dict__:
        raise NotImplementedError('Nuke is not a supported DCC yet!')
    else:
        global Dcc
        from tpDccLib.core import dcc
        Dcc = dcc.UnknownDCC
        logger.warning('No DCC found, using abstract one!')


def is_nuke():
    """
    Checks if Nuke is available or not
    :return: bool
    """

    return Dcc.get_name() == Dccs.Nuke


def is_maya():
    """
    Checks if Maya is available or not
    :return: bool
    """

    return Dcc.get_name() == Dccs.Maya


def is_max():
    """
    Checks if Max is available or not
    :return: bool
    """

    return Dcc.get_name() == Dccs.Max


def is_houdini():
    """
    Checks if Houdini is available or not
    :return: bool
    """

    return Dcc.get_name() == Dccs.Houdini


def callbacks():
    """
    Return a full list of callbacks based on DccCallbacks dictionary
    :return: list<str>
    """

    new_list = list()
    for k, v in DccCallbacks.__dict__.items():
        if k.startswith('__') or k.endswith('__'):
            continue
        new_list.append(v[0])

    return new_list


def register_class(cls_name, cls, is_unique=False):
    """
    This function registers given class
    :param cls_name: str, name of the class we want to register
    :param cls: class, class we want to register
    :param is_unique: bool, Whether if the class should be updated if new class is registered with the same name
    """

    if is_unique:
        if cls_name in sys.modules[__name__].__dict__:
            setattr(sys.modules[__name__], cls_name, getattr(sys.modules[__name__], cls_name))
    else:
        sys.modules[__name__].__dict__[cls_name] = cls
