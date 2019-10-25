# -*- coding: utf-8 -*-
"""Slack class file."""

import os
import re
import slack
import time


class Slack(object):
    """Slack class."""

    def __init__(self, token, env='test', notifications='#bitsdb-dev'):
        """Initialize an Slack class instance."""
        # app token
        self.token = token

        # environment
        self.env = env

        # channel to use for notifications
        self.notifications = notifications

        # user running the CLI
        self.unix_user = os.environ.get('USER', None)

        # connect to slack web client
        self.client = slack.WebClient(token=token)

        # collections
        self.groups = None
        self.usergroups = None
        self.users = None

    # channels
    def get_channels(self, exclude_archived=False):
        """Return a list of Slack channels."""
        if exclude_archived:
            exclude_archived = 1
        else:
            exclude_archived = 0
        return self.client.channels_list(
            exclude_archived=exclude_archived
        ).get('channels', [])

    def get_channels_dict(self):
        """Return a dict of Slack channels by id."""
        channels = {}
        for channel in self.get_channels():
            cid = channel['id']
            channels[cid] = channel
        return channels

    def invite_channel_member(self, channel, user):
        """Invite a user to a channel."""
        return self.client.channels_invite(channel=channel, user=user)

    def post_message(self, channel, text):
        """Post a message to a channel."""
        if self.env:
            text = '%s [%s@%s]' % (text, self.unix_user, self.env)
        try:
            return self.client.chat_postMessage(
                as_user=False,
                username='BITSdb-cli',
                channel=channel,
                text=text
            )
        except Exception as e:
            print('ERROR posting message to Slack channel: %s' % (channel))
            print(e)

    # conversations
    def get_conversations(self):
        """Return a list of Slack conversations."""
        return self.client.conversations_list(
            limit=1000,
        ).get('channels', [])

    def get_conversations_dict(self):
        """Return a dict of Slack conversations by id."""
        conversations = {}
        for conversation in self.get_conversations():
            cid = conversation['id']
            conversations[cid] = conversation
        return conversations

    # groups
    def get_group_info(self, channel):
        """Return info for a Slack channel."""
        return self.client.groups_info(channel=channel)

    def get_groups(self):
        """Return a list of Slack groups."""
        return self.client.groups_list().get('groups', [])

    def get_groups_dict(self):
        """Return a dict of Slack groups by id."""
        groups = {}
        for group in self.get_groups():
            gid = group['id']
            groups[gid] = group
        return groups

    def invite_group_member(self, channel, user):
        """Invite a user to a group."""
        return self.client.groups_invite(channel=channel, user=user)

    def kick_group_member(self, channel, user):
        """Remove a user group."""
        return self.client.groups_kick(channel=channel, user=user)

    # usergroups
    def get_usergroups(self):
        """Return a list of Slack usergroups."""
        return self.client.usergroups_list().get('usergroups', [])

    def get_usergroups_dict(self):
        """Return a dict of Slack usergroups by id."""
        usergroups = {}
        for usergroup in self.get_usergroups():
            uid = usergroup['id']
            usergroups[uid] = usergroup
        return usergroups

    # users
    def get_user(self, user):
        """Return a Slack user."""
        return self.client.users_profile_get(user=user)

    def get_users(self):
        """Return a list of Slack users."""
        return self.client.users_list().get('members', [])

    def get_users_dict(self, key='id'):
        """Return a dict of Slack users by id."""
        users = {}
        for user in self.get_users():
            k = user[key]
            if k:
                users[k] = user
        return users

    def get_users_by_class(self, users=None):
        """Return a dict of users by class."""
        if not users:
            users = self.get_users()
        classes = {
            'bots': [],
            'broad': [],
            'deleted': [],
            'restricted': [],
            'ultra_restricted': [],
            'other': [],
        }
        for user in users:
            # skip deleted users
            if user['deleted']:
                classes['deleted'].append(user)
                continue
            # get user email
            email = '%s' % (user['profile'].get('email', ''))
            # sort into classes
            if not email:
                classes['bots'].append(user)
            elif user['is_ultra_restricted']:
                classes['ultra_restricted'].append(user)
            elif user['is_restricted']:
                classes['restricted'].append(user)
            elif re.search('@broadinstitute.org', email):
                classes['broad'].append(user)
            else:
                classes['other'].append(user)
        return classes

    def get_users_by_email(self):
        """Return a dict of slack users."""
        slack_users = self.get_users()
        users = {}
        for user in slack_users:
            email = user['profile'].get('email')
            if email:
                users[email] = user
        return users

    def _get_profile(self, user, retries=0):
        """Return a profile."""
        # check number of retries
        max_retries = 3
        if retries >= max_retries:
            return None

        # attempt to get the user's profile.
        try:
            return self.client.users_profile_get(user=user)

        # otherwise, sleep until retry time and try again
        except slack.errors.SlackApiError as e:
            print('ERROR: {}'.format(e))
            while e.response.headers.get('retry-after', 0):
                retries += 1
                retry_after = int(e.response.headers.get('retry-after', 0))
                sleep = retry_after * 2

                print('Sleeping %s...' % (sleep))
                time.sleep(sleep)

                print('Retrying [%s]...' % (retries))
                return self._get_profile(user, retries)

    def get_users_profiles(self):
        """Return a dict of slack users profiles."""
        users = self.get_users()
        profiles = []
        count = 0
        for user in sorted(users, key=lambda x: x['updated']):
            count += 1
            uid = user['id']
            print('%s/%s: %s' % (count, len(users), uid))
            profile = self._get_profile(uid)
            if profile:
                profiles.append(profile)
        return profiles

    def set_user_email(self, user, email):
        """Set a user's email."""
        return self.client.users_profile_set(
            user=user,
            name='email',
            value=email,
        )
