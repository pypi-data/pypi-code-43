import time

from healer.system.dbus.arkon import *


class ManagerMain(ObjectManagerDBUS):
    """
    """

    def __init__(self, name:str):
        super().__init__()
        self.name = name

#     def react_faces_added(self, entry_path:str, device:dbus.Dictionary) -> None:
#         logger.info(f"{self.name} add {entry_path}")

#     def react_faces_removed(self, entry_path:str, face_list:dbus.Array) -> None:
#         logger.info(f"{self.name} rem {entry_path}")

#     def react_props_changed(self, entry_face:str, changed:dbus.Dictionary, invalid_list:dbus.Array, entry_path:str) -> None:
#         pass
#         if entry_path != "/org/bluez/hci0/dev_88_1B_99_05_5B_59":
#         if entry_path != "/org/bluez/hci0":
#         if not entry_path.startswith("/org/bluez"):
#             return
#         logger.info(f"entry_path={entry_path} entry_face={entry_face}")
#         logger.info(f"changed={changed}")
#         logger.info(f"invalid_list={invalid_list}")


def manager_main():
    print()

    manager1 = ManagerMain("one")
    manager2 = ManagerMain("two")

    manager1.observer_start()
    manager2.observer_start()

    time.sleep(30000)

    manager1.observer_stop()
    manager2.observer_stop()


manager_main()
