import logging
import re
import psutil
from typing import Union
from pydbus import SessionBus
from gi.repository import GLib
from rammon.config import config


logger = logging.getLogger("rammon")
logger.setLevel(logging.INFO)


class RamMonitor:
    def __init__(self):
        self.loop = GLib.MainLoop()
        self.bus = SessionBus()
        self.notifications = self.bus.get(".Notifications")

        self.last_notification: int = 0
        self.snoozed = dict()

    def on_action(self, notification_id: int, action: str):
        logger.debug(f"Action(notification_id={notification_id!r}, action={action!r})")
        if self.last_notification == notification_id:
            snooze = re.match(r"snooze-([a-z_-]+)", action)
            if snooze:
                self.snooze(snooze.group(1))

    def on_dismiss(self, notification_id: int, reason: int):
        logger.debug(f"Dismiss(notification_id={notification_id!r}, reason={reason!r})")

    def snooze(self, level):
        self.snoozed[level] = True
        logger.info(f"Snoozing level '{level}' for {config.SNOOZE_DURATION_SECONDS}s")
        GLib.timeout_add_seconds(config.SNOOZE_DURATION_SECONDS, self.unsnooze, level)

    def unsnooze(self, level):
        self.snoozed.pop(level)
        logger.info(f"Unsnoozing level '{level}'")

    def notify(
        self,
        title: str = "Notification",
        description: str = "Some Text",
        level: str = "info",
        icon: Union[str, None] = None,
    ):
        icon = (
            icon
            or {
                "info": "dialog-information",
                "warning": "dialog-warning",
                "error": "dialog-error",
            }[level]
        )
        if not self.snoozed.get(level):
            self.last_notification = self.notifications.Notify(
                "RAM Monitor",
                self.last_notification,
                icon,
                title,
                description,
                ["default", "Dismiss", f"snooze-{level}", "Snooze"],
                {},
                config.NOTIFICATION_TIMEOUT_MS,
            )

    def check_and_loop(self):
        memory_usage = psutil.virtual_memory()
        if memory_usage.percent > config.CRITICAL_PERCENT_USED:
            self.notify("Critical", f"{memory_usage.percent}% Memory Used", "error")
        elif memory_usage.percent > config.WARNING_PERCENT_USED:
            self.notify("Low", f"{memory_usage.percent}% Memory Used", "warning")
        GLib.timeout_add_seconds(config.POLL_PERIOD_SECONDS, self.check_and_loop)

    def start(self):
        GLib.timeout_add_seconds(1, self.check_and_loop)
        self.notifications.onActionInvoked = self.on_action
        self.notifications.onNotificationClosed = self.on_dismiss
        self.loop.run()
