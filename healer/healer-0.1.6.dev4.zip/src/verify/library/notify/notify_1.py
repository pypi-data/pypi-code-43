"""
GLIB
https://askubuntu.com/questions/108764/how-do-i-send-text-messages-to-the-notification-bubbles
"""

# from gi.repository import GObject

import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify

# class NotifyManager(GObject.Object):
#
#     def __init__(self):
#         super().__init__()
#         Notify.init("application")
#
#     def show(self, title, text, file_path_to_icon=""):
#         notify = Notify.Notification.new(title, text, file_path_to_icon)
#         notify.show()

# manager = NotifyManager()
# manager.show("this is a title", "this is some text")

Notify.init("application")
notify = Notify.Notification.new("this is a title", "this is some text")
notify.show()
