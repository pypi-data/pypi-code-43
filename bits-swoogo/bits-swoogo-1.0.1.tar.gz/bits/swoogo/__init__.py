# -*- coding: utf-8 -*-
"""Swoogo class file."""

import requests


class Swoogo(object):
    """Swoogo class."""

    def __init__(self, api_key, api_secret, verbose=False):
        """Initialize a class instance."""
        self.api_key = api_key
        self.api_secret = api_secret
        self.verbose = verbose

        self.base_url = 'https://www.swoogo.com/api/v1'

        self.access_token = self._get_access_token()

        self.headers = {
            'Authorization': 'Bearer %s' % (self.access_token),
        }

    def _get_access_token(self):
        """Return a bearer token for making authorized requests."""
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        }
        url = '%s/oauth2/token.json' % (self.base_url)
        data = 'grant_type=client_credentials'
        auth = (self.api_key, self.api_secret)
        response = requests.post(url, auth=auth, headers=headers, data=data)
        return response.json().get('access_token')

    def _get_list_items(self, url, headers, params):
        """Return the results from a paginated list."""
        response = requests.get(url, headers=headers, params=params)
        response_data = response.json()
        items = response_data.get('items', [])

        next_url = response_data.get('_links', {}).get('next', {}).get('href')
        while next_url:
            response = requests.get(next_url, headers=headers, params=params)
            response_data = response.json()
            items.extend(response_data.get('items', []))
            next_url = response_data.get('_links', {}).get('next', {}).get('href')

        return items

    #
    # Events
    #
    def get_events(self):
        """Get all events from swoogo."""
        url = '%s/events.json' % (self.base_url)
        params = {}
        response = requests.get(url, headers=self.headers, params=params)
        return response.json().get('items', [])

    #
    # Questions
    #
    def get_question(self, question_id):
        """Get a question from swoogo."""
        url = '%s/event-questions/%s.json' % (self.base_url, question_id)
        params = {}
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_questions(self, event_id):
        """Get all questions from an event in swoogo."""
        url = '%s/event-questions.json' % (self.base_url)
        params = {
            'event_id': event_id,
            'fields': 'id,name,attribute,type,page_id,sort',
            'per-page': 200,
        }
        return self._get_list_items(url, headers=self.headers, params=params)

    #
    # Registrants
    #
    def get_registrants(self, event_id, fields=None):
        """Get all registrants from an event in swoogo."""
        url = '%s/registrants.json' % (self.base_url)
        if not fields:
            fields = [
                'id',
                'first_name',
                'last_name',
                'email',
                'registration_status',
            ]
        params = {
            'event_id': event_id,
            'fields': ','.join(fields),
            'per-page': 200,
        }
        return self._get_list_items(url, headers=self.headers, params=params)

    def get_registrants_by_domain(self, event_id, registrants=None):
        """Return a dict of registrants by their email domain name."""
        if not registrants:
            registrants = self.get_registrants(event_id)
        domains = {}
        for r in registrants:
            email = r['email']
            domain = '.'.join(email.split('@')[1].split('.')[-2:])
            if domain not in domains:
                domains[domain] = []
            domains[domain].append(r)
        return domains

    def get_registrants_by_id(self, event_id, registrants=None):
        """Return a dict of registrants by their registration id."""
        if not registrants:
            registrants = self.get_registrants(event_id)
        reg_ids = {}
        for r in registrants:
            rid = r['id']
            reg_ids[rid] = r
        return reg_ids
