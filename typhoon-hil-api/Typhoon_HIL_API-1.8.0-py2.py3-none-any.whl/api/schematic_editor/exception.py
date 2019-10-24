#
# Schematic API exceptions module.
#
#
# This file is a part of Typhoon HIL API library.
#
# Typhoon HIL API is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import print_function, unicode_literals


class SchApiException(Exception):
    """
    Base Schematic API exception.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize an object.
        """
        super(SchApiException, self).__init__(*args, **kwargs)


class SchApiDuplicateConnectionException(SchApiException):
    """
    Indicate that connectables are already directly connected by connection.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize an exception.
        """
        super(SchApiDuplicateConnectionException, self).__init__(*args,
                                                                 **kwargs)


class SchApiItemNotFoundException(SchApiException):
    """
    Indicate that some item doesn't exists.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize an exception.
        """
        super(SchApiItemNotFoundException, self).__init__(*args, **kwargs)


class SchApiItemNameExistsException(SchApiException):
    """
    Indicate
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize an exception.
        """
        super(SchApiItemNameExistsException, self).__init__(*args, **kwargs)
