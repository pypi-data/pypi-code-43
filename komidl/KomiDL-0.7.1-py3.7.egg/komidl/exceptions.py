# KomiDL - A gallery downloader
# Copyright (C) 2019 DNSheng
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""This module defines custom exceptions raised and caught by KomiDL"""


class ExtractorFailed(Exception):
    """Any failures as a result of the extractor unable to handle an
       appropriate URL

    If the extractor returns an invalid URL for an image, then it is
    considered to be an ExtractorFailed exception, and not an InvalidURL
    exception.
    """


class InvalidURL(Exception):
    """Any inappropriate URL given by the user returned by the server"""
