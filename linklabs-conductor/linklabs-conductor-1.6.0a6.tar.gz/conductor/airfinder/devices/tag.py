import logging

from conductor.subject import FailedAPICallException
from conductor.airfinder.devices.access_point import AccessPoint, \
                                                     NordicAccessPoint
from conductor.airfinder.devices.location import Location
from conductor.airfinder.devices.node import Node
from conductor.util import mac_to_addr, parse_time

LOG = logging.getLogger(__name__)


class Tag(Node):
    """ Represents a SymBLE Tag. """

    subject_name = "node"

    def __init__(self, session, subject_id, instance, _data=None):
        # Validate and construct object.
        if not session or not subject_id or not instance:
            raise Exception("Invalid Construction of a Tag!")

        self.subject_id = mac_to_addr(subject_id)
        super().__init__(session, subject_id, instance, _data=_data)
        if not self._data:
            url = '{}/{}/{}'.format(self.network_asset_url, self.subject_name,
                                    self.subject_id)
            self._data = self._get(url)

    def __repr__(self):
        return '{} {} ({})'.format(self.__class__.__name__, self.subject_id,
                                   self.name)

    @property
    def _md(self):
        """ The raw json metadata returned by the object. """
        return self._data.get('assetInfo').get('metadata').get('props')

    @property
    def locations(self):
        return [Location(self.session, self._md.get('location' + x),
                         self.instance) for x in range(3)]

    @property
    def name(self):
        """ The assigned name given to the node. """
        # Overrides default Airfinder Node's Name.
        return self._data.get('nodeName')

    @property
    def last_location(self):
        """ The last location the node reported and the time. """
        is_ap = self._md.get('usingAPasLoc0')
        loc = self._md.get('location0')
        time = parse_time(self._md.get('locationTime'))

        if not loc:
            return None

        try:
            if bool(is_ap):
                try:
                    url = '{}/accesspoint/{}'.format(
                        self._af_network_asset_url, loc)
                    x = self._get(url)
                    tok, ap = x['registrationToken'], None
                    if tok == AccessPoint.application:
                        ap = AccessPoint
                    elif tok == NordicAccessPoint.application:
                        ap = NordicAccessPoint
                except FailedAPICallException:
                    LOG.error("Known bug in Conductor.")
                    return (Location(self.session, loc, self.instance), time)
                return (ap(self.session, loc, self.instance, x), time)
            else:
                return (Location(self.session, loc, self.instance), time)
        except ValueError:
            return None

    @property
    def last_priority(self):
        """ The priority of the last message sent to or from the Node. """
        return bool(self._md.get('priority'))

    @property
    def last_source_message(self):
        """ Returns the 'source message' of the last message sent. The 'source
        message' contains the payload of the message prior to being parsed by
        the Device Type / Application Token's message specification - which
        provides us with the human-readable metadata fields. """
        # smi = self._md.get('sourceMessageId')
        # smt = self._md.get('sourceMessageTimestamp')
        # TODO return source_message_to_uplink_message(self.session, smi, smt)
        pass
