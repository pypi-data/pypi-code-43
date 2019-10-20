""" Generic backend for future upgrades. """


class Backend(object):
    """ Generic backend for future upgrades. """

    def __init__(self):
        self.user = None
        self.password = None
        self.url = None
        self.tenant = None
        self.session_request = None
        self.requester = None

    def authenticate(self):
        """ Authenticate using credentials provided via CLI """
        return True

    def get_evcs(self):
        """ Get all EVC """
        return True

    def add_evcs(self, new_evcs):
        """ Add EVC based on the provided circuit names """
        return True

    def change_evcs(self, new_evcs):
        """ Change EVC based on the provided circuit names """
        return True

    def delete_evcs(self, evcs_to_delete):
        """ Delete EVC with the provided circuit IDs """
        return True

    def move_evcs(self, evcs_to_move):
        """ Move EVC out of a provided NNI """
        return True
