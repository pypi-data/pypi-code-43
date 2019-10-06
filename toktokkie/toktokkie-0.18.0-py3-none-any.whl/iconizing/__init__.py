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

from typing import Type
from toktokkie.iconizing.procedures.Procedure import Procedure
from toktokkie.iconizing.procedures.GnomeProcedure import GnomeProcedure
from toktokkie.iconizing.procedures.NoopProcedure import NoopProcedure
from toktokkie.iconizing.Iconizer import Iconizer

procedures = [GnomeProcedure]


def default_procedure() -> Type[Procedure]:
    """
    Checks all available procedures for eligibility
    :return: The eligible procedure or None if none were found
    """
    for procedure in procedures:
        if procedure.is_applicable():
            return procedure
    return NoopProcedure
