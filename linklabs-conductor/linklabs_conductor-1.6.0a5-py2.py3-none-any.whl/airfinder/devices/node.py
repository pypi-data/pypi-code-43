""" A base class for SymBLE Nodes. """
import logging

from uuid import uuid4

from conductor.airfinder.base import AirfinderUplinkMessage, AirfinderSubject
from conductor.airfinder.devices.access_point import AccessPoint
from conductor.devices.gateway import Gateway
from conductor.subject import DownlinkMessage
from conductor.tokens import AppToken
from conductor.util import find_cls, Version

LOG = logging.getLogger(__name__)


class NodeUplinkMessage(AirfinderUplinkMessage):
    """ Uplink Messages for SymBLE EndNodes. """

    @property
    def msg_type(self):
        return int(self._md.get('msgType'))

    @property
    def msg_counter(self):
        return int(self._md.get('msgCounter'))

    @property
    def symble_version(self):
        """ The version of the SymBLE Core on the Node. """
        pass

    @property
    def access_point(self):
        AccessPoint(self.session, self.instance,
                    self._md("symbleAccessPoint"))


class NodeDownlinkMessage(DownlinkMessage):
    """ Represents a SymBLE Downlink Message. """

    @property
    def target(self):
        """ The recpient SymBLE Endnode. """
        return self._data.get('subjectId')

    @property
    def acknowledged(self):
        """ Whether the downlink messge was acknowledged. """
        return self._data.get('acknowledged')

    @property
    def issued_commands(self):
        """ The Issued Commands from Conductor. """
        return [DownlinkMessage(x) for x in self._data.get('issuedCommandIds')]

    @property
    def route_status(self):
        """ The status of each route. """
        return self._data.get('routeStatus')

    def get_status(self):
        """ Gets the status of the SymBLE Downlink Message. """
        self._data = self._get(''.join[self.af_client_edge_url,
                                       '/symbleDownlinkStatus',
                                       '/', self.target, '/', self.subject_id])
        return self._data


class Node(AirfinderSubject):
    """ Base class for SymBLE Endnodes. """
    subject_name = 'node'
    application = None

    @property
    def name(self):
        """ The user issued name of the Subject. """
        return self._data.get('nodeName')

    @property
    def fw_version(self):
        """ The firmware version of the SymBLE Endnode. """
        pass

    @property
    def symble_version(self):
        """ The version the SymBLE Core on the EndNode is running. """
        pass

    @property
    def msg_spec_version(self):
        """ The message spec version of the SymBLE EndNode. """
        return Version(int(self._md.get('messageSpecVersion')))

    @property
    def mac_address(self):
        """ The mac address of the device from its metadata. """
        return self._md.get('macAddress')

    @property
    def device_type(self):
        """ Represents the human-readable Application Token that identifies
        which data parser the device is using. """
        return self._md.get('deviceType')

    @property
    def app_token(self):
        """ The Application Token of the Device Type of the Node. """
        val = self._md.get('app_tok')
        return AppToken(self.session, val, self.instance) if val else None

    @property
    def last_access_point(self):
        """ The last access point the node has communicated through. """
        addr = self._md.get('symbleAccessPoint')
        x = self._get_registered_af_asset('accesspoint', addr)
        obj = find_cls(AccessPoint, x['registrationToken'])
        if obj:
            return obj(self.session, addr, self.instance, x)
        dev = x['assetInfo']['metadata']['props'].get('deviceType')
        LOG.error("No device conversion for {}".format(dev))
        return AccessPoint(self.session, addr, self.instance, x)

    @property
    def last_gateway(self):
        """ The last gateway that the node's AP communicated through. """
        val = self._md.get('gateway')
        return Gateway(self.session, val, self.instance) if val else None

    @property
    def acknowledged(self):
        """ Whether the last downlink messages was acknowledged. """
        return bool(self._md.get('acknowledged'))

    def _get_spec(self, vers=None):
        """ Should return the correct messge specification for the message
        specification. """
        pass

    def _get_msg_obj(self, *args):
        """ Should return the correct uplink message object for the message
        specification.
        """
        return NodeUplinkMessage(*args)

    def _send_message(self, payload, time_to_live_s, access_point=None):
        """ Sends a SymBLE Unicast message. Defaults to sending to all
        Access Points within a Site. This requires the SymBLE endnode
        and all Access Points to be registered to a common site. To send a
        downlink to an individual Access Point, just specify the access_point
        parameter. This does not require a regsitration of a site.

        Args:
            payload (bytearray):
                The data to be recieved by the SymBLE Node.
            time_to_live_s (int):
                The time the SymBLE Endnode has to request its Mailbox to
                recieve the Downlink Message.
            access_point (:class:`.AccessPoint`):
                When specified, the message will be targeted at the specified
                Access Point.

        Returns:
            :class:`.NodeDownlinkMessage` when sent to all APs, otherwise,
            :class:`.DownlinkMessage` when sent to an individual AP.
        """
        if access_point:
            return access_point.send_unicast_message(self, payload,
                                                     time_to_live_s,
                                                     uuid4().fields[0])
        else:
            url = "{}/multicastCommand/{}/?payload={}&ttlMsecs={}".format(
                    self._af_client_edge_url, self.subject_id,
                    payload.hex(), int(time_to_live_s * 1e3))
            data = self._post(url)
            return NodeDownlinkMessage(self.session,
                                       data.get('symbleMessageId'),
                                       self.instance, _data=data)

    def _send_multicast_message(self, payload, time_to_live_s,
                                access_point=None):
        """ Sends a SymBLE Multicast message. Defaults to sending to all
        Access Points within a Site. This requires the SymBLE endnode
        and all Access Points to be registered to a common site. To send a
        downlink to an individual Access Point, just specify the access_point
        parameter. This does not require a regsitration of a site.

        Args:
            payload (bytearray):
                The data to be recieved by the SymBLE Node.
            time_to_live_s (int):
                The time the SymBLE Endnode has to request its Mailbox to
                recieve the Downlink Message.
            access_point (:class:`.AccessPoint`):
                When specified, the message will be targeted at the specified
                Access Point.

        Returns:
            :class:`.NodeDownlinkMessage` when sent to all APs, otherwise,
            :class:`.DownlinkMessage` when sent to an individual AP.
        """
        if access_point:
            return access_point.send_multicast_message(self.application,
                                                       payload,
                                                       time_to_live_s,
                                                       uuid4().fields[0])
        else:
            raise NotImplementedError("Must specify AccessPoint!")
