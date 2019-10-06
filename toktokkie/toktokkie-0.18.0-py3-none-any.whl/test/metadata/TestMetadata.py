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

from typing import List, Dict, Any, Type
from toktokkie.metadata.Metadata import Metadata
from toktokkie.exceptions import InvalidMetadata
from toktokkie.test.TestFramework import _TestFramework


class _TestMetadata(_TestFramework):
    """
    Class that defines what a metadata test has to test
    """

    def test_renaming(self):
        """
        Tests renaming files associated with the metadata type
        :return: None
        """
        raise NotImplementedError()

    def test_prompt(self):
        """
        Tests generating a new metadata object using user prompts
        :return: None
        """
        raise NotImplementedError()

    def test_validation(self):
        """
        Tests if the validation of metadata works correctly
        :return: None
        """
        raise NotImplementedError()

    def test_checking(self):
        """
        Tests if the checking mechanisms work correctly
        :return: None
        """
        raise NotImplementedError()

    def check_validation(
            self,
            valid_data: List[Dict[str, Any]],
            invalid_data: List[Dict[str, Any]],
            cls: Type[Metadata],
            directory: str
    ):
        """
        Helper function that checks that any valid or invalid metadata JSON
        is identified as such when loading metadata objects
        :param valid_data: List of valid metadata dictionaries
        :param invalid_data: List of invalid metadata dictionaries
        :param cls: The metadata class to use
        :param directory: The directory to use
        :return: None
        """
        for entry in valid_data:
            print(entry)
            cls(directory, entry)
        for entry in invalid_data:
            print(entry)
            try:
                cls(directory, entry)
                self.fail()
            except InvalidMetadata:
                pass
