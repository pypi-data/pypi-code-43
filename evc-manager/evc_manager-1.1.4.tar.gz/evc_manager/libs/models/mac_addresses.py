""" Class to manage the list of Mac-addresses """


from .mac_address import MacAddress


class MacAddresses(object):
    """ Class to manage the list of Mac-addresses """

    def __init__(self):
        self._mac_addresses = list()

    @property
    def mac_addresses(self):
        """ Getter """
        return self._mac_addresses

    @mac_addresses.setter
    def mac_addresses(self, mac_addresses):
        """ Setter """
        if not isinstance(mac_addresses, list):
            raise ValueError("Mac_addresses must be provided as a list")

        for mac_address in mac_addresses:
            self._mac_addresses.append(MacAddress(mac_address))

    def add_mac_address(self, mac_address):
        """ Add a MAC to _mac_addresses """
        self._mac_addresses.append(MacAddress(mac_address))
