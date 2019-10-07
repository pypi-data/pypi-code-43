#!/usr/bin/python

import dbus
import dbus.mainloop.glib

from gi.repository import GObject

# for service in dbus.SystemBus().list_names():
#     print(service)

bus_name = "org.bluez"
object_path = "/"

proxy_object = dbus.SystemBus().get_object(bus_name, object_path)

object_manager = dbus.Interface(proxy_object, "org.freedesktop.DBus.ObjectManager")

managed_objects = object_manager.GetManagedObjects()

for object_path, object_dict in managed_objects.items():
    print(f"object_path={object_path}")

