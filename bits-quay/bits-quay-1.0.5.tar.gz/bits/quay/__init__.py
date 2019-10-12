# -*- coding: utf-8 -*-
"""Quay class file."""

import requests

from urllib.parse import urlencode


class Quay(object):
    """Quay class."""

    def __init__(
        self,
        token,
        orgname="broadinstitute",
        clientid=None,
        secret=None,
        role_team='roleaccounts',
        verbose=False
    ):
        """Initialize a Quay class instance."""
        # access token
        self.token = token

        # organization name
        self.orgname = orgname

        # role accounts team
        self.role_team = role_team

        # oauth2 clientid and secret
        self.clientid = clientid
        self.secret = secret

        # set verbosity
        self.verbose = verbose

        # API base url
        self.base_url = 'https://quay.io/api/v1'

        # request headers
        self.headers = {'Authorization': 'Bearer %s' % (self.token)}

    #
    # Sub Classes
    #
    def app(self, auth=None):
        """Return an App instance."""
        from bits.quay.app import App
        return App(auth, self)

    def client(self, auth=None):
        """Return an App instance."""
        from bits.quay.client import Client
        return Client(auth, self)

    def datastore(self, auth=None):
        """Return a Datastore instance."""
        from bits.quay.datastore import Datastore
        return Datastore(auth, self)

    def firestore(
        self,
        auth=None,
        project='broad-bitsdb-firestore',
        app_project=None,
        bitsdb_project='broad-bitsdb-prod',
    ):
        """Return a Firestore instance."""
        from bits.quay.firestore import Firestore
        return Firestore(
            auth,
            self,
            project=project,
            app_project=app_project,
            bitsdb_project=bitsdb_project,
        )

    #
    # Helpers
    #
    def delete(self, path, params=None):
        """DELETE a url path."""
        url = '%s/%s' % (self.base_url, path)
        response = requests.delete(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response

    def get(self, path, params=None):
        """GET a url path."""
        url = '%s/%s' % (self.base_url, path)
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response

    def put(self, path, params=None):
        """PUT a url path."""
        url = '%s/%s' % (self.base_url, path)
        response = requests.put(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response

    #
    # Oauth Authorization
    #
    def get_oauth_authorize_url(self, client_id, redirect_uri, scope):
        """Return the url for authorizing an oauth user."""
        base_url = 'https://quay.io/oauth/authorize'
        params = {
            'response_type': 'token',
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'scope': scope,
        }
        return '{}?{}'.format(base_url, urlencode(params))

    #
    # Quay endpoints
    #

    # discovery
    def get_api_discovery(self):
        """Return API discovery document."""
        # GET /api/v1/discovery
        url = "discovery"
        return self.get(url).json()

    # organization
    def get_org(self):
        """Return organization and teams."""
        # GET /api/v1/organization/{orgname}
        url = "organization/{}".format(self.orgname)
        return self.get(url).json()

    # org applications
    def get_org_applications(self):
        """Return a list of organization members."""
        # GET /api/v1/organization/{orgname}/applications
        url = 'organization/{}/applications'.format(self.orgname)
        return self.get(url).json().get('applications', [])

    # org collaborators
    def get_org_collaborators(self):
        """Return a list of organization collaborators."""
        # GET /api/v1/organization/{orgname}/collaborators
        url = 'organization/{}/collaborators'.format(self.orgname)
        return self.get(url).json().get('collaborators', [])

    # org invoices
    def get_org_invoices(self):
        """Return a list of org invoices."""
        # GET /api/v1/organization/{orgname}/invoices
        url = "organization/{}/invoices".format(self.orgname)
        return self.get(url).json().get('invoices', [])

    # org members
    def delete_org_member(self, membername):
        """Return an organization member."""
        # DELETE /api/v1/organization/{orgname}/members/{membername}
        url = 'organization/{}/members/{}'.format(self.orgname, membername)
        return self.delete(url)

    def get_org_member(self, membername):
        """Return an organization member."""
        # GET /api/v1/organization/{orgname}/members/{membername}
        url = 'organization/{}/members/{}'.format(self.orgname, membername)
        return self.get(url).json()

    def get_org_members(self):
        """Return a list of organization members."""
        # GET /api/v1/organization/{orgname}/members
        url = 'organization/{}/members'.format(self.orgname)
        return self.get(url).json().get('members', [])

    def get_org_repos(self, public=False, starred=False):
        """Return a list of repos."""
        return self.get_repos(namespace=self.orgname, public=public, starred=starred)

    # org teams
    def get_org_teams(self):
        """Return a list of organization members."""
        return list(self.get_org()['teams'].values())

    # org team members
    def add_org_team_member(self, teamname, member):
        """Add or invite a member to an existing team."""
        # PUT /api/v1/organization/{orgname}/team/{teamname}/members/{membername}
        url = 'organization/{}/team/{}/members/{}'.format(self.orgname, teamname, member)
        return self.put(url)

    def delete_org_team_member(self, teamname, member):
        """Delete a member of a team or remove invitation."""
        # DELETE /api/v1/organization/{orgname}/team/{teamname}/members/{membername}
        url = 'organization/{}/team/{}/members/{}'.format(self.orgname, teamname, member)
        return self.delete(url)

    def get_org_team_members(self, teamname):
        """Return a list of organization members."""
        # GET /api/v1/organization/{orgname}/team/{teamname}/members
        url = 'organization/{}/team/{}/members'.format(self.orgname, teamname)
        params = {
            'includePending': True,
        }
        return self.get(url, params=params).json().get('members', [])

    def invite_org_team_member(self, teamname, email):
        """Invite an email address to an existing team."""
        # PUT /api/v1/organization/{orgname}/team/{teamname}/invite/{email}
        url = 'organization/{}/team/{}/invite/{}'.format(self.orgname, teamname, email)
        return self.put(url)

    def uninvite_org_team_member(self, teamname, email):
        """Delete an invite of an email address to join a team."""
        # DELETE /api/v1/organization/{orgname}/team/{teamname}/invite/{email}
        url = 'organization/{}/team/{}/invite/{}'.format(self.orgname, teamname, email)
        return self.delete(url)

    # org team permissions
    def get_org_team_permissions(self, teamname):
        """Return a list of organization permissions."""
        # GET /api/v1/organization/{orgname}/team/{teamname}/permissions
        url = 'organization/{}/team/{}/permissions'.format(self.orgname, teamname)
        return self.get(url).json().get('permissions', [])

    # repo
    def get_repo(self, repo, includeTags=True, includeStats=False):
        """Return a repository."""
        # GET /api/v1/repository/{repository}
        if '/' not in repo:
            repo = '{}/{}'.format(self.orgname, repo)
        url = 'repository/{}'.format(repo)
        params = {
            'includeTags': includeTags,
            'includeStats': includeStats,
        }
        return self.get(url, params=params).json()

    def get_repos(
        self,
        last_modified=None,
        namespace=None,
        popularity=None,
        public=False,
        repo_kind=None,
        starred=False
    ):
        """Return a list of repos."""
        # GET /api/v1/repository
        url = 'repository'
        if not namespace and not public and not starred:
            namespace = self.orgname
        params = {
            'last_modified': last_modified,
            'namespace': namespace,
            'popularity': popularity,
            'public': public,
            'repo_kind': repo_kind,
            'starred': starred,
        }
        return self.get(url, params=params).json().get('repositories', [])

    def get_user(self, username=None):
        """Return the current user."""
        # GET /api/v1/user - get current user
        # GET /api/v1/users/username - get named user
        url = 'user'
        if username:
            url = 'users/{}'.format(username)
        return self.get(url).json()
