# appteka - helpers collection

# Copyright (C) 2018-2019 Aleksandr Popov

# This program is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Lesser GNU General Public License for more details.

# You should have received a copy of the Lesser GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Helpers for distribution of software."""


import sys
import platform
import locale
import gettext
from pkg_resources import resource_filename as resource


def build_folder_name(name, version, appendix=None):
    """Return name of build folder."""
    bit_version = platform.architecture()[0]
    os_name = sys.platform
    if 'win' in os_name:
        os_name = 'win'
    res = "build/{}-{}".format(name, version)
    if appendix is not None:
        res += "-{}".format(appendix)
    res += "-{}-{}".format(os_name, bit_version)
    return res


def init_translation(package_name, resource_name, module_name):
    """ Returns function for specifying of places to be translated. """
    lang = locale.getdefaultlocale()[0]
    gettext.install(module_name)

    def _echo(text):
        return text

    try:
        trans = gettext.translation(
            module_name,
            resource(package_name, resource_name),
            languages=[lang],
        )
        return trans.gettext
    except (ImportError, FileNotFoundError):
        return _echo
