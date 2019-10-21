""" This module is used to collect the current config from the
backend. The current config class is used to separate what is
admin from configuration info. """


from .nni import NNI
from ..core.fix_variables import evaluate_str
from ..core.fix_variables import evaluate_integer


class CurrentConfig(object):
    """ CurrentConfig Class """

    def __init__(self):
        self._is_active = False
        self._is_optimized = False
        self._is_expired = False
        self._is_up = False
        self._is_backup = False
        self._current_path = False
        self._backend = None
        self._backend_evc_id = None

    @property
    def is_active(self):
        """ Getter """
        return self._is_active

    @is_active.setter
    def is_active(self, status):
        """ Setter """
        if isinstance(status, bool):
            self._is_active = status
        elif isinstance(status, str):
            status = status.lower()
            if status in ['active', 'up']:
                self._is_active = True
            elif status in ['deactived', 'down', 'scheduled']:
                self._is_active = False
            else:
                raise ValueError('is_active must be bool or active/deactived')
        else:
            raise ValueError('is_active must be bool or active/deactived')

    @property
    def is_optimized(self):
        """ Getter """
        return self._is_optimized

    @is_optimized.setter
    def is_optimized(self, status):
        """ Setter """
        if isinstance(status, bool):
            self._is_optimized = status
        else:
            raise ValueError('is_optimized must be bool')

    @property
    def is_expired(self):
        """ Getter """
        return self._is_expired

    @is_expired.setter
    def is_expired(self, status):
        """ Setter """
        if isinstance(status, bool):
            self._is_expired = status
        else:
            raise ValueError('is_expired must be bool')

    @property
    def is_up(self):
        """ Getter """
        return self._is_up

    @is_up.setter
    def is_up(self, status):
        """ Setter """
        if isinstance(status, bool):
            self._is_up = status
        else:
            raise ValueError('is_up must be bool')

    @property
    def is_backup(self):
        """ Getter """
        return self._is_backup

    @is_backup.setter
    def is_backup(self, status):
        """ Setter """
        if isinstance(status, bool):
            self._is_backup = status

        else:
            raise ValueError('is_backup must be bool')

    @property
    def current_path(self):
        """ Getter """
        return self._current_path

    @current_path.setter
    def current_path(self, current_path):
        """ Setter """
        if isinstance(current_path, list):
            for path in current_path:
                if isinstance(path, list):
                    for nni in path:
                        if not isinstance(nni, NNI):
                            raise ValueError('Must be a list of NNIS')

        self._current_path = current_path

    @property
    def backend(self):
        """ Getter """
        return self._backend

    @backend.setter
    def backend(self, backend):
        """ Setter """
        self._backend = evaluate_str(backend, 'backend')

    @property
    def backend_evc_id(self):
        """ Getter """
        return self._backend_evc_id

    @backend_evc_id.setter
    def backend_evc_id(self, backend_evc_id):
        """ Setter """
        self._backend_evc_id = evaluate_integer(backend_evc_id, 'backend_evc_id')

    def import_json(self, curr_config):
        """ Import current config from JSON """
        self.is_active = curr_config['is_active']
        self.is_optimized = curr_config['is_optimized']
        self.is_expired = curr_config['is_expired']
        self.is_up = curr_config['is_up']
        self.is_backup = curr_config['is_backup']
        self.current_path = curr_config['current_path']
        self.backend = curr_config['backend']
        self.backend_evc_id = curr_config['backend_evc_id']
