from __future__ import print_function
import click
import logging
import glob
import os

from os.path import join
import prettytable as pt
from mcutk.apps import appfactory
from mcutk.exceptions import ProjectNotFound
from mcutk.managers.conf_mgr import ConfMgr
from . import TOOLCHAINS

@click.command('config', short_help='configuration(\"~/.mcutk\") management')
@click.option('--show', is_flag=True, help='show configuration from \"~/.mcutk\"')
@click.option('--auto', is_flag=True, help='auto scan your system, then configure into \"~/.mcutk\"')
def cli(show, auto):
    """Configuration Management Command"""
    cfger = ConfMgr.load()

    if show:
        if cfger.is_empty:
            print("Need to initialize the mcutk")
            return
        else:
            cfger.show()

    if auto:
        print("Discover installed toolchains from your system ...\n")
        tb = pt.PrettyTable()
        tb.align = 'l'
        tb.field_names = ["name", "version", "path"]
        toolchains = list()

        for toolname in TOOLCHAINS:
            try:
                tool = appfactory(toolname)
                app = tool.get_latest()
                if app and app.is_ready:
                    toolchains.append(app)
                    tb.add_row([app.name, app.version, app.path])
                    cfger.set_app(app)
                else:
                    logging.debug("not found tool: %s", toolname)
            except:
                logging.exception("failed to discover tool %s", toolname)

        cfger.save()
        print(tb)
        print("\n\"{}\" has been updated successfully!\n".format(cfger.CONFIG_FILE))

