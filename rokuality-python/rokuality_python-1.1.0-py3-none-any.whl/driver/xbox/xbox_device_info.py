
class XBoxDeviceInfo():
    
    os_version = None
    dev_mode = None
    os_edition = None
    console_type = None
    console_id = None
    device_id = None
    serial_number = None

    def __init__(self, info_json):
        self.os_version = info_json["OsVersion"]
        self.dev_mode = info_json["DevMode"]
        self.os_edition = info_json["OsEdition"]
        self.console_type = info_json["ConsoleType"]
        self.console_id = info_json["ConsoleId"]
        self.device_id = info_json["DeviceId"]
        self.serial_number = info_json["SerialNumber"]

    def get_os_version(self):
        return self.os_version

    def get_dev_mode(self):
        return self.dev_mode

    def get_os_edition(self):
        return self.os_edition

    def get_console_type(self):
        return self.console_type

    def get_console_id(self):
        return self.console_id

    def get_device_id(self):
        return self.device_id

    def get_serial_number(self):
        return self.serial_number