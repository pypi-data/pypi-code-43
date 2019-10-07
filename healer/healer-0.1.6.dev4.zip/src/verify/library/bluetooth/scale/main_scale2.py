import blus

command = "fe 02 01 00 b9 35 01 8e".split()
command = bytes(map(lambda x: int(x, 16), command))
print(f"command: {command}")

scale_addr = "88:1B:99:05:5B:59"
scale_uuid = "00001101-0000-1000-8000-00805f9b34fb"


class Observer(blus.DeviceObserver):

    def seen(self, bluez_manager, path, face_dict):
        alias = face_dict.get("Alias")
        print("Seeing %s at %s" % (alias, path))


blus.DeviceManager(Observer()).scan()
