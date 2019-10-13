import json
import requests
from pytmg.TMGResult import TMGResult


class TMG:
    def __init__(self):
        self.search_url = "https://tmgmatrix.cisco.com/public/api/networkdevice/search"

    def _search(self, cable_type=[], data_rate=[], form_factor=[],
                reach=[], search_input=[], os_type=[],
                transceiver_product_family=[],
                transceiver_product_id=[],
                network_device_product_family=[],
                network_device_product_id=[]):
        body  = {
            "cableType": cable_type,
            "dataRate": data_rate,
            "formFactor": form_factor,
            "reach": reach,
            "searchInput": search_input,
            "osType": os_type,
            "transceiverProductFamily": transceiver_product_family,
            "transceiverProductID": transceiver_product_id,
            "networkDeviceProductFamily": network_device_product_family,
            "networkDeviceProductID": network_device_product_id
        }
        headers = {
            "content-type": "application/json"
        }

        res = requests.post(self.search_url,
                            json=body,
                            headers=headers)
        res.raise_for_status()
        return res.json()

    def search(self, **kwargs):
        return self._search(
            cable_type=kwargs.get("cable_type", []),
            data_rate=kwargs.get("data_rate", []),
            form_factor=kwargs.get("form_factor", []),
            reach=kwargs.get("reach", []),
            search_input=kwargs.get("search_input", []),
            os_type=kwargs.get("os_type", []),
            transceiver_product_family=kwargs.get("transceiver_product_family", []),
            transceiver_product_id=kwargs.get("transceiver_product_id", []),
            network_device_product_family=kwargs.get("network_device_product_family", []),
            network_device_product_id=kwargs.get("network_device_product_id", []),
        )

    def search_device(self, search_device):
        search_terms = {"search_input": [search_device]}
        res = self.search(**search_terms)
        return TMGResult(res)

    def search_devices(self, search_devices):
        tmg_results = []
        for device in search_devices:
            res = self.search_device(device)
            tmg_results.append(res)
        return tmg_results

