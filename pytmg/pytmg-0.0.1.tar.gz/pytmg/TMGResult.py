from pytmg.TMGNetworkDevice import TMGNetworkDevice

class TMGResult:
    def __init__(self, input):
        self.result = input
        self.total_count = self.result["totalCount"]
        self.network_devices = []
        for product_family in self.result["networkDevices"]:
            for network_device in product_family["networkAndTransceiverCompatibility"]:
                self.network_devices.append(TMGNetworkDevice(
                    network_device,
                    product_family["productFamily"],
                    product_family["networkFamilyDataSheet"]))
