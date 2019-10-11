# -*- coding: utf-8 -*-
"""GitHub Client class file."""

import re


class Client(object):
    """GitHub Client class."""

    def __init__(self, auth, github):
        """Initialize a class instance."""
        self.auth = auth
        self.github = github

        self.datastore = self.github.datastore(auth)
        self.firestore = self.github.firestore(auth)

    def broadies_list(self):
        """List Broad GitHub Users."""
        print('Getting People from Firestore...')
        people = self.firestore.get_people()
        users = []
        for person in sorted(people, key=lambda x: x.get('email_username', '').lower()):
            if not person.get('github_id'):
                continue
            print('{} -> {} [{}]'.format(
                person['email_username'],
                person['github_login'],
                person['github_id'],
            ))
            users.append(person)
        print('Total Linked GitHub Users: {}'.format(len(users)))

    def collaborators_list(self):
        """List GitHub Collaborators."""
        print('Getting GitHub collaborators...')
        github_collaborators = self.github.get_org_outside_collaborators()
        print('Found {} collaborators in organization: {}.'.format(
            len(github_collaborators),
            self.github.org,
        ))
        for c in sorted(github_collaborators, key=lambda x: x['login'].lower()):
            print('{} [{}]'.format(c['login'].lower(), c['id']))

    def invitations_list(self):
        """List GitHub Invitations."""
        print('Getting GitHub invitations...')
        github_invitations = self.github.get_org_invitations()
        print('Found {} invitations in organization: {}.'.format(
            len(github_invitations),
            self.github.org,
        ))
        for i in sorted(github_invitations, key=lambda x: x['login'].lower()):
            print('{}: {} ({}) [{}]'.format(
                i['login'].lower(),
                i['created_at'],
                i['role'],
                i['id'],
            ))

    def members_list(self, insecure=False):
        """List GitHub Members."""
        print('Getting GitHub members...')
        github_members = self.github.get_org_members(insecure=insecure)
        print('Found {} members in organization: {}.'.format(
            len(github_members),
            self.github.org,
        ))
        for m in sorted(github_members, key=lambda x: x['login'].lower()):
            admin = ''
            if m['site_admin']:
                admin = ' (admin)'
            print('{} [{}]{}'.format(
                m['login'].lower(),
                m['id'],
                admin
            ))

    def organization_audit(self):
        """Audit the github organiztaion."""
        print('Organization Name: {}'.format(self.github.org))

        print('\nGetting organization members...')
        members = self.github.get_org_members()
        print('Found {} organization members.'.format(len(members)))

        print('\nGetting organization collaborators...')
        collaborators = self.github.get_org_outside_collaborators()
        print('Found {} organization collaborators.'.format(len(collaborators)))

        print('\nGetting owner account members...')
        owners = self.github.get_org_members(role='admin')
        for user in sorted(owners, key=lambda x: x['login'].lower()):
            print('   * {} [{}]'.format(user['login'].lower(), user['id']))
        print('Found {} owner account members.'.format(len(owners)))

        print('\nGetting role account members...')
        role_members = self.github.get_team_members(self.github.role_team)
        for user in sorted(role_members, key=lambda x: x['login'].lower()):
            print('   * {} [{}]'.format(user['login'].lower(), user['id']))
        print('Found {} role account members.'.format(len(role_members)))

        print('\nGetting open organization invitations...')
        invitations = self.github.get_org_invitations()
        for i in sorted(invitations, key=lambda x: x['login'].lower()):
            print('   * {} [{}]'.format(i['login'].lower(), i['id']))
        print('Found {} open organization invitations.'.format(len(invitations)))

        print('\nGetting organization repos...')
        repos = self.github.get_org_repos()
        private_repos = []
        public_repos = []
        for r in sorted(repos, key=lambda x: x['name']):
            if r['private']:
                private_repos.append(r)
            else:
                public_repos.append(r)
        print('   * private repos: {}'.format(len(private_repos)))
        print('   * public repos: {}'.format(len(public_repos)))
        print('Found {} organization repos.'.format(len(repos)))

        print('\nGetting organization teams...')
        teams = self.github.get_org_teams()
        print('Found {} organization teams.'.format(len(teams)))

    def public_members_list(self):
        """List GitHub Public Mmebers."""
        print('Getting GitHub public_members...')
        github_members = self.github.get_org_public_members()
        print('Found {} public_members in organization: {}.'.format(
            len(github_members),
            self.github.org,
        ))
        for m in sorted(github_members, key=lambda x: x['login'].lower()):
            print('{} [{}]'.format(m['login'].lower(), m['id']))

    def repo_hooks_list(self):
        """List GitHub Repo Hooks."""
        print('Getting GitHub repos...')
        github_repos = self.github.get_org_repos()
        print('Found {} repos in organization: {}.'.format(
            len(github_repos),
            self.github.org,
        ))
        for r in sorted(github_repos, key=lambda x: x['name']):
            hooks = self.github.get_repo_hooks(r['name'])
            if hooks:
                print('{}/{}:'.format(self.github.org, r['name']))
                for h in hooks:
                    # get repo hook name
                    name = h['name']
                    if name == 'web':
                        name = h['config'].get('url')
                    # get repo hook status
                    status = 'inactive'
                    if h['active']:
                        status = 'active'
                    print('  - {}: ({})'.format(name, status))

    def repo_hooks_search(self, query):
        """List GitHub Repo Hooks."""
        print('Getting GitHub repos...')
        github_repos = self.github.get_org_repos()
        print('Found {} repos in organization: {}.'.format(
            len(github_repos),
            self.github.org,
        ))
        for r in sorted(github_repos, key=lambda x: x['name']):
            hooks = self.github.get_repo_hooks(r['name'])
            if hooks:
                matches = []
                for h in hooks:
                    name = h['name']
                    if name == 'web':
                        name = h['config'].get('url')
                    h['displayName'] = name
                    # find a match
                    if re.search(query, name):
                        matches.append(h)
                if matches:
                    print('{}/{}:'.format(self.github.org, r['name']))
                for h in matches:
                    status = 'inactive'
                    if h['active']:
                        status = 'active'
                    print('  - {}: ({}) [{}]'.format(
                        h['displayName'],
                        h['config']['content_type'],
                        status,
                    ))

    def repos_list(self):
        """List GitHub Repos."""
        print('Getting GitHub repos...')
        github_repos = self.github.get_org_repos()
        print('Found {} repos in organization: {}.'.format(
            len(github_repos),
            self.github.org,
        ))
        for r in sorted(github_repos, key=lambda x: x['name']):
            print('{} [{}]'.format(r['name'], r['id']))

    def role_accounts_list(self):
        """List GitHub Role Accounts."""
        print('Getting GitHub Role Accounts...')
        team = self.github.get_team(self.github.role_team)
        role_accounts = self.github.get_team_members(team['id'])
        for m in sorted(role_accounts, key=lambda x: x['login'].lower()):
            print('{} [{}]'.format(m['login'].lower(), m['id']))

    def services_list(self):
        """List GitHub Services."""
        print('Getting GitHub repos...')
        github_repos = self.github.get_org_repos()
        print('Found {} repos in organization: {}.'.format(
            len(github_repos),
            self.github.org,
        ))
        for r in sorted(github_repos, key=lambda x: x['name']):
            hooks = self.github.get_repo_hooks(r['name'])
            if hooks:
                output = ''
                for h in hooks:
                    name = h['name']
                    if name == 'web':
                        continue
                    # get hook status
                    status = 'inactive'
                    if h['active']:
                        status = 'active'
                    # set output
                    output += '  - {}: ({})\n'.format(
                        name,
                        status
                    )
                if output:
                    print('{}/{}:'.format(self.github.org, r['name']))
                    print(output)

    def teams_audit(self):
        """Audit github teams."""
        print('\nGetting organization teams...')
        teams = self.github.get_org_teams()
        print('Found {} organization teams.'.format(len(teams)))

        print('\nGetting cached teams members...')
        teams_members = self.firestore.get_teams_members_dict()
        print('Found {} teams members.'.format(len(teams_members)))

        print('\nGetting cached teams repos...')
        teams_repos = self.firestore.get_teams_repos_dict()
        print('Found {} teams repos.'.format(len(teams_repos)))

        print('\nGetting org admins...')
        owners = self.github.get_org_members(role="admin")
        print('Found {} org admins.'.format(len(owners)))

        print('\nGetting team syncs...')
        team_syncs = self.firestore.get_team_syncs_dict()
        print('Found {} team syncs.'.format(len(team_syncs)))

        print('\nChecking for teams with no members or no repos:')

        nomembers = []
        norepos = []
        onemember = []
        for t in sorted(teams, key=lambda x: x['slug']):
            tid = t['id']
            tmembers = teams_members.get(tid, {})
            trepos = teams_repos.get(tid, {})
            if not tmembers.get('members', []):
                nomembers.append(t)
            if len(tmembers.get('members', [])) == 1:
                onemember.append(t)
            if not trepos.get('repos', []):
                norepos.append(t)

        print('Found {} teams with no members.'.format(len(nomembers)))
        print('Found {} teams with one member.'.format(len(onemember)))
        print('Found {} teams with no repos.'.format(len(norepos)))

        if nomembers:
            print('\nTeams with no members:')
            for team in sorted(nomembers, key=lambda x: x['slug']):
                slug = team['slug']
                team_url = 'https://github.com/orgs/broadinstitute/teams'
                note = ''
                if slug in team_syncs:
                    note = ' - syncing from {}!'.format(
                        team_syncs[slug]['google_group'],
                    )
                print('   * {} [{}]: {}/{}{}'.format(
                    slug,
                    t['id'],
                    team_url,
                    slug,
                    note
                ))

        if onemember:
            print('\nTeams with one member:')
            for team in sorted(onemember, key=lambda x: x['slug']):
                slug = team['slug']
                team_url = 'https://github.com/orgs/broadinstitute/teams'
                note = ''
                if slug in team_syncs:
                    note = ' - syncing from {}!'.format(
                        team_syncs[slug]['google_group'],
                    )
                print('   * {} [{}]: {}/{}{}'.format(
                    slug,
                    t['id'],
                    team_url,
                    slug,
                    note
                ))

        if norepos:
            print('\nTeams with no repos:')
            for team in sorted(norepos, key=lambda x: x['slug']):
                slug = team['slug']
                team_url = 'https://github.com/orgs/broadinstitute/teams'
                note = ''
                if slug in team_syncs:
                    note = ' - syncing from {}!'.format(
                        team_syncs[slug]['google_group'],
                    )
                print('   * {} [{}]: {}/{}{}'.format(
                    slug,
                    t['id'],
                    team_url,
                    slug,
                    note
                ))

        print('\nTeams with Google Group Syncs [{}]:'.format(len(team_syncs)))
        for slug in sorted(team_syncs):
            sync = team_syncs[slug]
            tid = sync['github_team']

            maintainers = self.github.get_team_members(tid, role='maintainer')
            logins = []
            for user in maintainers:
                uid = user['id']
                if uid in owners:
                    continue
                login = user['login']
                logins.append(login)

            print('   * {} <-- {}: {}'.format(
                slug,
                sync['google_group'],
                ', '.join(sorted(logins))
            ))

        nomaintainer = []

        print('\nTeams without Google Group Syncs [{}]:'.format(
            len(teams) - len(team_syncs)
        ))

        print('\n  With a Maintainer:')
        for team in sorted(teams, key=lambda x: x['slug']):
            tid = team['id']
            slug = team['slug']
            if slug in team_syncs:
                continue

            maintainers = self.github.get_team_members(tid, role='maintainer')
            logins = []
            for user in maintainers:
                login = user['login']
                logins.append(login)

            if not logins:
                nomaintainer.append(team)
                continue

            print('     * {} [{}]: {}'.format(
                slug,
                tid,
                ', '.join(sorted(logins)),
            ))

        print('\n  Without a Maintainer:')
        for team in sorted(nomaintainer, key=lambda x: x['slug']):
            slug = team['slug']
            print('     * {} [{}]'.format(slug, team['id']))

    def team_syncs_list(self):
        """List GitHub Team Syncs."""
        print('Getting GitHub team syncs...')
        team_syncs = self.firestore.get_team_syncs_dict()
        print('Found {} syncs.'.format(len(team_syncs)))
        for oid in sorted(team_syncs, key=lambda x: team_syncs[x]['google_group']):
            s = team_syncs[oid]
            print('{} --> {} [{}]'.format(
                s['google_group'],
                s['github_team_slug'],
                s['github_team']
            ))

    def teams_list(self):
        """List Github teams."""
        print('Getting GitHub teams...')
        teams = self.github.get_org_teams()
        print('Found {} teams in organization: {}.'.format(len(teams), self.github.org))
        for r in sorted(teams, key=lambda x: x['slug']):
            print('{} [{}]'.format(r['slug'], r['id']))
