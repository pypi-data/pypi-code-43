import logging

from collections import namedtuple
from enum import IntEnum

from conductor.asset_group import AssetGroup
from conductor.event_count import EventCount
from conductor.devices.gateway import Gateway
from conductor.subject import UplinkSubject, DownlinkSubject, UplinkMessage
from conductor.tokens import AppToken
from conductor.util import Version, parse_time


LOG = logging.getLogger(__name__)


# TODO: Format documenation.

class ModuleUplinkMessage(UplinkMessage):

    SignalData = namedtuple('SignalData', ['spreading_factor', 'snr', 'rssi',
                                           'frequency', 'channel'])

    @property
    def signal_data(self):
        vals = self._data.get('value')
        return self.SignalData(int(vals.get('sf')),
                               int(vals.get('snr')),
                               int(vals.get('rssi')),
                               int(vals.get('frequency')),
                               int(vals.get('channelNumber')))

    @property
    def port(self):
        vals = self._data.get('value')
        return int(vals.get('port'))

    @property
    def module(self):
        vals = self._data.get('value')
        return Module(self.session, vals.get('module'), self.instance)

    @property
    def gateway(self):
        vals = self._data.get('value')
        return Gateway(self.session, vals.get('gateway'), self.instance)


class Module(UplinkSubject, DownlinkSubject, EventCount):
    """ Represents a single Module (end node). """
    subject_name = 'node'
    msgObj = ModuleUplinkMessage

    ALLOWED_PORT_RANGE = range(0, 128)

    class DownlinkMode(IntEnum):
        OFF = 0,
        ALWAYS = 1
        MAILBOX = 2

    def send_message(self, payload, gateway_addr=None, acked=True,
                     time_to_live_s=60.0, port=0, priority=10):
        """
        Sends a downlink message to a node. If the `gateway_addr` is specified,
        then the message will be sent through that gateway. Otherwise,
        Conductor will route the message automatically.

        `payload` should be a bytearray or bytes object.

        Returns a `DownlinkMessage` object, which can be used to poll for the
        message's status or cancel the message.
        """
        if port not in self.ALLOWED_PORT_RANGE:
            raise ValueError("Port must be within [0, 127]")

        body = {}
        if gateway_addr:
            body['commandRoutes'] = {'linkAddresses': [self.subject_id +
                                                       '!101!' + gateway_addr]}
        else:
            body['commandTargets'] = {'targetNodeAddresses': [self.subject_id]}

        return self._send_message_with_body(body, payload, acked,
                                            time_to_live_s, port, priority)

    def get_routes(self):
        """ Gets the routes for the subject """
        url = '{}/module/{}/routes'.format(self.client_edge_url,
                                           self.subject_id)
        return self._get(url)

    def get_asset_groups(self):
        """ Returns all the AssetGroups the module is a part of. """
        url = '{}/assetGroup/node/{}'.format(self.network_asset_url,
                                             self.subject_id)
        return [AssetGroup(self.session, x['id'], _data=x)
                for x in self._get(url)]

    @property
    def downlink_mode(self):
        """ Returns the downlink mode of the module. """
        val = self._md.get('downlinkMode')
        return self.DownlinkMode(int(val)) if val else None

    @property
    def module_firmware_version(self):
        """ Returns the Symphony Link Module Version. """
        val = self._md.get('firmware_version')
        return Version(val[:1], val[2:3], val[4:]) if val else None

    @property
    def last_modified_time(self):
        """ Returns the last time the Access Point was modified. """
        val = self._md.get('lastModified')
        return parse_time(val) if val else None

    @property
    def last_mailbox_request_time(self):
        """ Returns the last time the module requested it's mailbox. """
        val = self._md.get('mailboxRequestTime')
        return parse_time(val) if val else None

    @property
    def initial_detection_time(self):
        """ Returns the last time the Access Point was modified. """
        val = self._data.get('initialDetectionTime')
        return parse_time(val) if val else None

    @property
    def registration_time(self):
        """ Returns the last time the Access Point was modified. """
        val = self._data.get('registrationTime')
        return parse_time(val) if val else None

    @property
    def application_token(self):
        """ Returns the Application Token the module is registered to. """
        val = self._data.get('registrationToken')
        return AppToken(self.session, val) if val else None

    @property
    def registered_by_gateway(self):
        """ Returns the Gateway that registered the AccessPoint. """
        val = self._md.get("registeredByGateway")
        try:
            return Gateway(self.session, val, self.instance)
        except Exception as e:
            LOG.exception(e)
            return None


class LTEmModuleUplinkMessage(UplinkMessage):

    SignalData = namedtuple('SignalData', ['cell_id', 'cell_tac', 'rsrp',
                                           'rsrq', 'imei', 'iccid'])

    @property
    def signal_data(self):
        vals = self._data.get('value')
        return self.SignalData(int(vals.get('cellId')),
                               int(vals.get('cellTac')),
                               int(vals.get('cellRsrp')),
                               int(vals.get('cellRsrq')),
                               int(vals.get('imei')),
                               int(vals.get('iccid')))

    @property
    def module(self):
        vals = self._data.get('value')
        return LTEmModule(self.session, vals.get('module'), self.instance)


# TODO: Format Documenation.

class LTEmModule(Module):
    """ Represents a single LTE-M Module (end node). """
    subject_name = 'lte'
    msgObj = LTEmModuleUplinkMessage

    def _post_status_update(self, status):
        """" Updates the status of an LTE module. """
        url = '{}/lte/{}/{}'.format(self.network_asset_url, self.subject_id,
                                    status)
        return self._post(url)

    def activate(self):
        """ Activate an LTE device. """
        return self._post_status_update('activate')

    def deactivate(self):
        """ Deactivate an LTE device. """
        return self._post_status_update('deactivate')

    def restore(self):
        """ Restore an LTE device. """
        return self._post_status_update('restore')

    def suspend(self):
        """ Suspend an LTE device. """
        return self._post_status_update('suspend')

    @property
    def cell_data_usage(self):
        """ Returns the cell data usage of the LTEm module. """
        val = self._md.get('cellDataUsage')
        return int(val) if val else None

    @property
    def last_cell_id(self):
        """ Returns the ID of the last cell tower the LTEm module transmitted
        through. """
        val = self._md.get('cellId')
        return int(val) if val else None

    @property
    def last_cell_tac(self):
        """ Returns the TAC of the last cell tower the LTEm module transmitted
        through. """
        val = self._md.get('cellTac')
        return int(val) if val else None

    @property
    def iccid(self):
        """ Returns the ICCID of the LTEm module. """
        val = self._md.get('iccid')
        return int(val) if val else None

    @property
    def imei(self):
        """ Returns the IMEI of the LTEm module. """
        val = self._md.get('imei')
        return int(val) if val else None

    @property
    def ip_address(self):
        """ Returns the IP Address of the LTEm module.  """
        val = self._md.get('ipAddress')
        return val

    @property
    def version(self):
        """ Returns the software version of the LTEm module. """
        val = self._md.get('sw_ver')
        return Version(int(val[2]), int(val[4]), int(val[6])) if val else None

    @property
    def sqn_versions(self):
        """ Returns the Sequans versions of the LTEm module as a tuple. """
        val1 = self._md.get('lte_ver1')
        val2 = self._md.get('lte_ver2')
        return (val1, val2)

    @property
    def provisioned_status(self):
        """ Returns the provisioned status of the LTEm module. """
        val = self._md.get('lteProvStatus')
        return val

    @property
    def mdn(self):
        """ Returns the mdn of the LTEm module. """
        val = self._md.get('mdn')
        return int(val) if val else None

    @property
    def min(self):
        """ Returns the min of the LTEm module."""
        val = self._md.get('min')
        return int(val) if val else None

    @property
    def msisdn(self):
        """ Returns the msisdn of the LTEm module."""
        val = self._md.get('msisdn')
        return int(val) if val else None

    @property
    def last_slot(self):
        """ Returns the last slot of the LTEm module."""
        val = self._md.get('slot')
        return int(val) if val else None
