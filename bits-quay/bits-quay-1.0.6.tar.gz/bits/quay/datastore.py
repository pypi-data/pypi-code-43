# -*- coding: utf-8 -*-
"""Datastore Class file."""

from google.cloud import datastore


class Datastore(object):
    """Datastore class."""

    def __init__(
        self,
        auth=None,
        quay=None,
        project='broad-quay'
    ):
        """Initialize a class instance."""
        self.auth = auth
        self.datastore = datastore
        self.quay = quay
        self.project = project

        self.verbose = False
        if self.quay:
            self.verbose = self.quay.verbose

        self.db = datastore.Client(self.project)

    #
    # helpers
    #
    def list_entities(self, kind):
        """Return a list of all entities of a given kind."""
        query = self.db.query(kind=kind)
        return list(query.fetch())

    def list_entities_dict(self, kind):
        """Return a dict of all entities of a given kind."""
        entities = {}
        query = self.db.query(kind=kind)
        for entity in query.fetch():
            entity_key = entity.key.id
            if not entity_key:
                entity_key = entity.key.name
            entities[entity_key] = dict(entity)
        return entities

    #
    # users
    #
    def delete_user(self, emplid):
        """Delete a single user from Datastore."""
        key = self.db.key('QuayUser', emplid)
        self.db.delete(key)

    def get_users(self):
        """Return a list of users from the GitHub app."""
        return self.list_entities('QuayUser')

    def get_users_dict(self):
        """Return a list of users from the GitHub app."""
        return self.list_entities_dict('QuayUser')
