import sys
import time
import pyudev

flask_context = pyudev.Context()

# for device in flask_context.list_devices():
#     print(device)

# sys.exit()

monitor = pyudev.Monitor.from_netlink(flask_context)


def on_event(action, device):
    print(f"action={action} device={device}")
    for config in device.properties.items():
        print(f"   config={config}")


observer = pyudev.MonitorObserver(monitor, on_event)

try:
    print('start')
    observer.start()
    time.sleep(15)
finally:
    print('stop')
    observer.stop()
