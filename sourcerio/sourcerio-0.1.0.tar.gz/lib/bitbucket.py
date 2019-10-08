import json

from lib.http import Http
from lib.logging import info

class Bitbucket(object):
    def __init__(self, user, password, organization):
        self.api_url = 'https://api.bitbucket.org/2.0'
        self.organization = organization
        self.password = password
        self.user = user

    def list_repositories(self):
        repos = []

        url = '%s/repositories/%s' % (self.api_url, self.organization)
        info('[bitbucket] listing repositories')

        get_next_page = True
        while get_next_page:
            http = Http(self.user, self.password)
            data = json.loads(http.get(url))

            for repo in data['values']:
                for link in repo['links']['clone']:
                    if link['name'] == 'ssh':
                        repos.append(link['href'])

            if 'next' in data:
                url = data['next']
            else:
                get_next_page = False

        return sorted(repos)
