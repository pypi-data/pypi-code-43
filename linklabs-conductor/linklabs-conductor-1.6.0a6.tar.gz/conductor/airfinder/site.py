"""" Represents an Airfinder Site. """
import logging

from conductor.airfinder.base import AirfinderSubject
from conductor.airfinder.devices.access_point import AccessPoint

LOG = logging.getLogger(__name__)


class Site(AirfinderSubject):
    """ Represents an Airfinder Site. """
    subject_name = 'Site'

    def _get_registered_asset_by_site(self, subject_name, subject_id):
        """ Gets a registered asset by site-id. """
        url = ''.join([self._af_network_asset_url, '/{}/{}/'.format(subject_name, subject_id)])
        params = {'siteId': self.subject_id}
        return self._get(url, params)

    def _get_registered_assets_by_site(self, asset_name):
        """ Gets all the registered assets by site-id. """
        url = ''.join([self._af_network_asset_url, asset_name])
        params = {'siteId': self.subject_id}
        return self._get(url, params=params)

    def rename(self, name):
        """ Rename an existing site. """
        # TODO
        url = ''.join([self._af_network_asset_url, 'airfinder/sites'])
        param = {'siteId': self.subject_id}
        updates = {
            "name": name,
        }
        _data = self._put(url, params, updates)

    def get_site_users(self):
        """ Gets all the site-users, in the site. """
        return [SiteUser(self.session, x.get('id'), _data=x) for x in
                self._get_registered_assets_by_site('users')]

    def get_site_user(self, site_user_id):
        """ Gets a site-user in a site. """
        x = self._get_registered_asset_by_site('user', site_user_id)
        return SiteUser(self.session, x.get('id'), _data=x)

    def get_areas(self):
        """ Gets all the areas for a site. """
        return [Area(self.session, x.get('id'), self, _data=x) for x in
                self._get_registered_assets_by_site('areas')]

    def create_area(self, name):
        """ Create an area as a part of this Site. """
        url = ''.join([self._af_network_asset_url, asset_name])
        params = {'siteId': self.subject_id}
        return self._get(url, params)

    def delete_area(self, area_id):
        """ Delete an area. """
        url = ''.join([self._af_network_asset_url, asset_name])
        params = {'siteId': self.subject_id}
        return self._delete(url, params)

    def get_area(self, area_id):
        """ Gets an area in a site. """
        x = self._get_registered_asset_by_site('area', area_id)
        return Area(self.session, x.get('id'), self, _data=x)

#    def get_workflows(self):
#        """ Gets all the workflows for the Site. """
#        return self._get_registered_assets_by_site('workflows')

#    def get_workflow(self, workflow_id):
#        """" Gets a workflow for the Site. """
#        return self._get_registered_asset_by_site('workflow', workflow_id)

    def remove_locations(self, locations):
        """ Remove locations from a Site. """
        # TODO: test
        url = ''.join([self._af_network_asset_url, 'tags'])
        data = {
            "nodeAddresses": [locations],
            "siteId": self.subject_id
        }
        resp = self.session.delete(url, json=data)
        resp.raise_for_status()
        return resp.json()

    def get_access_points(self):
        return [AccessPoint(self.session, x.get('nodeAddress'), self.instance, _data=x) for x in
                self._get_registered_assets_by_site('/accesspoints')]


    def get_tags(self):
        """ Gets all the tags in a site. """
        tags = []
        for site in self._get_registered_assets_by_site('tags'):
            print(x)
            dev = x.get('assetInfo').get('metadata').get('props').get('deviceType')
            subject_id = x.get('id') if 'id' in x else x.get('nodeAddress')
            if dev in DEVICE_DICT:
                tags.append(DEVICE_DICT[dev](self.session, subject_id, self.instance, x))
            else:
                LOG.error("No device conversion for {}".format(dev))
                tags.append(Tag(self.session, subject_id, self.instance, x))
        return tags

    def get_tag(self, mac_id):
        """ Gets a tag in the site. """
        return self._get_registered_asset_by_site('tag', mac_id)

    def add_tag(self, mac_id, field1="", field2="", category=None, description=""):
        """ Adds a tag in the site. """
        url = ''.join([self._af_network_asset_url, 'tags'])
        params = {
            "accountId": self._md.get('accountId'),
            "macAddress": mac_id,
            "siteId": self.subject_id,
            "description": description,
            "categoryId": category,
            "groups": [""],
            "field1": field1,
            "field2": field2,
            "properties": "object",
            "homeLocation": "",
            "adjacentLocations": [""],
            "trackTagAge": ""
        }
        resp = self.session.post(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def bulk_add_tags(self, file_name):
        """ Bulk-add tags to an airfinder site. """
        raise NotImplemented

    def remove_tag(self, mac_id):
        """ Remove a tag to an airfinder site. """
        url = ''.join([self._af_network_asset_url, 'tags'])
        params = {
            "nodeAddress": mac_id,
            "accountId": self._md.get('accountId'),
            "siteId": self.subject_id
        }
        resp = self.session.post(url, params=params)
        resp.raise_for_status()
        return resp.json()

#    def bulk_add_locations(self, file_name):
#        """ Bulk-add locations to a site. """
#        raise NotImplemented

#    def get_groups(self):
#        """ Get all the groups in a site. """
#        return self._get_registered_assets_by_site('groups')

#    def get_group(self, group_id):
#        """ Get a group from a site. """
#        return self._get_registered_asset_by_site('group', group_id)

#    def get_categories(self):
#        """ Get all the categories in a site."""
#        return self._get_registered_assets_by_site('categories')

#    def get_category(self, category_id):
#        """ Get a category in a site. """
#        return self._get_registered_asset_by_site('category', category_id)

    def get_asset_group(self):
        """ Get the Site as an Asset Group. """
        x = _get_registered_asset_by_site('assetGroup')
        return AssetGroup(self.session, x['id'], _data=x)

    @property
    def area_count(self):
        """ Returns the number of Areas within the Site. """
        val = self._md.get('areaCount')
        return int(val) if val else None

