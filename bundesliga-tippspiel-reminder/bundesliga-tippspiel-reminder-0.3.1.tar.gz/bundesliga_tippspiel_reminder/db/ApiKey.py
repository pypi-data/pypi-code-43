"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of bundesliga-tippspiel-reminder (btr).

btr is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

btr is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with btr.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

from kudubot.db import Base
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship


class ApiKey(Base):
    """
    Stores the API key for a user
    """

    __tablename__ = "api_keys"
    """
    The name of the table
    """

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    """
    The ID of the API key
    """

    kudubot_user_id = Column(
        Integer,
        ForeignKey("addressbook.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False
    )
    """
    The kudubot address ID
    """

    kudubot_user = relationship("Address")
    """
    The kudubot address
    """

    tippspiel_user = Column(Integer, nullable=False)
    """
    The bundesliga-tippspiel user
    """

    key = Column(String(255), nullable=False)
    """
    The actual API key
    """
