# -*- coding: utf-8 -*-
"""Firestore Class file."""

from google.cloud import firestore


class Firestore(object):
    """Firestore class."""

    def __init__(
        self,
        auth=None,
        github=None,
        project='broad-bitsdb-firestore',
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
        self.app = firestore.Client()
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
    # Collections from Firestore data warehouse: broad-bitsdb-firestore
    #

    #
    # github repos with outside collaborators
    #
    def get_repos_outside_collaborators(self):
        """Return a list of repos outside collaborators."""
        query = self.db.collection('github_repos_outside_collaborators')
        repos_outside_collaborators = []
        for item in query.stream():
            repos_outside_collaborators.append(item.to_dict())
        return repos_outside_collaborators

    def get_repos_outside_collaborators_dict(self, key='id'):
        """Return a dict of repos outside collaborators."""
        return self.get_dict(self.get_repos_outside_collaborators(), key)

    #
    # github teams with members
    #
    def get_teams_members(self):
        """Return a list of team syncs."""
        query = self.db.collection('github_teams_members')
        teams_members = []
        for item in query.stream():
            teams_members.append(item.to_dict())
        return teams_members

    def get_teams_members_dict(self, key='id'):
        """Return a dict of team syncs by team id."""
        return self.get_dict(self.get_teams_members_dict(), key)

    #
    # github teams with repos
    #
    def get_teams_repos(self):
        """Return a list of team syncs."""
        query = self.db.collection('github_teams_repos')
        teams_repos = []
        for item in query.stream():
            teams_repos.append(item.to_dict())
        return teams_repos

    def get_teams_repos_dict(self, key='id'):
        """Return a dict of team syncs by team id."""
        return self.get_dict(self.get_teams_repos_dict(), key)

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
    # Collections from Firestore Bitsdb: broad-bitsdb-prod
    #

    #
    # github team syncs
    #
    def get_team_syncs(self):
        """Return a list of team syncs."""
        query = self.bitsdb.collection('github_team_syncs')
        team_syncs = []
        for item in query.stream():
            team_syncs.append(item.to_dict())
        return team_syncs

    def get_team_syncs_dict(self, key='github_team_slug'):
        """Return a dict of team syncs by team id."""
        return self.get_dict(self.get_team_syncs(), key)

    def get_user_team_syncs(self, google_id):
        """Return a list of team syncs for the given user."""
        fields = [
            'github_team',
            'github_team_slug',
            'google_group',
        ]
        groups_ref = self.bitsdb.collection('github_group_members')
        query = groups_ref.where(u'members', u'array_contains', google_id).select(fields)
        teams = []
        for doc in query.stream():
            sync = doc.to_dict()
            teams.append(sync)
        return teams

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
    # github teams
    #
    def get_teams(self):
        """Return a list of teams."""
        query = self.app.collection('github_teams')
        teams = []
        for item in query.stream():
            teams.append(item.to_dict())
        return teams

    def get_teams_dict(self, key='id'):
        """Return a dict of teams by team id."""
        return self.get_dict(self.get_teams(), key)

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
