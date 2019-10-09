# -*- coding: utf-8 -*-
"""Firestore Class file."""

import re
from google.cloud import firestore


class Firestore(object):
    """Firestore class."""

    def __init__(
        self,
        auth=None,
        github=None,
        project='broad-bitsdb-firestore',
        app_project=None,
        bitsdb_project='broad-bitsdb-prod',
    ):
        """Initialize a class instance."""
        self.auth = auth
        self.firestore = firestore
        self.github = github
        self.project = project
        self.bitsdb_project = bitsdb_project

        self.verbose = False
        if self.github:
            self.verbose = self.github.verbose

        # set the default db object
        self.db = firestore.Client(project=self.project)
        if not app_project:
            self.app = firestore.Client()
        else:
            self.app = firestore.Client(project=app_project)
        self.bitsdb = firestore.Client(project=self.bitsdb_project)

    def get_dict(self, items, key='id'):
        """Return a dict from a list."""
        data = {}
        for i in items:
            if key not in i or not i[key]:
                continue
            k = i[key]
            data[k] = i
        return data

    #
    # people
    #
    def get_people(self):
        """Return a list of people."""
        fields = [
            'email_username',
            'emplid',
            'full_name',
            'github_id',
            'github_login',
            'google_id',
            'terminated',
            'username',
        ]
        query = self.db.collection('people_people').select(fields)
        people = []
        for item in query.stream():
            people.append(item.to_dict())
        return people

    def get_people_dict(self, key='email_username'):
        """Return a dict of people by username."""
        return self.get_dict(self.get_people(), key)

    #
    # Collections from GitHub App Firetore: broad-github-app or broad-github-app-dev
    #
    # Uses: self.app connection
    #

    #
    # github members
    #
    def get_members(self):
        """Return a list of members."""
        query = self.app.collection('github_members')
        members = []
        for item in query.stream():
            members.append(item.to_dict())
        return members

    def get_members_dict(self, key='id'):
        """Return a dict of members by member id."""
        return self.get_dict(self.get_members(), key)

    #
    # github repos
    #
    def get_repos(self):
        """Return a list of repos."""
        query = self.app.collection('github_repos')
        repos = []
        for item in query.stream():
            repos.append(item.to_dict())
        return repos

    def get_repos_dict(self, key='id'):
        """Return a dict of repos by repo id."""
        return self.get_dict(self.get_repos(), key)

    #
    # github team syncs
    #
    def get_team_syncs(self):
        """Return a list of team syncs."""
        query = self.app.collection('team_syncs')
        team_syncs = []
        for item in query.stream():
            team_syncs.append(item.to_dict())
        return team_syncs

    def get_team_syncs_dict(self, key='team_slug'):
        """Return a dict of team syncs by team id."""
        return self.get_dict(self.get_team_syncs(), key)

    def get_user_team_syncs(self, google_id):
        """Return a list of team syncs for the given user."""
        fields = [
            'team_id',
            'team_slug',
            'group_email',
            'group_id',
        ]
        groups_ref = self.app.collection('team_syncs')
        query = groups_ref.where(u'group_members', u'array_contains', google_id).select(fields)
        team_syncs = []
        for doc in query.stream():
            sync = doc.to_dict()
            team_syncs.append(sync)
        return team_syncs

    #
    # github teams
    #
    def get_teams(self, fields=None):
        """Return a list of teams."""
        query = self.app.collection('github_teams')
        if fields:
            query = query.select(fields)
        teams = []
        for item in query.stream():
            teams.append(item.to_dict())
        return teams

    def get_teams_dict(self, key='id', fields=None):
        """Return a dict of teams by team id."""
        return self.get_dict(self.get_teams(fields=fields), key)

    def get_user_teams(self, login):
        """Return a list of teams where login is a member."""
        # get teams
        teams = self.get_teams_dict(fields=['id', 'slug'])

        # get member records
        query = self.app.collection_group('members').where('login', '==', login)

        # add teams to user_teams
        user_teams = []
        for doc in query.stream():
            path = doc.reference.path
            if not re.match(r'github_teams\/[0-9]+\/members\/[0-9]+', path):
                continue
            _, team_id, _, _ = path.split('/')

            team_id = int(team_id)
            if team_id not in teams:
                continue

            user_teams.append(teams[team_id])
        return user_teams

    #
    # github teams members
    #
    def get_teams_members(self):
        """Return a list of teams and their members."""
        # get teams
        teams = self.get_teams_dict()

        # add team members to teams
        for doc in self.app.collection_group('members').stream():
            path = doc.reference.path
            if not re.match(r'github_teams\/[0-9]+\/members\/[0-9]+', path):
                continue
            _, team_id, _, _ = path.split('/')

            team_id = int(team_id)
            if team_id not in teams:
                continue

            team = teams[team_id]
            if 'members' not in team:
                team['members'] = []

            team['members'].append(doc.to_dict())

        # create list to return
        teams_members = []
        for team_id in teams:
            t = teams[team_id]
            team = {
                'id': team_id,
                'slug': t['slug'].lower(),
                'members': t.get('members', []),
            }
            teams_members.append(team)

        return teams_members

    def get_teams_members_dict(self, key='id'):
        """Return a dict of team syncs by team id."""
        return self.get_dict(self.get_teams_members_dict(), key)

    #
    # github teams repos
    #
    def get_teams_repos(self):
        """Return a list of teams and their repos."""
        # get teams
        teams = self.get_teams_dict()

        # add team members to teams
        for doc in self.app.collection_group('repos').stream():
            path = doc.reference.path
            if not re.match(r'github_teams\/[0-9]+\/repos\/[0-9]+', path):
                continue
            _, team_id, _, _ = path.split('/')

            team_id = int(team_id)
            if team_id not in teams:
                print('ERROR: Team not found: {}'.format(team_id))
                continue

            team = teams[team_id]
            if 'repos' not in team:
                team['repos'] = []

            team['repos'].append(doc.to_dict())

        # create list to return
        teams_repos = []
        for team_id in teams:
            t = teams[team_id]
            team = {
                'id': team_id,
                'slug': t['slug'].lower(),
                'repos': t.get('repos', []),
            }
            teams_repos.append(team)

        return teams_repos

    def get_teams_repos_dict(self, key='id'):
        """Return a dict of team syncs by team id."""
        return self.get_dict(self.get_teams_repos_dict(), key)

    #
    # github users
    #
    def delete_stored_github_user(self, github_id):
        """Delete a github user stored in firestore."""
        return self.app.collection('github_users').document(str(github_id)).delete()

    def get_stored_github_user(self, github_id):
        """Return the stored user for the given github user id."""
        return self.app.collection('github_users').document(str(github_id)).get().to_dict()

    #
    # settings
    #
    def get_config(self):
        """Return the config settings from Firestore."""
        config = {}
        for doc in self.app.collection('settings').stream():
            config[doc.id] = doc.to_dict()
        return config

    #
    # tokens
    #
    def delete_stored_token(self, google_id):
        """Delete a token stored in firestore."""
        return self.app.collection('tokens').document(google_id).delete()

    def get_stored_token(self, google_id):
        """Return the stored token for the given google user id."""
        return self.app.collection('tokens').document(google_id).get().to_dict()

    def get_tokens(self):
        """Return all token records from firestore."""
        tokens = []
        for doc in self.app.collection('tokens').stream():
            tokens.append(doc.to_dict())
        return tokens

    #
    # users - google users with special privileges in the app
    #
    def get_user(self, google_id):
        """Return the stored token for the given google user id."""
        return self.app.collection('users').document(google_id).get().to_dict()

    def get_users(self):
        """Return a list of users."""
        users = []
        ref = self.app.collection('users')
        for doc in ref.stream():
            u = doc.to_dict()
            u['id'] = doc.id
            users.append(u)
        return users
