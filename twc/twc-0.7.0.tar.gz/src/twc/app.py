# Copyright (C) 2019 Michał Góral.
#
# This file is part of TWC
#
# TWC is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TWC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TWC. If not, see <http://www.gnu.org/licenses/>.

'''TWC entry point'''

import asyncio
import argparse
from tasklib import TaskWarrior

from prompt_toolkit.eventloop import use_asyncio_event_loop
from prompt_toolkit.styles import Style

import twc.config as config
import twc.commands as commands
import twc.layout as layout

from twc.locale import tr
from twc.utils import eprint
from twc._version import version


def update_config(settings, args):
    for name, val in vars(args).items():
        if val is not None:
            setattr(settings, name, val)


def parse_args():
    '''Support for commanline arguments. Keep their defaults as None and when
    their name will match, they'll nicely override settings.'''
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-t', '--taskrc',
        help=tr('path to taskrc'))
    parser.add_argument(
        '-a', '--agenda',
        help=tr('agenda to start application with'))
    parser.add_argument(
        '--debug',
        action='store_true',
        help=tr('enable debugging features'))
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {}'.format(version))
    return parser.parse_args()


def print_exceptions(loop, context):
    exc = context['exception']
    fmt = dict(etype=type(exc).__name__, msg=str(exc))

    msgs = [
        tr('{etype}: {msg}'.format_map(fmt)),
    ]

    eprint(msgs)


def run():
    '''Runs application'''
    args = parse_args()
    cfg = config.config()
    update_config(cfg.settings, args)

    tw = TaskWarrior(taskrc_location=cfg.settings.taskrc)

    controller = layout.LayoutController(tw, cfg)
    application = controller.make_app(
        style=Style.from_dict(cfg.style),
        key_bindings=commands.global_bindings(cfg),
        full_screen=True)

    cfg.settings.apply(application)

    controller = application.controller()

    # initial prepare of agenda view, which sends signals to all connected
    # slots
    if cfg.agendas:
        agenda = cfg.settings.agenda
        if agenda not in cfg.agendas:
            eprint(tr('No agenda named "{}"'.format(agenda)))
            agenda = next(iter(cfg.agendas))
        controller.agendaview.reset_agenda(agenda)

    use_asyncio_event_loop()

    loop = asyncio.get_event_loop()

    if not args.debug:
        loop.set_exception_handler(print_exceptions)

    loop.run_until_complete(application.run_async().to_asyncio_future())
    loop.close()


def main():
    return run()
