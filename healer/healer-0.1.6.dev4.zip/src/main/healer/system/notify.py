"""
System desktop notification

https://lazka.github.io/pgi-docs/Notify-0.7/classes/Notification.html
"""

from __future__ import annotations

import enum
import logging
import os
from dataclasses import dataclass
from typing import List

from healer.support.typing import AutoNameEnum

import gi  # isort:skip
gi.require_version('Notify', '0.7')  # isort:skip
from gi.repository import Notify  # isort:skip

logger = logging.getLogger(__name__)


@dataclass
class NotifyUnit:
    """
    Resusalbe desktop notification unit
    """

    unit_title:str = None
    unit_message:str = None
    unit_icon_name:str = None
    unit_expire_time:int = Notify.EXPIRES_NEVER

    notification:Notify.Notification = None

    def __post_init__(self):
        self.open()

    def has_active(self) -> bool:
        return self.notification is not None

    def open(self):
        if not self.notification:
            self.notification = Notify.Notification.new(
                summary=self.title,
                body=self.message,
                icon=self.icon_name,
            )

    def close(self):
        if self.notification:
            self.notification.close()
            self.notification = None

    def update(self):
        if self.notification:
            self.notification.set_timeout(self.unit_expire_time)
            self.notification.update(
                summary=self.title,
                body=self.message,
                icon=self.icon_name,
            )
            try:
                self.notification.show()  # fails when missing display
            except Exception as error:
                logger.warning(f"failure: {error}")

    @property
    def title(self) -> str:
        return self.unit_title

    @title.setter
    def title(self, title:str) -> None:
        if self.unit_title == title:
            return
        self.unit_title = title
        self.update()

    @property
    def message(self) -> str:
        return self.unit_message

    @message.setter
    def message(self, message:str) -> None:
        if self.unit_message == message:
            return
        self.unit_message = message
        self.update()

    @property
    def icon_name(self) -> str:
        return self.unit_icon_name

    @icon_name.setter
    def icon_name(self, icon_name:str) -> None:
        if self.unit_icon_name == icon_name:
            return
        self.unit_icon_name = icon_name
        self.update()


@enum.unique
class NotifyEnv(AutoNameEnum):
    DISPLAY = enum.auto()
    DBUS_SESSION_BUS_ADDRESS = enum.auto()


class NotifySupport:
    """
    DBUS notification configuration
    """

    runtime_user_dir = "/run/user"  # user login resources

    @staticmethod
    def runtime_socket(user_id:str) -> str:
        "user dbus session access"
        return f"{NotifySupport.runtime_user_dir}/{user_id}/bus"

    @staticmethod
    def runtime_dbus_url(user_id:str) -> str:
        "user dbus session access"
        return f"unix:path={NotifySupport.runtime_socket(user_id)}"

    @staticmethod
    def runtime_user_list() -> List[str]:
        "list users with dbus session"
        user_list = []
        for user_id in os.listdir(NotifySupport.runtime_user_dir):
            user_bus = NotifySupport.runtime_socket(user_id)
            if os.path.exists(user_bus):
                user_list.append(user_id)
        return user_list

    @staticmethod
    def configure_user_bus() -> str:
        "select user for dbus notifications"
        # TODO config
        Notify.init("HEALER")  # application title name
        user_list = NotifySupport.runtime_user_list()
        if user_list:
            user_id = user_list[0]
            logger.info(f"notify user: {user_id}")
            os.environ[NotifyEnv.DISPLAY] = os.environ.get(NotifyEnv.DISPLAY, ':0')
            os.environ[NotifyEnv.DBUS_SESSION_BUS_ADDRESS] = NotifySupport.runtime_dbus_url(user_id)
        else:
            logger.warning(f"no user dbus")


NotifySupport.configure_user_bus()
