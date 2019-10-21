""" Represents an Airfinder User. """
import logging

from conductor.account import ConductorAccount
from conductor.airfinder.base import AirfinderSubject
from conductor.airfinder.devices.access_point import AccessPoint
from conductor.airfinder.devices.node import Node
from conductor.airfinder.site import Site
from conductor.util import find_cls

LOG = logging.getLogger(__name__)


class SiteUser():
    """
    This class is used to manage other Airfinder SiteUsers,
    given the User has Admin-level permissions.
    """
    subject_name = 'SiteUser'

    SITE_USER_PERMISSIONS = {
        "Admin": False,
        "Status": True,
        "AddTags": True,
        "EditDeleteTags": True,
        "EditDeleteGroupsCategories": False
    }

    def __init__(self, session, subject_id, _data=None):
        super().__init__(session, subject_id, _data)

    @property
    def can_add_tags(self):
        """ Can the SiteUser add tags? """
        return bool(self._md.get('AddTags'))

    @property
    def is_admin(self):
        """ Is the SiteUser an Admin? """
        return bool(self._md.get('Admin'))

    @property
    def can_edit_delete_groups_categories(self):
        """ Can the SiteUser Edit/Delete Groups and Categories? """
        return bool(self._md.get('EditDeleteGroupsCategories'))

    @property
    def can_edit_delete_tags(self):
        """ Can the SiteUser Edit/Delete tags? """
        return bool(self._md.get('EditDeleteTags'))

    @property
    def email(self):
        """ The SiteUser's email address. """
        return self._md.get('email')

    @property
    def user_id(self):
        return self._md.get('userId')

    @property
    def status(self):
        return bool(self._md.get('Status'))

    @property
    def site(self):
        return Site(self.session, self._md.get('siteId'))

    def forgot_password(self):
        """ Sends the site user an email to reset their password. """
        url = ''.join([self._af_network_asset_url, 'users/forgotPassword'])
        params = {'email': self.email}
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    def resend_email(self):
        """ Resends the site user an email to reset their password. """
        url = ''.join([self._af_network_asset_url, 'users/resend'])
        params = {'email': self.email}
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        return resp.json()


class User(ConductorAccount, AirfinderSubject):
    """
    This class provides methods for interacting with Airfinder through
    Conductor for any particular account.

    This is the starting point for everything else in this module. Initialize
    with your username and password. If the password is omitted the initializer
    will prompt for one. Optionally provide the account name that you're trying
    to access (if you don't provide the account, the constructor will try to
    figure out which account is linked to your username).
    """
    subject_name = "User"

    def create_site(self, name):
        """ Create a site with the given name.

        Args:
            name (str): The name of the new Site.

        Raises:
            FailedAPICallException: When a failure occurs.

        Returns:
            :class:`.Site`, representing the recently created site.
        """
        url = ''.join([self._af_network_asset_url, '/sites'])
        data = {
            "configType": "Site",
            "configValue": name,
            "properties": {}
        }
        x = self._post(url, json=data)
        return Site(self.session, x.get('id'), self.instance, _data=x)

    def get_sites(self):
        """ Get all the Sites that a user has access to.

        Raises:
            FailedAPICallException: When a failure occurs.

        Returns:
            A list of :class:`.Site` objects.
        """
        return [Site(self.session, x.get('id'), self.instance, _data=x)
                for x in self._get_registered_af_assets('sites')]

    def get_site(self, site_id):
        """ Get all the Sites that a user has access to.

        Args:
            site_id (str or :class:`.Site`): The id of the site to get

        Raises:
            FailedAPICallException: When a failure occurs.

        Returns:
            The requested :class:`.Site` object.
        """
        x = self._get_registered_af_asset('site', str(site_id))
        return Site(self.session, x.get('id'), self.instance, _data=x)

    def delete_site(self, site_id):
        """
        Delete a specific site by site_id.

        .. note::
            Will delete all contained :class:`.Area` and :class:`.Zone` objects
            as well.

        Args:
            site_id (str or :class:`.Site`): The id of the site to delete

        Raises:
            FailedAPICallException: When the call fails.

        """
        url = ''.join([self._af_network_asset_url, '/site/', str(site_id)])
        self._delete(url)

    def get_node(self, mac_id):
        """ Gets all the devices that a user has access to.

        Args:
            mac_id (str or :class:`.AirfinderSubject`):
                The Mac ID in (XX:XX:XX:XX:XX:XX or XXXXXXXXXXXX format) or
                the conductor address of the device.

        Raises:
            FailedAPICallException: When a failure occurs.

        Returns:
            The corresponding :class:`.AirfinderSubject` object for the device.
        """
        x = self._get_registered_af_asset('tag', mac_id)
        subject_id = x.get('id') if 'id' in x else x.get('nodeAddress')
        obj = find_cls(Node, x['registrationToken'])
        if obj:
            return obj(self.session, subject_id, self.instance, x)
        dev = x['assetInfo']['metadata']['props'].get('deviceType')
        LOG.error("No device conversion for {}".format(dev))
        return Node(self.session, subject_id, self.instance, x)

    def get_access_point(self, subject_id):
        """ Get an Access Point, by subject_id.

        Args:
            subject_id (str or :class:`.AccessPoint` or :class:`.Module`)

        Raises:
            FailedAPICallException: When a failure occurs.

        Returns:
            The corresponding :class:`.AccessPoint` object for the device.
        """
        x = self._get_registered_af_asset('accesspoint', str(subject_id))
        obj = find_cls(AccessPoint, x['registrationToken'])
        if obj:
            return obj(self.session, x['nodeAddress'], self.instance, x)
        dev = x['assetInfo']['metadata']['props'].get('deviceType')
        LOG.error("No device conversion for {}".format(dev))
        return AccessPoint(self.session, x['nodeAddress'], self.instance, x)

    def create_site_user(self, email, site, site_user_permissions=None):
        """ Create a Site User.

        Raises:
            FailedAPICallException: When a failure occurs.

        Returns:
            The created :class:`.SiteUser` object.
        """
        # if site_user_permissions is None:
        #    site_user_permissions = SITE_USER_PERMISSIONS

        url = ''.join([self._af_network_asset_url, '/users'])
        data = {
            "sites": [str(site)],
            "email": email,
            "permissions": site_user_permissions
        }
        x = self._post(url, json=data)
        return SiteUser(self.session, x['id'], _data=x)

        # TODO
        # def get_site_user(self, email):
        #    """ """
        #     pass
