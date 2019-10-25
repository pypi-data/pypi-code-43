from asset_inventory.models.server import Server
from asset_inventory.models.device import Device


class Inventory:

    def __init__(self, ip, server: Server, devices: [Device]):
        self.ip = ip
        self.server = server
        self.devices = devices

    def serialize(self):
        server_serialize = self.server.serialize()
        devices_serialize = [device.serialize() for device in self.devices]

        inventory_serialize = {component: value for component, value in server_serialize.items()}
        inventory_serialize.update({'devices': devices_serialize})

        return inventory_serialize
