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

from typing import List, Dict, Any
from datetime import timedelta, datetime
from kudubot.db import Base
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship


class Reminder(Base):
    """
    Database table that defines a reminder.
    """

    __tablename__ = "reminders"
    """
    The name of the table
    """

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    """
    The ID of the reminder
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

    reminder_time = Column(Integer, nullable=False)
    """
    The time before the next unbet match when the reminder message
    will be sent.
    Unit: seconds
    """

    last_reminder = Column(String(19), nullable=False,
                           default="1970-01-01:01-01-01")
    """
    The time when the last reminder was sent. Format in the form
    %Y-%m-%d:%H-%M-%S
    """

    @property
    def reminder_time_delta(self) -> timedelta:
        """
        :return: The 'reminder_time' parameter as a datetime timedelta
        """
        return timedelta(seconds=self.reminder_time)

    @property
    def last_reminder_datetime(self) -> datetime:
        """
        :return: The 'last_reminder' parameter as a datetime object
        """
        return datetime.strptime(self.last_reminder, "%Y-%m-%d:%H-%M-%S")

    def get_due_matches(
            self,
            matches: List[Dict[str, Any]],
            bets: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Retrieves any due matches for the reminder settings
        :param matches: All matches
        :param bets: All bets of the user
        :return: A list of due matches
        """
        now = datetime.utcnow()
        start = max(now, self.last_reminder_datetime)
        start_str = start.strftime("%Y-%m-%d:%H-%M-%S")
        then = now + self.reminder_time_delta
        then_str = then.strftime("%Y-%m-%d:%H-%M-%S")

        due_matches = list(filter(
            lambda x: start_str < x["kickoff"] < then_str,
            matches
        ))

        betted_match_ids = list(map(lambda x: x["match_id"], bets))

        to_remind = list(filter(
            lambda x: x["id"] not in betted_match_ids,
            due_matches
        ))

        return to_remind
