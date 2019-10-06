# -*- coding: utf-8 -*-
"""Google Cloud Identity API."""

import re

from bits.google.services.base import Base
from googleapiclient.discovery import build


class CloudIdentity(Base):
    """CloudIdentity class."""

    def __init__(self, credentials):
        """Initialize a class instance."""
        self.ci = build('cloudidentity', 'v1', credentials=credentials)

    #
    # Groups
    #
    def get_group(self, name):
        """Return a Cloud Identity Group."""
        if not re.match('groups/', name):
            name = 'groups/{}'.format(name)
        return self.ci.groups().get(name=name).execute()

    def get_groups(self, parent, view='BASIC', pageSize=1000):
        """Return a list of groups."""
        if not re.match('customers/', parent):
            parent = 'customers/{}'.format(parent)
        params = {
            'parent': parent,
            'view': view,
            'pageSize': pageSize,
        }
        groups = self.ci.groups()
        request = groups.list(**params)
        return self.get_list_items(groups, request, 'groups')

    def lookup_group(self, groupKey):
        """Return Name of a Cloud Identity Group."""
        params = {
            'groupKey_id': groupKey
        }
        return self.ci.groups().lookup(**params).execute()

    def search_groups(self, query, view='BASIC', pageSize=1000):
        """Return results of a group search."""
        params = {
            'query': query,
            'view': view,
            'pageSize': pageSize,
        }
        groups = self.ci.groups()
        request = groups.search(**params)
        return self.get_list_items(groups, request, 'groups')
