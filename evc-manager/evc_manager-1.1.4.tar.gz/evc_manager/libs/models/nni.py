""" Module that models the NNI connections """


from ..core.fix_variables import evaluate_str


class NNI(object):
    """ Network-to-Network Interface Class. """

    def __init__(self):
        self._device_a = None
        self._interface_a = None
        self._device_z = None
        self._interface_z = None
        self._name = None

    @property
    def name(self):
        """ Getter """
        return self._name

    @name.setter
    def name(self, name):
        """ Setter """
        self._name = evaluate_str(name, 'name')

    @property
    def device_a(self):
        """ Getter """
        return self._device_a

    @device_a.setter
    def device_a(self, dev_a):
        """ Setter """
        self._device_a = evaluate_str(dev_a, 'device_a')

    @property
    def interface_a(self):
        """ Getter """
        return self._interface_a

    @interface_a.setter
    def interface_a(self, int_a):
        """ Setter """
        self._interface_a = evaluate_str(int_a, 'interface_a')

    @property
    def device_z(self):
        """ Getter """
        return self._device_z

    @device_z.setter
    def device_z(self, dev_z):
        """ Setter """
        self._device_z = evaluate_str(dev_z, 'device_z')

    @property
    def interface_z(self):
        """ Getter """
        return self._interface_z

    @interface_z.setter
    def interface_z(self, int_z):
        """ Setter """
        self._interface_z = evaluate_str(int_z, 'interface_z')

    def import_dict(self, nni):
        """ Import dictionary into class """
        self.device_a = nni['node_a']
        self.interface_a = nni['interface_a']
        self.device_z = nni['node_z']
        self.interface_z = nni['interface_z']
        self.name = nni['name']
