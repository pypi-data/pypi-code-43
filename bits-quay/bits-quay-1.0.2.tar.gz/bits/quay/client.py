# -*- coding: utf-8 -*-
"""Quay Client class file."""

import datetime


class Client(object):
    """Quay Client class."""

    def __init__(self, auth, quay):
        """Initialize a client instance."""
        self.auth = auth
        self.quay = quay

    def invoices_list(self):
        """List invoices."""
        invoices = self.quay.get_org_invoices()
        print('Found {} Quay invoices:'.format(len(invoices)))
        for i in sorted(invoices, key=lambda x: x['date']):
            date = datetime.datetime.fromtimestamp(i['date'])
            start = datetime.datetime.fromtimestamp(i['period_start'])
            end = datetime.datetime.fromtimestamp(i['period_end'])
            plan = i['plan']
            total = i['total']
            paid = 'unpaid'
            if i['paid']:
                paid = 'paid'
            print('{} Plan: {} {}-{} - ${} [{}]'.format(date, plan, start, end, total, paid))

    def members_list(self):
        """List members."""
        members = self.quay.get_org_members()
        print('Found {} Quay members:'.format(len(members)))
        for m in sorted(members, key=lambda x: x['name']):
            name = m['name']
            teams = []
            for t in m['teams']:
                teams.append(t['name'])

            print('{}: [{}]'.format(name, ', '.join(sorted(teams))))

    def repos_list(self):
        """List repos."""
        repos = self.quay.get_repos()
        print('Found {} Quay repos:'.format(len(repos)))
        for r in sorted(repos, key=lambda x: x['name']):
            name = r['name']
            namespace = r['namespace']

            visibility = 'private'
            if r['is_public']:
                visibility = 'public'

            print('{}/{} [{}]'.format(
                name,
                namespace,
                visibility,
            ))

    def teams_list(self):
        """List Quay repos."""
        org = self.quay.get_org()
        teams = org['teams']
        print('Found {} Quay teams:'.format(len(teams)))
        for team in teams:
            members = self.quay.get_org_team_members(team)
            print('\n{}:'.format(team))
            for m in sorted(members, key=lambda x: x['name']):
                # invited = False
                comment = ''
                if m['invited']:
                    comment = ' (invited)'
                print(' * %s%s' % (
                    m['name'],
                    comment,
                ))
