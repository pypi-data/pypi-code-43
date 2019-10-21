""" Class Tag part of EthernetVirtualCircuit"""


class Tag(object):
    """ Class Tag part of EthernetVirtualCircuit"""

    def __init__(self):
        self._type = 'vlan'  # it has to be a str. 'vlan' is the default
        self._value = 0  # it has to be an int

    @property
    def type(self):
        """ Tag Type property

        :return: self._type
        """
        return self._type

    @type.setter
    def type(self, uni_type):
        """ Tag type setter

        :param uni_type: tag type. Must be or 'vlan' or 'mpls'
        """
        if isinstance(uni_type, str):
            uni_type = uni_type.lower()
        else:
            msg = "Error: Tag Value must be or 'vlan' or 'mpls'"
            raise ValueError(msg)

        if uni_type not in ['vlan', 'mpls']:
            msg = "Error: Tag Value must be or 'vlan' or 'mpls'"
            raise ValueError(msg)

        self._type = uni_type

    @property
    def value(self):
        """ Tag Value property

        :return: self._value
        """
        return self._value

    @value.setter
    def value(self, uni_value):
        """ Tag Value setter

        :param uni_value: tag value. Must be int from [-1,1-4095]
        :return:
        """
        if not isinstance(uni_value, int):
            try:
                uni_value = int(uni_value)
            except TypeError:
                msg = "Error: Tag Value must be integer"
                raise ValueError(msg)

        if self.is_vlan() and not (uni_value == -1 or 1 <= uni_value <= 4095):
            msg = "Error: VLAN IDs must be int and be -1 or between 1 and 4095"
            raise ValueError(msg)

        if not self.is_vlan() and not 1 <= uni_value <= 1048576:
            msg = "Error: MPLS labels must be integer and between 1-1048576"
            raise ValueError(msg)

        self._value = int(uni_value)

    def is_vlan(self):
        """

        :return:
        """
        if self.type in ['mpls']:
            return False
        return True
