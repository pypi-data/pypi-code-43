import logging

from conductor.airfinder.devices.access_point import AccessPoint
from conductor.airfinder.devices.location import Location
from conductor.airfinder.devices.node import Node
from conductor.util import mac_to_addr

LOG = logging.getLogger(__name__)


class Tag(Node):
    """docstring for Tag"""

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
    def locations(self):
        return [Location(self.session, self.metadata_json.get('location' + x),
                         self.instance) for x in range(3)]

    @property
    def metadata_json(self):
        """ The raw json metadata returned by the object. """
        return self._data.get('assetInfo').get('metadata').get('props')

    @property
    def name(self):
        """ The assigned name given to the node. """
        # Overrides default Airfinder Node's Name.
        return self._data.get('nodeName')

    @property
    def last_location(self):
        """ The last location the node reported """
        is_ap = self.metadata.get('usingAPasLoc0')
        loc = self.metadata.get('location0')

        if not loc:
            return None

        try:
            if bool(is_ap):
                return AccessPoint(self.session, loc, self.instance)
            else:
                return Location(self.sesion, loc, self.instance)
        except ValueError:
            return None

    @property
    def last_priority(self):
        """ The priority of the last message sent to or from the Node. """
        return bool(self.metadata_json.get('priority'))

    @property
    def last_source_message(self):
        """ Returns the 'source message' of the last message sent. The 'source
        message' contains the payload of the message prior to being parsed by
        the Device Type / Application Token's message specification - which
        provides us with the human-readable metadata fields. """
        # smi = self.metadata_json.get('sourceMessageId')
        # smt = self.metadata_json.get('sourceMessageTimestamp')
        # TODO return source_message_to_uplink_message(self.session, smi, smt)
        pass
