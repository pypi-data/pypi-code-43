#!/usr/bin/python

import dbus
import dbus.mainloop.glib

from gi.repository import GObject

for service in dbus.SystemBus().list_names():
    print(service)

print(f"-------------")

for service in dbus.SystemBus().list_names():
    if 'org.bluez' in str(service):  # dbus.String
        print(f"PRESENT: {service}")
