
import sys
import dbus
import dbus.mainloop.glib

BT_ROOT = "org.bluez"
ADAPTER_INTERFACE = BT_ROOT + ".Adapter1"
DEVICE_INTERFACE = BT_ROOT + ".Device1"

MANAGER_INTERFACE = "org.freedesktop.DBus.ObjectManager"


def pretty(bucket, indent=2):
    for key, value in bucket.items():
        print('\t' * indent + str(key))
        if isinstance(value, dict):
            pretty(value, indent + 1)
        else:
            print('\t' * (indent + 1) + str(value))


if __name__ == '__main__':

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    sys_bus = dbus.SystemBus()

    # ProxyObject
    bluez = sys_bus.get_object("org.bluez", "/")
    print(bluez)

    # Interface of ProxyObject
    bluez_manager = dbus.Interface(bluez, MANAGER_INTERFACE)
    print(bluez_manager)

    object_dict = bluez_manager.GetManagedObjects()
#     pretty(object_dict)

#     sys.exit()

    path_list = [
        path for path, face_dict in object_dict.items()
        if DEVICE_INTERFACE in face_dict.keys()
    ]

    for path in path_list:
        print(f"path={path}")
        face_dict = object_dict[path]
        print(f"face_dict={face_dict}")
