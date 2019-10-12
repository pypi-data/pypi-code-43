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

import attr


def passthrough(val):
    return val


def ms(val):
    return float(val) / 1000


def strip(val):
    return val.strip()


class _SettingDescr:
    '''Descriptor of fields which should automatically do some things (like apply
    converters).'''
    def __init__(self, converter):
        self.val = None
        self.conv = converter

    def __get__(self, obj, objtype):
        return self.val

    def __set__(self, obj, val):
        self.val = self.conv(val)


def settings_descriptors(cls):
    for a in cls.__attrs_attrs__:
        if a.metadata and a.metadata.get('setting'):
            setattr(cls, a.name, _SettingDescr(a.metadata['converter']))
    return cls


def setting(*a, **kw):
    kw.setdefault('metadata', {})['setting'] = True

    # Do not set converter recognizable by attr.s - this would cause double
    # conversion during initialization, e.g. once in attr.s-generated __init__
    # and second time in Descriptor's __set__().
    kw['metadata']['converter'] = kw.pop('converter', passthrough)
    return attr.ib(*a, **kw)


@settings_descriptors
@attr.s
class Settings:
    # Time in milliseconds that is waited for a mapped sequence to complete.
    timeoutlen = setting(1000, converter=ms)

    # Time in milliseconds that is waited for a key code sequence to complete.
    # It's important to distinguish escape key from other keys that start with
    # escape sequence (x1B - ^[ - c-[).
    ttimeoutlen = setting(50, converter=ms)

    # Enable autocompletion
    autocomplete = setting(False)

    # Default filter used for all blocks
    deffilter = setting('-DELETED -PARENT')

    # Show various help texts, hints and tooltips
    autohelp = setting(True)

    # Status line formattings
    statusleft = setting(
        '<status.1><sr left=" " right=" ">{COMMAND}</sr></status.1>'
        '<sr left=" " right=" "><text>{taskrc}</text></sr>')
    statusright = setting(
        '<status.2><sr left=" ID:" right=" ">{task.id}</sr></status.2>'
        '<sr left=" " right=" ">{agenda.ppos}%</sr>')

    # Enable incremental search
    incsearch = setting(True)

    # Disable case sensitive search
    ignorecase = setting(True)

    # Override ignorecase when search string contains upper case characters.
    # Only used when 'ignorecase' is on (that's how it works in vim).
    smartcase = setting(True)

    # Agenda to start application with. If it's not set, first defined agenda
    # will be used.
    agenda = setting(None)

    # Used taskrc path.
    taskrc = setting('~/.taskrc', converter=strip)

    def apply(self, app):
        app.timeoutlen = self.timeoutlen
        app.ttimeoutlen = self.ttimeoutlen
