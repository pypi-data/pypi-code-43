# -*- coding: utf-8 -*-
"""GitHub Helpers class file."""

import dateparser


class Helpers(object):
    """GitHub Helpers class."""

    def __init__(self, auth=None, github=None):
        """Initialize a class instance."""
        self.auth = auth
        self.github = github

        self.verbose = False
        if self.github:
            self.verbose = self.github.verbose

    def get_org_members_full(self):
        """Return a list of org members with full details."""
        firestore = self.github.firestore(app_project='broad-github-app')
        firestore_members = firestore.get_members_dict()

        # assemble a list of members and their full records
        members = []

        if self.verbose:
            print('Getting org members...')
        for m in sorted(self.github.get_org_members(), key=lambda x: x['login'].lower()):
            mid = m['id']
            login = m['login'].lower()

            # check for cached record
            cached = firestore_members.get(mid)

            # check last modified
            last_modified = None
            if cached and cached.get('updated_at'):
                updated_at = dateparser.parse(cached['updated_at'])
                last_modified = updated_at.strftime('%a, %d %b %Y %H:%M:%S GMT')
                user = self.github.get_user(login, last_modified=last_modified)
            else:
                user = self.github.get_user(login)

            # check if record was updated
            if user is False:
                members.append(cached)
                if self.verbose:
                    print('Skipped user: {}'.format(login))
            else:
                members.append(user)
                # firestore.db.collection('github_members').document(str(mid)).set(user)
                if self.verbose:
                    print('Updated user: {}'.format(login))

        return members

    def get_org_repos_full(self):
        """Return a list of org repos with full details."""
        firestore = self.github.firestore(app_project='broad-github-app')
        firestore_repos = firestore.get_repos_dict()

        # assemble a list of repos and their full records
        repos = []
        for r in sorted(self.github.get_org_repos(), key=lambda x: x['name'].lower()):
            rid = r['id']
            name = r['name'].lower()

            # check for cached record
            cached = firestore_repos.get(rid)

            # check last modified
            last_modified = None
            if cached and cached.get('updated_at'):
                updated_at = dateparser.parse(cached['updated_at'])
                last_modified = updated_at.strftime('%a, %d %b %Y %H:%M:%S GMT')
                repo = self.github.get_repo(name, last_modified=last_modified)
            else:
                repo = self.github.get_repo(name)

            # check if record was updated
            if repo is False:
                repos.append(cached)
                if self.verbose:
                    print('Skipped repo: {}'.format(name))
            else:
                repos.append(repo)
                # firestore.db.collection('github_repos').document(str(rid)).set(repo)
                if self.verbose:
                    print('Updated repo: {}'.format(name))

        return repos

    def get_org_teams_full(self):
        """Return a list of org teams with full details."""
        firestore = self.github.firestore(app_project='broad-github-app')
        firestore_teams = firestore.get_teams_dict()

        # assemble a list of teams and their full records
        teams = []
        for t in sorted(self.github.get_org_teams(), key=lambda x: x['name'].lower()):
            tid = t['id']
            name = t['name'].lower()

            # check for cached record
            cached = firestore_teams.get(tid)

            # check last modified
            last_modified = None
            if cached and cached.get('updated_at'):
                updated_at = dateparser.parse(cached['updated_at'])
                last_modified = updated_at.strftime('%a, %d %b %Y %H:%M:%S GMT')
                team = self.github.get_team(tid, last_modified=last_modified)
            else:
                team = self.github.get_team(tid)

            # check if record was updated
            if team is False:
                teams.append(cached)
                if self.verbose:
                    print('Skipped team: {}'.format(name))
            else:
                teams.append(team)
                # firestore.db.collection('github_teams').document(str(tid)).set(team)
                if self.verbose:
                    print('Updated team: {}'.format(name))

        return teams

    def get_org_repos_collaborators(self):
        """Return a list of org repos collaborators."""
        repos_collaborators = []
        for r in sorted(self.github.get_org_repos(), key=lambda x: x['name'].lower()):
            rid = r['id']
            name = r['name'].lower()

            # get repo collaborators
            collaborators = []
            for m in self.github.get_repo_collaborators(name):
                collaborators.append({'id': m['id'], 'login': m['login'].lower()})

            repo = {
                'id': rid,
                'name': name,
                'collaborators': collaborators,
            }
            repos_collaborators.append(repo)
            # firestore.db.collection('github_repos_collaborators').document(str(rid)).set(repo)
            if self.verbose:
                print('Updated repo collaborators: {}'.format(name))

        return repos_collaborators

    def get_org_teams_members(self):
        """Return an iterator of org teams and their members."""
        for t in sorted(self.github.get_org_teams(), key=lambda x: x['slug'].lower()):
            tid = t['id']
            slug = t['slug']

            # get team members
            members = []
            for m in self.github.get_team_members(tid):
                members.append({'id': m['id'], 'login': m['login'].lower()})

            team = {
                'id': tid,
                'slug': slug,
                'members': members,
            }
            if self.verbose:
                print('Retrieved {} members from team: {}'.format(len(members), slug))

            yield team

    def get_org_teams_repos(self):
        """Return an iterator of org teams and their repos."""
        for t in sorted(self.github.get_org_teams(), key=lambda x: x['slug'].lower()):
            tid = t['id']
            slug = t['slug']

            # get team repos
            repos = []
            for r in self.github.get_team_repos(tid):
                repos.append({'id': r['id'], 'name': r['name']})

            team = {
                'id': tid,
                'slug': slug,
                'repos': repos,
            }
            if self.verbose:
                print('Retrieved {} repos from team: {}'.format(len(repos), slug))

            yield team
