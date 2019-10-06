"""LICENSE
Copyright 2015 Hermann Krumrey <hermann@krumreyh.com>

This file is part of toktokkie.

toktokkie is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

toktokkie is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with toktokkie.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""


class InvalidMetadata(Exception):
    """
    Exception that is raised whenever metadata is invalid
    """
    pass


class MetadataMismatch(Exception):
    """
    Exception that is raised whenever the metadata type in the JSON data
    is in conflict with the actual metadata class
    """
    pass


class MissingMetadata(Exception):
    """
    Exception that is raised whenever metadata is not found
    """
    pass


class MissingXDCCInstructions(Exception):
    """
    Exception that is raised whenever xdcc update instructions don't exist
    """
    pass


class InvalidXDCCInstructions(Exception):
    """
    Exception that is raised whenever xdcc update instructions are invalid
    """
    pass
