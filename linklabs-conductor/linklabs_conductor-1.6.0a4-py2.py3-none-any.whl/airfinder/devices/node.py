""" A base class for SymBLE Nodes. """
import logging

from conductor.airfinder.base import AirfinderUplinkMessage, AirfinderSubject
from conductor.airfinder.devices.access_point import AccessPoint
from conductor.devices.gateway import Gateway
from conductor.subject import DownlinkMessage
from conductor.tokens import AppToken

LOG = logging.getLogger(__name__)


class NodeUplinkMessage(AirfinderUplinkMessage):
    """ Uplink Messages for SymBLE EndNodes. """

    @property
    def msg_counter(self):
        return int(self.metadata_json.get('msgCounter'))

    @property
    def symble_version(self):
        """ The version of the SymBLE Core on the Node. """
        pass

    @property
    def access_point(self):
        AccessPoint(self.session, self.instance,
                    self.metadata_json("symbleAccessPoint"))


class NodeDownlinkMessage(DownlinkMessage):
    """ Represents a SymBLE Downlink Message. """

    @property
    def target(self):
        """ The recpient SymBLE Endnode. """
        return self._data.get('subjectId')

    @property
    def acknowledged(self):
        """ """
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
    msg_obj = NodeUplinkMessage
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
        pass

    @property
    def mac_address(self):
        """ The mac address of the device from its metadata. """
        return self.metadata_json.get('macAddress')

    @property
    def device_type(self):
        """ Represents the human-readable Application Token that identifies
        which data parser the device is using. """
        return self.metadata_json.get('deviceType')

    @property
    def app_token(self):
        """ The Application Token of the Device Type of the Node. """
        val = self.metadata_json.get('app_tok')
        return AppToken(self.session, val, self.instance) if val else None

    @property
    def last_access_point(self):
        """ The last access point the node has communicated through. """
        addr = self.metadata_json.get('symbleAccessPoint')
        return AccessPoint(self.session, addr, self.instance) if addr else None

    @property
    def last_gateway(self):
        """ The last gateway that the node's AP communicated through. """
        val = self.metadata_json.get('gateway')
        return Gateway(self.session, val, self.instance) if val else None

    def _send_message(self, payload, time_to_live_s):
        """ Sends a SymBLE Unicast message.

        Args:
            payload (bytes):
                The data to be recieved by the SymBLE Node.
            time_to_live_s (int):
                The time the SymBLE Endnode has to request its Mailbox to
                recieve the Downlink Message.
        """
        url = "{}/multicastCommand/{}/{}/{}".format(self.af_client_edge_url,
                                                    self.subject_id, payload,
                                                    time_to_live_s)
        data = self._post(url)
        return NodeDownlinkMessage(self.session, data.get('symbleMessageId'),
                                   self.instance, _data=data)
