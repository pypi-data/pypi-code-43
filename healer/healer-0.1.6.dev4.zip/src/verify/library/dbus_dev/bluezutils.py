import dbus

BT_ROOT = "org.bluez"
ADAPTER_INTERFACE = BT_ROOT + ".Adapter1"
DEVICE_INTERFACE = BT_ROOT + ".Device1"


def get_managed_objects():
    sys_bus = dbus.SystemBus()
    bluez_manager = dbus.Interface(sys_bus.get_object("org.bluez", "/"),
                "org.freedesktop.DBus.ObjectManager")
    return bluez_manager.GetManagedObjects()


def find_adapter(pattern=None):
    return find_adapter_in_objects(get_managed_objects(), pattern)


def find_adapter_in_objects(object_dict, pattern=None):
    sys_bus = dbus.SystemBus()
    for path, ifaces in object_dict.items():
        adapter = ifaces.get(ADAPTER_INTERFACE)
        if adapter is None:
            continue
        if not pattern or pattern == adapter["Address"] or \
                            path.endswith(pattern):
            bluez_obj = sys_bus.get_object(BT_ROOT, path)
            return dbus.Interface(bluez_obj, ADAPTER_INTERFACE)
    raise Exception("Bluetooth adapter not found")


def find_device(device_address, adapter_pattern=None):
    return find_device_in_objects(get_managed_objects(), device_address,
                                adapter_pattern)


def find_device_in_objects(object_dict, device_address, adapter_pattern=None):
    sys_bus = dbus.SystemBus()
    path_prefix = ""
    if adapter_pattern:
        adapter = find_adapter_in_objects(object_dict, adapter_pattern)
        path_prefix = adapter.object_path
    for path, ifaces in object_dict.iteritems():
        face_dict = ifaces.get(DEVICE_INTERFACE)
        if face_dict is None:
            continue
        if (face_dict["Address"] == device_address and
                        path.startswith(path_prefix)):
            bluez_obj = sys_bus.get_object(BT_ROOT, path)
            return dbus.Interface(bluez_obj, DEVICE_INTERFACE)

    raise Exception("Bluetooth face_dict not found")
