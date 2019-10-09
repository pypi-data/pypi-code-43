# -*- coding: utf-8 -*-
"""GitHub Sync Class."""


class Sync(object):
    """Sync Class."""

    def __init__(self, auth=None, github=None):
        """Initialize a class instance."""
        self.auth = auth
        self.github = github
        self.mongo = auth.mongo_prod()

        self.verbose = False
        if self.github:
            self.verbose = self.github.verbose

        # github users
        self.logins = {}
        self.users = {}

        # people
        self.people = {}

        # team syncs
        self.team_syncs = {}

    def get_datastore_users(self):
        """Return a dict of users from the broad-github datastore project."""
        datastore = self.github.datastore()
        for entity in datastore.get_users():
            user = dict(entity)
            login = user['login']
            uid = user['github_id']
            self.logins[login] = user
            self.users[uid] = user
        return self.users

    def get_mongo_github_team_syncs(self):
        """Return a dict of team sync records from BITSdb prod mongo db."""
        self.team_syncs = self.mongo.get_collection_dict('github_team_sync', key='github_team')
        return self.team_syncs

    def get_people(self):
        """Return a dict of people."""
        firestore = self.github.firestore()
        return firestore.get_people_dict()

    def prepare_data(self):
        """Prepare data for syncing."""
        print('Getting source data...')
        github_team_syncs = self.get_mongo_github_team_syncs()
        print('  Found {} github_team_sync records in BITSdb Mongo.'.format(len(github_team_syncs)))
        github_users = self.get_datastore_users()
        print('  Found {} GitHubUser records in broad-github Datastore.'.format(len(github_users)))
        people = self.get_people()
        print('  Found {} people records in bits-bitsdb-firestore Firestore.'.format(len(people)))

    def update_all(self):
        """Sync all GitHub data."""
        # prepare data for syncing
        self.prepare_data()
        self.update_team_syncs()
        self.update_users()

    def update_team_syncs(self):
        """Sync GitHub team syncs."""
        # on-prem mongo DB is currently the source of truth
        print('Updating GitHub Team Syncs from BITSdb Mongo...')

        # update the broad-github app's list of GitHubUser entities in datastore
        datastore = self.github.datastore()
        for entity in datastore.get_groups():
            group = dict(entity)
            import json
            print(json.dumps(group, indent=2, sort_keys=True))

    def update_users(self):
        """Sync all GitHub users."""
        # broad-github app is currently source of truth
        print('Updating GitHub Users from broad-github Datastore...')
