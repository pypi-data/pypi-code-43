from pytmg.TMGTransceiver import TMGTransceiver

class TMGNetworkDevice:
    def __init__(self, input, product_family, network_family_data_sheet):
        self.result = input
        self.product_id = self.result["productId"]
        self.product_family = product_family
        self.network_family_data_sheet = network_family_data_sheet
        self.transceivers = []
        for transceiver in self.result["transceivers"]:
            self.transceivers.append(TMGTransceiver(transceiver))
