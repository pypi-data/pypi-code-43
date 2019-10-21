""" Class to manage UNIs """

import copy
from .mac_address import MacAddress
from .uni import UNI


class UNIS(object):
    """ Class to manage the list of UNIs.
    Parent class of EthernetVirtualCircuit """

    def __init__(self):
        super(UNIS, self).__init__()
        self._unis = list()

    @property
    def unis(self):
        """ Getter """
        return self._unis

    @unis.setter
    def unis(self, unis):
        """ Setter """
        if not isinstance(unis, list):
            raise ValueError('UNIS must be a list of UNIs')

        if not unis:
            raise ValueError('UNIS must be a non-empty list of UNIs')

        for uni in unis:
            if not isinstance(uni, UNI):
                raise ValueError('UNIS must be a list of UNIs')

        self._unis = unis

    def import_unis(self, unis):
        """ Import UNIS from a list of dictionaries """
        new_unis = list()
        for endpoint in unis:
            uni = UNI()
            uni.device = endpoint['device']
            uni.interface_name = endpoint['interface_name']
            if 'interface_description' in endpoint:
                uni.interface_description = endpoint['interface_description']
            if 'type' in endpoint['tag']:
                uni.tag.type = endpoint['tag']['type']
            else:
                uni.tag.type = "vlan"
            uni.tag.value = endpoint['tag']['value']
            if 'mac_addresses' in endpoint:
                for mac_addr in endpoint['mac_addresses']:
                    uni.mac_addresses.append(MacAddress(mac_addr['mac_address']))
            new_unis.append(copy.deepcopy(uni))
            del uni
        self.unis = new_unis  # pylint: disable=W0201
