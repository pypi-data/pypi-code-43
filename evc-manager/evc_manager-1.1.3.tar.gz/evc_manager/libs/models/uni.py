"""  User Network Interface (UNI) Class """


from .mac_addresses import MacAddresses
from .tag import Tag
from ..core.fix_variables import evaluate_str


class UNI(MacAddresses):
    """ User-to-Network Interface Class. """

    def __init__(self):
        super().__init__()
        self._device = None
        self._interface_name = None
        self._interface_description = None
        self._tag = Tag()

    @property
    def device(self):
        """ Getter """
        return self._device

    @device.setter
    def device(self, device_name):
        """ Setter """

        self._device = evaluate_str(device_name, 'device_name')

    @property
    def interface_name(self):
        """ Getter """
        return self._interface_name

    @interface_name.setter
    def interface_name(self, intf_name):
        """ Setter """
        self._interface_name = evaluate_str(intf_name, 'interface_name')

    @property
    def interface_description(self):
        """ Getter """
        return self._interface_description

    @interface_description.setter
    def interface_description(self, desc):
        """ Setter """
        self._interface_description = evaluate_str(desc, 'description')

    @property
    def tag(self):
        """ Getter """
        return self._tag

    @tag.setter
    def tag(self, uni_tag):
        """ Setter """
        self._tag = uni_tag
