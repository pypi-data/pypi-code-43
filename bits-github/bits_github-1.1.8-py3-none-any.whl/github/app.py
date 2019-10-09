# -*- coding: utf-8 -*-
"""GitHub App class file."""

import datetime
import logging


class App(object):
    """GitHub App class."""

    def __init__(self, auth=None, github=None, debug=False, debug_user=None):
        """Initialize a class instance."""
        self.auth = auth
        self.debug = debug
        self.debug_user = debug_user
        self.github = github

        self.verbose = False
        if self.github:
            self.verbose = self.github.verbose

    #
    # users - app users in firestore
    #
    def is_admin(self, request):
        """Return true if the user is an admin."""
        google_id = self.user_id(request)
        user = self.github.firestore().get_user(google_id)
        if user and user['admin']:
            return True
        return False

    #
    # tokens - tokens in firestore
    #
    def save_token(self, request, github_user, token):
        """Save a GitHUb user's token in Firestore."""
        # get authenticated user
        auth_user = self.user(request)
        google_email = auth_user.get('email')
        google_id = auth_user.get('id')

        # get github info from github user
        github_id = github_user.get('id')
        github_login = github_user.get('login')

        data = {
            'github_id': github_id,
            'github_login': github_login,
            'google_email': google_email,
            'google_id': google_id,
            'token': token,
            'updated': datetime.datetime.now().isoformat(),
        }

        if not github_id or not github_login or not token:
            logging.error('Invalid GitHub token info for user: %s [%s]' % (
                google_email,
                google_id,
            ))
            logging.error('GitHub User Data: %s' % (github_user))
            return

        # save user in firestore
        return self.github.firestore().app.collection('tokens').document(google_id).set(data)

    #
    # github users - github_users in firestore
    #
    def save_user(self, github_user):
        """Save a GitHUb user's token in Firestore."""
        user_id = github_user.get('id')
        if not user_id:
            logging.error('Failed to save GitHub user. ID not found')
            return
        github_id = str(user_id)
        return self.github.firestore().app.collection('github_users').document(github_id).set(github_user)

    #
    # user - logged in user from request headers
    #
    def user(self, request):
        """Return the current user."""
        # for debugging, return the debug user passed to the function
        if self.debug_user:
            return self.debug_user
        # get user email and id from headers
        google_email = request.headers.get('X-Goog-Authenticated-User-Email')
        google_id = request.headers.get('X-Goog-Authenticated-User-ID')
        print('Email: %s' % (google_email))
        print('ID: %s' % (google_id))
        data = {
            'email': google_email.replace('accounts.google.com:', ''),
            'id': google_id.replace('accounts.google.com:', ''),
        }
        return data

    def user_id(self, request):
        """Return the Google ID of the logged-in user."""
        user = self.user(request)
        return user.get('id')
