# -*- coding: utf-8 -*-
"""GitHub App class file."""

import datetime
import logging


class App(object):
    """GitHub App class."""

    def __init__(self, auth=None, github=None):
        """Initialize a class instance."""
        self.auth = auth
        self.github = github

        self.verbose = False
        if self.github:
            self.verbose = self.github.verbose

    #
    # tokens - tokens in firestore
    #
    def save_token(self, user, github_user, token):
        """Save a GitHUb user's token in Firestore."""
        google_email = user.get('email')
        google_id = user.get('id')

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
