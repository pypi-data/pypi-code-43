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

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from bokkichat.entities.message.TextMessage import TextMessage
from kudubot.Bot import Bot
from kudubot.db.Address import Address as Address
from kudubot.parsing.CommandParser import CommandParser
from bundesliga_tippspiel_reminder import version
from bundesliga_tippspiel_reminder.db.ApiKey import ApiKey
from bundesliga_tippspiel_reminder.db.Reminder import Reminder
from bundesliga_tippspiel_reminder.BundesligaTippspielReminderParser import \
    BundesligaTippspielReminderParser
from bundesliga_tippspiel_reminder.api import api_request, api_is_authorized


class BundesligaTippspielReminderBot(Bot):
    """
    The bundesliga tippspiel reminder bot
    """

    @classmethod
    def name(cls) -> str:
        """
        :return: The name of the bot
        """
        return "bundesliga-tippspiel-reminder"

    @classmethod
    def version(cls) -> str:
        """
        :return: The current version of the bot
        """
        return version

    @property
    def bg_pause(self) -> int:
        """
        The pause between background iterations
        :return: The pause in seconds
        """
        return 600

    @classmethod
    def parsers(cls) -> List[CommandParser]:
        """
        :return: The parsers for the bot
        """
        return [BundesligaTippspielReminderParser()]

    def is_authorized(
            self,
            address: Address,
            _: Dict[str, Any],
            db_session: Session
    ) -> bool:
        """
        Checks if a user is authorized
        :param address: The user to check
        :param _: possible command arguments
        :param db_session: The database session to use
        :return: True if authorized, False otherwise
        """
        return self._get_api_key(address, db_session) is not None

    @classmethod
    def unauthorized_message(cls) -> str:
        """
        :return: A custom message sent to a user if they tried to access
                 a feature that requires authorization without being
                 authorized
        """
        return "Not authorized, use /login <username> <password> first"

    @staticmethod
    def _get_api_key(address: Address, db_session: Session) \
            -> Optional[str]:
        """
        Retrieves the API key for an address
        :param address: The address for which to get the API key
        :param db_session: The database session to use
        :return: The API key, or None if no API key exists
        """
        api_key = db_session.query(ApiKey).filter_by(kudubot_user=address)\
            .first()
        return None if api_key is None else api_key.key

    @staticmethod
    def _get_reminder(address: Address, db_session: Session) \
            -> Optional[Reminder]:
        """
        Retrieves the reminder object for a user from the database
        :param address: The address of the user
        :param db_session: The database session to use
        :return: The Reminder object or None if none exist.
        """
        return db_session.query(Reminder).filter_by(kudubot_user=address)\
            .first()

    def _on_login(
            self,
            sender: Address,
            args: Dict[str, Any],
            db_session: Session
    ):
        """
        Handles a login command
        :param sender: The sender of the message
        :param args: The command arguments
        :param db_session: The database session
        :return: None
        """

        data = {"username": args["username"], "password": args["password"]}
        response = api_request("api_key", "post", data)

        if response["status"] == "ok":
            key = ApiKey(
                kudubot_user=sender,
                tippspiel_user=args["username"],
                key=response["data"]["api_key"]
            )
            db_session.add(key)
            db_session.commit()
            reply = "Logged in successfully"
        else:
            reply = "Login unsuccessful"

        reply = TextMessage(self.connection.address, sender, reply, "Login")
        self.connection.send(reply)

    def _on_is_authorized(
            self,
            sender: Address,
            _: Dict[str, Any],
            db_session: Session
    ):
        """
        Handles an is_authorized command
        :param sender: The sender of the message
        :param _: The command arguments
        :param db_session: The database session to use
        :return: None
        """
        api_key = self._get_api_key(sender, db_session)
        reply = "yes" if api_is_authorized(api_key) else "no"
        self.connection.send(TextMessage(
            self.connection.address, sender, reply, "Authorized"
        ))

    @Bot.auth_required
    def _on_leaderboard(
            self,
            address: Address,
            _: Dict[str, Any],
            db_session: Session
    ):
        """
        Handles a leaderboard command
        :param address: The sender of the command
        :param _: Command arguments
        :param db_session: The database session to use
        :return: None
        """
        api_key = self._get_api_key(address, db_session)
        response = api_request("leaderboard", "get", {}, api_key)

        if response["status"] == "ok":
            leaderboard = response["data"]["leaderboard"]
            formatted = []
            for i, (user, points) in enumerate(leaderboard):
                formatted.append("{}: {} ({})".format(
                    i + 1,
                    user["username"],
                    points
                ))
            self.send_txt(address, "\n".join(formatted), "Leaderboard")

    @Bot.auth_required
    def _on_reminder_state(
            self,
            address: Address,
            _: Dict[str, Any],
            db_session: Session
    ):
        """
        Handles a reminder_state command
        :param address: The sender of the command
        :param _: Command arguments
        :param db_session: The database session to use
        :return: None
        """
        reminder = self._get_reminder(address, db_session)
        if reminder is None:
            reply = "No reminder set"
        else:
            reply = "Reminder set to go off {} hours before a match.".format(
                int(reminder.reminder_time / 3600)
            )
        self.send_txt(address, reply, "Reminder State")

    @Bot.auth_required
    def _on_activate_reminder(
            self,
            address: Address,
            args: Dict[str, Any],
            db_session: Session
    ):
        """
        Handles activating reminders
        :param address: The sender of the message
        :param args: Command arguments
        :param db_session: The database session to use
        :return: None
        """
        reminder = self._get_reminder(address, db_session)

        hours = args["hours"]
        seconds = hours * 3600
        if hours < 1 or hours > 120:
            self.send_txt(
                address,
                "Reminders can only be 1-120 hours",
                "Invalid Reminder Time"
            )
            return

        if reminder is None:
            reminder = Reminder(
                kudubot_user=address,
                reminder_time=seconds
            )
            db_session.add(reminder)
        else:
            reminder.reminder_time = seconds

        db_session.commit()

        self.send_txt(
            address,
            "Reminder set to {} hours".format(hours),
            "Reminder Time set"
        )

    @Bot.auth_required
    def _on_deactivate_reminder(
            self,
            address: Address,
            _: Dict[str, Any],
            db_session: Session
    ):
        """
        Deactivates a reminder
        :param address: The sender of the message
        :param _: Command arguments
        :param db_session: The database session to use
        :return: None
        """
        reminder = self._get_reminder(address, db_session)
        if reminder is not None:
            db_session.delete(reminder)
            db_session.commit()
        self.send_txt(address, "Reminder Deactivated", "Reminder Deactivated")

    def bg_iteration(self, _: int, db_session: Session):
        """
        Implements behaviours of the Background thread that periodically
        checks if any reminders are due
        :return: None
        """
        self.logger.info("Checking for due reminders")

        for reminder in db_session.query(Reminder).all():
            api_key = self._get_api_key(reminder.kudubot_user, db_session)

            if not api_is_authorized(api_key):
                continue

            resp = api_request("match", "get", {}, api_key)
            matches = resp["data"]["matches"]

            bets = api_request("bet", "get", {}, api_key)["data"]["bets"]
            due = reminder.get_due_matches(matches, bets)

            if len(due) > 0:
                body = "Reminders for hk-tippspiel.com:\n\n"
                for match in due:
                    body += "{} vs. {}\n".format(
                        match["home_team"]["name"],
                        match["away_team"]["name"]
                    )
                msg = TextMessage(
                    self.connection.address,
                    reminder.kudubot_user,
                    body,
                    "Reminders"
                )
                self.connection.send(msg)
                last_match = max(due, key=lambda x: x["kickoff"])
                reminder.last_reminder = last_match["kickoff"]
                db_session.commit()

        self.logger.info("Finished checking for due reminders")
