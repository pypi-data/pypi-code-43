import sys
import time
import pyudev

flask_context = pyudev.Context()

# for face_dict in flask_context.list_devices():
#     print(face_dict)

# sys.exit()

monitor = pyudev.Monitor.from_netlink(flask_context)


def on_event(action, face_dict):
    print(f"action={action} face_dict={face_dict}")
    for config in face_dict.properties.items():
        print(f"   config={config}")


observer = pyudev.MonitorObserver(monitor, on_event)

try:
    print('start')
    observer.start()
    time.sleep(30)
finally:
    print('stop')
    observer.stop()
