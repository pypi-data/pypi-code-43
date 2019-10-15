# -*- coding: utf-8 -*-
"""Google Cloud Search API."""


from bits.google.services.base import Base
from googleapiclient.discovery import build


class CloudSearch(Base):
    """CloudBilling class."""

    def __init__(self, credentials):
        """Initialize a class instance."""
        self.cloudsearch = build('cloudsearch', 'v1', credentials=credentials)

    def get_stats(self, params):
        """Return stats."""
        return self.cloudsearch.stats().getIndex(**params).execute().get('stats', [])
