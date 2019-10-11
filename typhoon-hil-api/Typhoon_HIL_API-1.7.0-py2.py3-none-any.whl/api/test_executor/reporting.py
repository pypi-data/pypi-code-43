#
# Reporting module.
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
import base64
import io


class Report(object):
    """
    Class that holds information which will be embedded in TextExecutor
    report.html file.
    """

    def __init__(self, logo=None, title=None, description=None):
        """
        Initialize an report object.

        Args:
            logo(str): Path to the logo image file.
            title(str): Report title.
            description(str): Report description.
        """
        self.__logo = None

        self.logo = logo
        self.title = title
        self.description = description

        self.sections = []

    def set_logo(self, logo_img):
        """
        Automatically convert img file to base64 representation
        ready for embedding directly in html code

        Args:
            logo_img(str): Path to the log image file.

        Returns:
            None
        """
        if logo_img is not None:
            try:
                with io.open(file=logo_img, mode="rb") as img_file:
                    pngdata = base64.b64encode(img_file.read())
                    self.__logo = pngdata
            except Exception:
                raise Exception(
                    "Unable to read logo image:'{}'.".format(logo_img)
                )

    def get_logo(self):
        """
        Returns report logo image data.

        Args:
            None

        Returns:
            Logo image data as base64 encoded string.
        """
        return self.__logo

    logo = property(get_logo, set_logo)
