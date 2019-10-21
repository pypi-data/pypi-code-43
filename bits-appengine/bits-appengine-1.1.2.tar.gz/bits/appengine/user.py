# -*- coding: utf-8 -*-
"""App Engine User class file."""

import os
import logging
from flask import request
from google.cloud import datastore
from google.cloud import firestore


class User(object):
    """Uses class."""

    def __init__(
        self,
        appengine=None,
        collection='users',
        database='firestore',
        debug_user=None,
        project=None
    ):
        """Initialize a class instance."""
        self.appengine = appengine
        self.collection = collection
        self.database = database
        self.debug_user = debug_user
        self.project = project

        self.admin = False
        self.email = None
        self.id = None

        # get the logged-in user
        if self.debug_user and self.is_dev():
            # get the debug user
            self.get_debug_user()
        else:
            # get the current logged-in user from headers
            self.get_current_user()

        # get stored user from the database
        self.get_stored_user()

        # set user as a dict
        self.user = {'email': self.email, 'id': self.id}

    def __getitem__(self, key):
        """Return the value of the given attribute."""
        return self.__dict__[key]

    def __str__(self):
        """Return the string representation."""
        return 'User: {} [{}]'.format(self.email, self.id)

    def get(self, key):
        """Return the value of the given attribute."""
        return self.__getitem__(key)

    def get_current_user(self):
        """Return the current user."""
        # define headers
        user_email_header = 'x-goog-authenticated-user-email'
        user_id_header = 'x-goog-authenticated-user-id'

        # get Google IAP user's email and id from headers
        self.email = request.headers.get(user_email_header).replace('accounts.google.com:', '')
        self.id = request.headers.get(user_id_header).replace('accounts.google.com:', '')

    def get_debug_user(self):
        """Return the debug user."""
        self.email = self.debug_user.get('email')
        self.id = self.debug_user.get('id')

    def get_stored_datastore_user(self):
        """Return the user info from datastore."""
        client = datastore.Client(project=self.project)
        if not self.id:
            return
        user = client.get(client.key(self.collection, self.id))
        if user and user.get('admin'):
            self.admin = True

    def get_stored_firestore_user(self):
        """Return the user info from firestore."""
        client = firestore.Client(project=self.project)
        if not self.id:
            return
        user = client.collection(self.collection).document(self.id).get().to_dict()
        if user and user.get('admin'):
            self.admin = True

    def get_stored_user(self):
        """Return the user info from the database."""
        if self.database == 'firestore':
            return self.get_stored_firestore_user()
        elif self.database == 'datastore':
            return self.get_stored_datastore_user()
        else:
            logging.error('Unsupported database: {}'.format(self.database))

    def is_admin(self):
        """Return true if the user is an admin."""
        if self.admin:
            return True

    def is_dev(self):
        """Return true if we are in the dev environment."""
        if os.getenv('GAE_ENV', '').startswith('standard'):
            return False
        return True

    def role(self):
        """Return the user's role."""
        role = 'user'
        if self.is_admin():
            role = 'admin'
        return role
