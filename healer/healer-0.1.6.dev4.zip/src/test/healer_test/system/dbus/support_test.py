
from healer.system.dbus.support import *


def test_has_system_busname():
    print()

    entry_name_list = [
        'org.bluez',
        'org.freedesktop.DBus'
    ]

    for entry_name  in entry_name_list:
        has_entry = SupportDBUS.has_system_bus_name(entry_name)
        print(f"{entry_name} : {has_entry}")
