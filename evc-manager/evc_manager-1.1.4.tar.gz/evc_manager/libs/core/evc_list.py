""" Module responsible for hosting all EVC imported from backend
or from YAML file. Any operation performed by evc_manager over an EVC
has to pass through this module to guarantee we have the right EVC. """


from .evc_to_dict import convert_class


class EvcsList(object):
    """ List of EVCs """

    def __init__(self, evc_list=None):
        self._evcs = list()
        if evc_list:
            self.evcs = evc_list

    @property
    def evcs(self):
        """ Getter """
        return self._evcs

    @evcs.setter
    def evcs(self, evc_list):
        """ Setter """
        # TODO: Validate input
        self._evcs = evc_list

    def to_dict(self):
        """ Convert to self to dictionary """
        return convert_class(self.evcs)

    def find(self, target_evc):
        """ Return True if a specific EVC already exists """
        for evc in self.evcs:
            if target_evc == evc:
                return evc
        return False
