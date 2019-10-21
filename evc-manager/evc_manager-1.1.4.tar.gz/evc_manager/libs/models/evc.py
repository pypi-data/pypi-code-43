"""
    Main Ethernet Virtual Circuit Class.
    Created to centralize and evaluate each param.
"""

from .unis import UNIS
from .current_config import CurrentConfig
from .metrics import Metrics
from .monitoring import Monitoring
from .notifications import Notifications
from .evc_paths import EvcPath
from ..core.fix_variables import evaluate_str
from ..core.fix_variables import evaluate_integer


class EthernetVirtualCircuit(UNIS, EvcPath):
    """ EVC Main Class"""

    def __init__(self):
        super().__init__()
        self._name = 0
        self._provisioning_time = 0
        self._decommissioning_time = 0
        self._tenant = 0
        self._priority = 0
        self._external_id = 0
        self._metrics = Metrics()
        self._current_config = CurrentConfig()
        self._monitoring = Monitoring()
        self._notifications = Notifications()

    @property
    def name(self):
        """ Getter """
        return self._name

    @name.setter
    def name(self, evc_name):
        """ Setter """
        self._name = evaluate_str(evc_name, 'name')

    @property
    def provisioning_time(self):
        """ Getter """
        return self._provisioning_time

    @provisioning_time.setter
    def provisioning_time(self, time):
        """ Setter """
        self._provisioning_time = evaluate_integer(time, 'time')

    @property
    def decommissioning_time(self):
        """ Getter """
        return self._decommissioning_time

    @decommissioning_time.setter
    def decommissioning_time(self, time):
        """ Setter """
        self._decommissioning_time = evaluate_integer(time, 'time')

    @property
    def tenant(self):
        """ Getter """
        return self._tenant

    @tenant.setter
    def tenant(self, tenant):
        """ Setter """
        self._tenant = evaluate_str(tenant, 'tenant')

    @property
    def priority(self):
        """ Getter """
        return self._priority

    @priority.setter
    def priority(self, priority):
        """ Setter """
        self._priority = evaluate_integer(priority, 'priority')

    @property
    def external_id(self):
        """ Getter """
        return self._external_id

    @external_id.setter
    def external_id(self, external_id):
        """ Setter """
        self._external_id = evaluate_str(external_id, 'external_id')

    @property
    def current_config(self):
        """ Getter """
        return self._current_config

    @current_config.setter
    def current_config(self, curr_config):
        """ Setter """
        if isinstance(curr_config, CurrentConfig):
            self._current_config = curr_config
        else:
            raise ValueError('CurrentConfig must use Class CurrentConfig')

    @property
    def metrics(self):
        """ Getter """
        return self._metrics

    @metrics.setter
    def metrics(self, metrics):
        """ Setter """
        if isinstance(metrics, Metrics):
            self._metrics = metrics
        else:
            raise ValueError('Metrics must use Class Metrics')

    @property
    def monitoring(self):
        """ Getter """
        return self._monitoring

    @monitoring.setter
    def monitoring(self, monitoring):
        """ Setter """
        if isinstance(monitoring, Monitoring):
            self._monitoring = monitoring
        else:
            raise ValueError('monitoring must use Class Monitoring')

    @property
    def notifications(self):
        """ Getter """
        return self._notifications

    @notifications.setter
    def notifications(self, notifications):
        """ Setter """
        if isinstance(notifications, Notifications):
            self._notifications = notifications
        else:
            raise ValueError('notifications must use Class Notifications')

    def __eq__(self, other):
        """ Compare EVCs """
        if self.name == other.name:
            return True

        if len(self.unis) == len(other.unis) and len(self.unis) == 0:
            return True

        if len(self.unis) == len(other.unis) and len(self.unis) == 2:
            if self.unis[0].interface_name == other.unis[0].interface_name:
                if self.unis[1].interface_name == other.unis[1].interface_name:
                    if self.unis[0].tag.value == other.unis[0].tag.value:
                        if self.unis[1].tag.value == other.unis[1].tag.value:
                            return True
            elif self.unis[1].interface_name == other.unis[0].interface_name:
                if self.unis[0].interface_name == other.unis[1].interface_name:
                    if self.unis[1].tag.value == other.unis[0].tag.value:
                        if self.unis[0].tag.value == other.unis[1].tag.value:
                            return True

        return False

    def is_using_backup_path(self):
        """ Indicate if it is using backup path """
        return self.current_config.is_backup
