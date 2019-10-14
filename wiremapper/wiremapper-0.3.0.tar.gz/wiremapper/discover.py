import dbus


def get_paired_devices():
    bus = dbus.SystemBus()
    manager = dbus.Interface(bus.get_object('org.bluez', '/'), 'org.freedesktop.DBus.ObjectManager')
    for path, ifaces in manager.GetManagedObjects().items():
        if 'org.bluez.Device1' in ifaces and str(ifaces['org.bluez.Device1']['Address']).startswith('00:13:43'):
            yield (str(ifaces['org.bluez.Device1']['Address']), str(ifaces['org.bluez.Device1']['Alias']))
