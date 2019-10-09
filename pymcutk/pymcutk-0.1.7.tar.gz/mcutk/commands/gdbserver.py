from __future__ import print_function
import click
import glob
import os
from os.path import join

from mcutk.debugger import getdebugger
from mcutk.managers.conf_mgr import ConfMgr
from mcutk.managers.debug_helper import Debughelper


@click.command('gdbserver', short_help='start a standalone gdbserver')
@click.option('-t', '--type', default='jlink', help='debugger type, jlink/pyocd.')
@click.option('-u', '--usbid', help='unique usb id')
@click.option('-p', '--port', help='specific server port')
def cli(type, usbid, port):
    """ Start a gdb server."""

    cfger = ConfMgr.load()
    debugger, device = Debughelper.choose_device(None)
    if port:
        device['port'] = port

    if debugger and device:
        debugger.start_gdbserver(**device)

