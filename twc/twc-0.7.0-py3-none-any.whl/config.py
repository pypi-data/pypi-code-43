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

'''Reader and handler of globally-available app configuration.'''

from collections import OrderedDict

import attr

import mgcomm.xdg
import mgcomm.env

from twc.settings import Settings


@attr.s
class Block:
    title = attr.ib()
    format = attr.ib('{description}')
    filter = attr.ib(None)
    sort = attr.ib(None)
    limit = attr.ib(None)


@attr.s
class Agenda:
    name = attr.ib()
    blocks = attr.ib(factory=list)


@attr.s
class Config:
    agendas = attr.ib(factory=OrderedDict)
    keys = attr.ib(factory=dict)
    settings = attr.ib(factory=Settings)

    _style = attr.ib()
    # TODO: commands should be populated from frozen command set (mgoral, 2019-04-18)
    _commands = attr.ib(factory=dict)

    def __attrs_post_init__(self):
        self.bind('enter', 'activate')
        self.bind('escape', 'cancel')
        self.bind('c-c', 'quit')
        self.bind('q', 'quit')
        self.bind('Q', 'quit')

        self.bind('f', 'followurl')

        self.bind('j', 'scroll.down')
        self.bind('k', 'scroll.up')
        self.bind('down', 'scroll.down')
        self.bind('up', 'scroll.up')

        self.bind(']', 'scroll.nextsection')
        self.bind('[', 'scroll.prevsection')
        self.bind('pagedown', 'scroll.nextsection')
        self.bind('pageup', 'scroll.prevsection')

        self.bind('g g', 'scroll.begin')
        self.bind('G', 'scroll.end')
        self.bind('home', 'scroll.begin')
        self.bind('end', 'scroll.end')

        self.bind('tab', 'tab.next')
        self.bind('s-tab', 'tab.prev')

        self.bind('/', 'search')
        self.bind('c-f', 'search')
        self.bind('n', 'search.forward')
        self.bind('N', 'search.backward')

        self.bind('R', 'refresh')

        self.bind('a', 'task.add')
        self.bind('t', 'task.add.subtask')
        self.bind('m', 'task.modify')
        self.bind('e', 'task.edit')
        self.bind('A', 'task.annotate')
        self.bind('D', 'task.denotate')
        self.bind('a-space', 'task.toggle')
        self.bind('delete', 'task.delete')
        self.bind('u', 'task.undo')
        self.bind('S', 'task.synchronize')
        self.bind('space', 'task.select')

    def add_block(self, agenda, **kwargs):
        '''Adds a new block to specified agenda. Keywords are passed directly
        to Block constructor. Agenda is created if it doesn't exist yet.'''
        if agenda not in self.agendas:
            self.agendas[agenda] = Agenda(agenda)

        if self.settings.deffilter:
            new_filter = self.settings.deffilter
            orig = kwargs.get('filter')
            if orig:
                new_filter += ' ( {} )'.format(orig)
            kwargs['filter'] = new_filter

        found = self.agendas[agenda]
        found.blocks.append(Block(**kwargs))

    @property
    def style(self):
        return self._style

    def set_style(self, name, definition):
        '''Defines a color style in a format supported by prompt-toolkit:
            fg:color bg:other bold italic'''

        # fix some common mistakes: capital letters, multiple spaces...
        style = definition.lower().split()
        if style:
            self._style[name] = ' '.join(style)

    def set(self, key, value):
        '''Changes a setting'''
        setattr(self.settings, key.strip(), value)

    def bind(self, key, command):
        '''Binds a key. Key can have the following form:
            - x: single key
            - c-x: key with modifier (ctrl) pressed
            - c x: key sequence: press c, then press x'''
        key = _bind_preprocess(key)
        self.unbind(key)

        sequence = tuple(key.split())
        self.keys[sequence] = command
        self._commands.setdefault(command, set()).add(sequence)

    def unbind(self, key):
        '''Unbinds a key. See bind's description for key format.'''
        sequence = tuple(key.split())

        command = self.keys.pop(sequence, None)
        if command:
            self._commands[command].discard(sequence)

    def command_handler(self, name, kb, **kw):
        def _decor(fn):
            for sequence in self._commands.get(name, []):
                kb.add(*sequence, **kw)(fn)
            return fn
        return _decor

    def deregister_command_handler(self, kb, handler):
        kb.remove(handler)

    @_style.default
    def _default_style(self):
        return {
            # name : (fg, bg)
            'heading': 'fg:orange bold',
            'text': 'fg:white',
            'comment': 'fg:gray',
            'info': 'fg:lightblue',
            'warning': 'fg:red',
            'error': 'fg:white bg:red',
            'highlight': 'reverse',
            'mark': 'fg:limegreen',

            'tabline': 'bg:gray',
            'tab': 'fg:white bg:darkgray',
            'tabsel': 'bg:',

            'statusline': 'fg:black bg:gray',
            'status.1': 'fg:black bg:lightblue',
            'status.2': 'fg:black bg:lightgray',

            'tooltip': 'fg:gray',
        }


def _bind_preprocess(key):
    if key.startswith('a-'):
        key = 'escape {}'.format(key[2:])
    return key


def _create_default_blocks(cfg):
    cfg.add_block(
        'Summary',
        title='<heading>== Next tasks ==</heading>',
        filter='status:pending',
        format='{description}<sr left=" "><warning>{priority}</warning></sr><sr left=" "><info>{tags}</info></sr>',  # pylint: disable=line-too-long
        sort='priority-,urgency-')

    cfg.add_block(
        'Summary',
        title='<heading>== Recently completed ==</heading>',
        filter='status:completed',
        format='{description}',
        sort='end-',
        limit=10)

    cfg.add_block(
        'Waiting',
        title='<heading>== Waiting tasks ==</heading>',
        filter='-COMPETED +WAITING',
        format='{description}')

    cfg.add_block(
        'Scheduled',
        title='<heading>== Scheduled tasks ==</heading>',
        filter='-COMPLETED and (+DUE or +SCHEDULED)',
        sort='due,scheduled',
        format='{description}<sr left=" (sch: " right=")">{scheduled:%Y-%m-%d}</sr><sr left=" (due: " right=")">{due:%Y-%m-%d}</sr>')  # pylint: disable=line-too-long


def config_path():
    '''Returns a path to the configuration file, which is searched in a way
    specified by XDG Base Directory Specification:
    https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html

    This function doesn't ensure that configuration file indeed exists. If no
    suitable configuration exists, it returns a user-specific path which is best
    suitable (according to XDG spec).'''
    return mgcomm.xdg.basedir('config', subdir='twc', file='config.py')


def config():
    '''Returns an object representing a configuration'''
    cfg = Config()

    filename = config_path()
    try:
        with open(filename) as cfg_mod:
            code = compile(cfg_mod.read(), filename, 'exec')
            exec(code, {'c': cfg})  # pylint: disable=exec-used
    except FileNotFoundError:
        pass

    if not cfg.agendas:
        _create_default_blocks(cfg)

    if not cfg.settings.agenda:
        cfg.settings.agenda = next(iter(cfg.agendas))

    return cfg
