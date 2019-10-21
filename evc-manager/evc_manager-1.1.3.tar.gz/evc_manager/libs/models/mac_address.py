""" MacAddress Module. """


import re


class MacAddress(object):
    """ MacAddress Class. """

    def __init__(self, mac_addr=None):
        self._mac_address = "00:00:00:00:00:00"
        if mac_addr:
            self.mac_address = mac_addr

    @property
    def mac_address(self):
        """ Getter """
        return self._mac_address

    @mac_address.setter
    def mac_address(self, mac_addr):
        """ Setter """
        if self.is_valid(mac_addr):
            self._mac_address = mac_addr
        else:
            raise ValueError('Mac-address has wrong format')

    @staticmethod
    def is_valid(mac_address):
        """ Verify if it is using the proper format
        Format has to be:
            xx:xx:xx:xx:xx:xx
            xx-xx-xx-xx-xx-xx
            x = 0-9 or a-f
        """
        if not isinstance(mac_address, str):
            return False

        if bool(re.match('^' +
                         '[\:\-]'.join(['([0-9a-f]{2})'] * 6) +
                         '$', mac_address.lower())):
            return True
        return False
