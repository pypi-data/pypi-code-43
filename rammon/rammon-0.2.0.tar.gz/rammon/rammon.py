import re
import psutil
from typing import Union
from pydbus import SessionBus
from gi.repository import GLib
from rammon.config import conf
from rammon.logging import logger


class RamMonitor:
    def __init__(self):
        self.loop = GLib.MainLoop()
        self.bus = SessionBus()
        self.notifications = self.bus.get(".Notifications")

        self.last_notification_id: int = 0
        self.snoozed = dict()

    def on_action(self, notification_id: int, action: str):
        logger.debug(f"Action(notification_id={notification_id!r}, action={action!r})")
        if self.last_notification_id == notification_id:
            snooze = re.match(r"snooze-([a-z_-]+)", action)
            if snooze:
                self.snooze(snooze.group(1))

    def on_dismiss(self, notification_id: int, reason: int):
        logger.debug(f"Dismiss(notification_id={notification_id!r}, reason={reason!r})")

    def snooze(self, level):
        self.snoozed[level] = True
        logger.info(f"Snoozing level '{level}' for {conf.SNOOZE_DURATION_SECONDS}s")
        GLib.timeout_add_seconds(conf.SNOOZE_DURATION_SECONDS, self.unsnooze, level)

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
            self.last_notification_id = self.notifications.Notify(
                "RAM Monitor",
                self.last_notification_id,
                icon,
                title,
                description,
                ["default", "Dismiss", f"snooze-{level}", "Snooze"],
                {},
                conf.NOTIFICATION_TIMEOUT_MS,
            )

    def check_and_loop(self):
        memory_usage = psutil.virtual_memory()
        if memory_usage.percent > conf.CRITICAL_PERCENT_USED:
            self.notify("Critical", f"{memory_usage.percent}% Memory Used", "error")
        elif memory_usage.percent > conf.WARNING_PERCENT_USED:
            self.notify("Low", f"{memory_usage.percent}% Memory Used", "warning")
        GLib.timeout_add_seconds(conf.POLL_PERIOD_SECONDS, self.check_and_loop)

    def start(self):
        GLib.timeout_add_seconds(1, self.check_and_loop)
        self.notifications.onActionInvoked = self.on_action
        self.notifications.onNotificationClosed = self.on_dismiss
        self.loop.run()
        try:
            self.notifications.CloseNotification(self.last_notification_id)
        except GLib.GError:
            pass

    def stop(self, *args):
        logger.info("Stopping rammon on request...")
        self.loop.quit()
