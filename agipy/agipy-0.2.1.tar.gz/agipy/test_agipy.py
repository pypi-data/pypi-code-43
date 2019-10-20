"""
agipy enables you to destroy cloud infrastructure in a hurry.
Copyright (C) 2019  Nils Müller<shimst3r@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>
"""

# Most of the test cases in this test suite are about testing to import
# submodules that will not be used.
# pylint: disable=import-outside-toplevel, unused-import


def test_import_agipy_module():
    """
    test_import_agipy_module makes sure the agipy module can be imported
    properly.
    """
    try:
        import agipy
    except ImportError:
        assert False
    else:
        assert True


def test_import_azure_provider():
    """
    test_import_azure_provider makes sure the azure provider module can be
    imported properly.
    """
    try:
        from agipy.providers import azure
    except ImportError:
        assert False
    else:
        assert True
