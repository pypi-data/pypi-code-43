from conductor.airfinder.devices.tag import Tag
from conductor.airfinder.devices.location import Location

class Zone(Tag):
    """ An Airfinder Zone within an Airfinder Area. """
    subject_name = 'Zone'

    def __init__(self, session, subject_id, parent_area, _data=None):
        super().__init__(session, subject_id, _data)
        self.parent_area = parent_area

    def _get_registered_asset_by_zone(self, subject_name, subject_id):
        """ Base function for getting a registered asset from the Network Asset API. """
        url = ''.join([NETWORK_ASSET_URL, '{}/{}'.format(subject_name, subject_id)])
        params = {
            'siteId': self.parent_area.parent_site.subject_id,
            'areaId': self.parent_area.subject_id,
            'zoneId': self.subject_id
        }
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def _get_registered_assets_by_zone(self, asset_name):
        """ Base function for getting list of registered assets from the Network Asset API. """
        url = ''.join([NETWORK_ASSET_URL, asset_name])
        params = {
            'siteId': self.parent_area.parent_site.subject_id,
            'areaId': self.parent_area.subject_id,
            'zoneId': self.subject_id
        }
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def get_locations(self):
        """ Get all the locations in a site. """
        return [Location(self.session, x.get('assetInfo').get('metadata').get('props').get('macAddress'), _data=x) for x in
                self._get_registered_assets_by_zone('locations')]

    def get_location(self, mac_id):
        """ Gets a location, in a site. """
        x = self._get_registered_asset_by_zone('location', mac_id)
        return Location(self.session, mac_id, _data=x)

    def add_location(self, mac_id, name):
        """ Adds a location to a site. """
        url = ''.join([NETWORK_ASSET_URL, 'locations'])
        params = {
            "accountId": 0,
            "macAddress": mac_id,
            'siteId': self.parent_area.parent_site.subject_id,
            'areaId': self.parent_area.subject_id,
            'zoneId': self.subject_id,
            "name": name,
            "properties": "object",
            "proxyLocations": [
                ""
            ]
        }
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        x = resp.json()
        return Location(self.session, x.get('id'), _data=x)

    def remove_location(self, mac_id):
        """ Remove a location from a site. """
        raise NotImplemented



