
import os
import re
import platform
import subprocess
import logging
import threading
import time
import tempfile
import shlex
from threading import Thread, Timer
from copy import deepcopy
from mcutk.debugger.base import DebuggerBase
from mcutk.util import run_command
from mcutk.apps import appfactory


class IDE(DebuggerBase):
    """IDE debugger
    """

    # supported ides
    TOOLS = [
        'iar',
        'mdk',
        'mcux'
    ]

    def __init__(self, ides, **kwargs):
        super(IDE, self).__init__("ide", '', **kwargs)
        if not isinstance(ides, list):
            raise TypeError('apps must be a list')
        self._ides = ides
        self.template_root = ''
        self._force_ide = None


    @property
    def is_ready(self):
        for ide in self._ides:
            if ide.is_ready is False:
                return False
        return True


    def set_force_ide(self, name):
        if name in self.TOOLS:
            self._force_ide = name



    def flash(self, debugfile, idename='mcux', target='flexspi_nor_debug', board=None, template_root=None, **kwargs):
        convert_map = {
            'armgcc': 'mdk',
            'uv4': 'mdk'
        }

        if self._force_ide:
            idename = self._force_ide
            logging.info("mandatory debugger run with %s", idename)

        # force to use mcuxpresso to flash binary to board
        if debugfile.endswith('.bin'):
            idename = 'mcux'

        idename = convert_map.get(idename, idename)

        if template_root is None:
            template_root = self.template_root

        if board is None:
            board = self._board

        # assert template projects root
        if not os.path.exists(template_root):
            raise IOError("template project[%s] is not exists!"%template_root)


        #assert tool name
        if idename not in IDE.TOOLS:
            raise ValueError("IDE [{}] is unsupported for board programming!".format(idename))

        for app in self._ides:
            if app.name == idename:
                prjdir = os.path.join(template_root, app.name)

                # workaround for iar programming
                if idename == 'iar':
                    if ":" not in board.usbid:
                        logging.warning('There is no header infomation in usbid, but IAR-CSPY need that\n!')
                else:
                    # workaround to make sure the origin board object is not changed.
                    board = deepcopy(board)
                    board.usbid = board.usbid.split(':')[-1]

                self._call_registered_callback("before-load")
                kwargs['gdbpath'] = self.gdbpath
                logging.info("IDE name: %s, Version: %s", app.name, app.version)
                ret = app.programming(board, prjdir, target, debugfile, **kwargs)

                return ret
        else:
            raise ValueError('{} path is not exists or not set!'.format(idename))



    def erase(self, target='debug'):
        from mcutk.debugger.redlink import RedLink
        prjdir = os.path.join(self.template_root, 'mcux')
        for app in self._ides:
            if app.name == 'mcux':
                mcux = app
                break
        else:
            raise ValueError('MCUXpressoIDE path is not exists or not set!')

        redlink = RedLink(mcux.path + '/ide', version=self.version)
        redlink.gdbpath = self.gdbpath
        redlink.template_root = prjdir
        self._board.usbid = self._board.usbid.split(':')[-1]
        redlink.set_board(self._board)
        return redlink.erase()





    def reset(self):
        pass







