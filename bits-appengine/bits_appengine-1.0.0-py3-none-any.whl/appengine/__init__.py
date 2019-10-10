# -*- coding: utf-8 -*-
"""Example class file."""

from flask import request


class AppEngine(object):
    """AppEngine class."""

    def __init__(self, debug_user=None):
        """Initialize an Example class instance."""
        self.debug_user = debug_user

    def email(self):
        """Return the Google primary email of the logged-in user."""
        return self.user().get('email')

    def user(self):
        """Return the current user."""
        # for debugging, return the debug user passed to the function
        if self.debug_user:
            return self.debug_user

        # get user email and id from headers
        google_email = request.headers.get('X-Goog-Authenticated-User-Email')
        google_id = request.headers.get('X-Goog-Authenticated-User-ID')

        # create the user dict
        user_data = {
            'email': google_email.replace('accounts.google.com:', ''),
            'id': google_id.replace('accounts.google.com:', ''),
        }
        return user_data

    def user_id(self):
        """Return the Google ID of the logged-in user."""
        return self.user().get('id')
