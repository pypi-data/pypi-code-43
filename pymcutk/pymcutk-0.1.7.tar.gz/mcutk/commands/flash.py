import os
import sys
import click
import glob
import logging
from os.path import join
import yaml

from mcutk.apps import appfactory
from mcutk.board import Board
from mcutk.managers.conf_mgr import ConfMgr
from mcutk.managers.debug_helper import Debughelper

LEVELS = {
    'warning': logging.WARNING,
    'debug': logging.DEBUG,
    'info': logging.INFO
}



@click.command('flash', short_help='flash debug file to board')
@click.argument('path', required=True, type=click.Path(exists=True))
@click.option('-u', '--usbid', help='unique usb id')
@click.option('-a', '--base-address', default=0, help='base address to load.')
@click.option('-c', '--config-file', help='load config from file.')
def cli(path, usbid, base_address, config_file):
    # config logging
    level = LEVELS.get('info', logging.INFO)
    format = '[%(levelname)s] %(message)s'
    logging.basicConfig(level=level, format=format)

    # get arm-none-eabi-gdb
    gdb = None
    armgcc = appfactory('armgcc').get_latest()
    if armgcc and armgcc.is_ready:
        gdb = os.path.join(armgcc.path, 'bin/arm-none-eabi-gdb')

    # load from config file
    device = dict()
    if config_file:
        with open(config_file) as file:
            config = yaml.safe_load(file)
            device = config.get('board')

    if usbid:
        device['usbid'] = usbid

    # prepare debugger and device
    debugger, device = Debughelper.choose_device(device)
    if not device:
        exit(1)

    board = Board(**device)
    board.debugger = debugger
    board.debugger.gdbpath = gdb
    click.secho(str(board), fg="yellow")

    if base_address:
        board.start_address = base_address

    ret = board.programming(path)
    if ret[0] == 0:
        click.secho('Flash programming successful!', fg="green")
        exit(0)
    else:
        click.secho('Flash programming failed!', fg="red")
        exit(1)