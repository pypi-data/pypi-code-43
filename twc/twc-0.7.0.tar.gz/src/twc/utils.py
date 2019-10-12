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

'''Utility functions'''

import sys
import contextlib
import asyncio

from prompt_toolkit.application.current import get_app
from prompt_toolkit.formatted_text import to_formatted_text


def pprint(text):
    '''Print some text in prompt_toolkit-friendly way.'''
    if not text:
        return
    if isinstance(text, list):
        text = '\n'.join(text)

    try:
        controller = get_app().controller()
        ft = to_formatted_text(text)
        controller.messages.print(ft)
    except AttributeError:  # no controller or controller() is None
        print(text)
        return


def eprint(text):
    '''Print error in prompt_toolkit-friendly way.'''
    if not text:
        return
    if isinstance(text, list):
        text = '\n'.join(text)

    try:
        controller = get_app().controller()
        ft = to_formatted_text(text, style='class:error')
        controller.messages.print(ft)
    except AttributeError:  # no controller or controller() is None
        print(text, file=sys.stderr)
        return


@contextlib.contextmanager
def aprint(text, delay=0.42, style=''):
    '''Context manager which prints a waiting print together with additional
    animation for as long as it is active. It's useful for indicating to the
    user that TWC is (still) working.

    Delay is given in seconds, but it is strongly discouraged to be changed
    from the default 0.42, which is well established Answer to the Ultimate
    Question of Life, The Universe and Everything.'''
    # We don't catch AttributeError on purpose. This function can't fulfil its
    # promise without a controller.
    controller = get_app().controller()
    loop = asyncio.get_event_loop()

    maxdots = 3
    cbh = None

    def _print(i):
        if i > maxdots:
            i = 0
        dots = '.' * i

        ft = to_formatted_text(text + dots, style=style)
        controller.messages.print(ft)
        controller.app.invalidate()

        nonlocal cbh
        cbh = loop.call_later(delay, _print, i + 1)

    try:
        cbh = loop.call_soon(_print, maxdots)
        yield
    finally:
        cbh.cancel()
        controller.messages.clear()


def cancel_all_async_tasks():
    for task in asyncio.Task.all_tasks():
        task.cancel()
