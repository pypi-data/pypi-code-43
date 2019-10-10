""" Represents an Airfinder Area. """

from conductor.airfinder.devices.tag import Tag
from conductor.airfinder.zone import Zone


class Area(Tag):
    """ Represents an Airfinder Area inside of an Airfinder Site. """
    subject_name = 'Area'

    def __init__(self, session, subject_id, parent_site, _data=None):
        super().__init__(session, subject_id, _data)
        self.parent_site = parent_site

    def _get_registered_asset_by_area(self, subject_name, subject_id):
        """ Base function for getting a registered asset from the Network Asset API. """
        url = ''.join([NETWORK_ASSET_URL, '{}/{}'.format(subject_name, subject_id)])
        params = {'siteId': self.parent_site.subject_id, 'areaId': self.subject_id}
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def _get_registered_assets_by_area(self, asset_name):
        """ Base function for getting list of registered assets from the Network Asset API. """
        url = ''.join([NETWORK_ASSET_URL, asset_name])
        params = {'siteId': self.parent_site.subject_id, 'areaId': self.subject_id}
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    @property
    def area_location(self):
        """ The issuance ID is the subject ID from the ConductorSubject base class. """
        return self.metadata.get('areaLocation')

    def get_parent_site(self):
        """ Get the Site that the area is within. """
        return self.parent_site

    def get_area_location(self):
        """ Get the location of the area; Outdoor will return coordinates, Indoor will return a mapping. """
        if 'Outdoor' == self.area_location:
            return self.metadata.get('points')
        elif 'Indoor' == self.area_location:
            return self.metadata.get('indoorMapping')

    def get_zones(self):
        """ Get all the Zones within the Area. """
        return [Zone(self.session, x.get('id'), self, _data=x) for x in
                self._get_registered_assets_by_area('zones')]

    def get_zone(self, zone_id):
        """ Get a Zone within the Area. """
        x = self._get_registered_asset_by_area('zone', zone_id)
        return Zone(self.session, x.get('id'), self, _data=x)

    def create_zone(self, name):
        """ Add a zone to the Area. """
        url = ''.join([NETWORK_ASSET_URL, 'zones'])
        params = {
            "siteId": self.parent_site.subject_id,
            "configType": "Zone",
            "configValue": name,
            "properties": "object",
        }
        resp = self.session.post(url, params=params)
        resp.raise_for_status()
        x = resp.json()
        return Zone(self.session, x.get('id'), self, _data=x)

    # TODO: Move this to zone.
    def delete_zone(self, zone_id):
        """ Remove a Zone from an Area. """
        url = ''.join([NETWORK_ASSET_URL, 'zones'])
        params = {"zoneId": zone_id}
        resp = self.session.delete(url, params=params)
        resp.raise_for_status()
        return resp.json()



