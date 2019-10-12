# -*- coding: utf-8 -*-
"""Quay App class file."""

import datetime
import logging


class App(object):
    """Quay App class."""

    def __init__(self, auth=None, quay=None):
        """Initialize a class instance."""
        self.auth = auth
        self.quay = quay

        self.verbose = False
        if self.quay:
            self.verbose = self.quay.verbose

    #
    # tokens - tokens in firestore
    #
    def save_token(self, user, quay_user, token):
        """Save a Quay user's token in Firestore."""
        google_email = user.get('email')
        google_id = user.get('id')

        # get quay info from quay user
        quay_username = quay_user.get('username')

        data = {
            'quay_username': quay_username,
            'google_email': google_email,
            'google_id': google_id,
            'token': token,
            'updated': datetime.datetime.now().isoformat(),
        }

        if not quay_username or not token:
            logging.error('Invalid Quay token info for user: %s [%s]' % (
                google_email,
                google_id,
            ))
            logging.error('Quay User Data: %s' % (quay_user))
            return

        # save user in firestore
        return self.quay.firestore().app.collection('tokens').document(google_id).set(data)

    #
    # quay users - quay_users in firestore
    #
    def save_user(self, quay_user):
        """Save a GitHUb user's token in Firestore."""
        username = quay_user.get('username')
        if not username:
            logging.error('Failed to save Quay user. Username not found')
            return
        return self.quay.firestore().app.collection('quay_users').document(username).set(quay_user)
