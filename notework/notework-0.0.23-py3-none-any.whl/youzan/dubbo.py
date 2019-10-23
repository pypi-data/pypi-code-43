import demjson
import requests


class dubbo:
    def __init__(self, tether_host=None, interface=None, method=None):
        self.tether_host = tether_host
        self.interface = interface
        self.method = method

    def get_dubbo_result(self, data):
        headers = {
            'Content-Type': 'application/json',
            'X-Request-Protocol': 'dubbo'
        }
        data = demjson.encode(data)
        url = '{}/soa/{}/{}'.format(self.tether_host, self.interface, self.method)
        response = requests.post(url, headers=headers, data=data)
        return demjson.decode(response.text)
