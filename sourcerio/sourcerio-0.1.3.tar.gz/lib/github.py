from github import Github

class GithubWrapper(object):
    def __init__(self, api_key, organization):
        self.api_key = api_key
        self.organization = organization

    def list_repositories(self):
        repos = []

        client = Github(self.api_key)
        for repo in client.get_organization(self.organization).get_repos():
            repos.append(repo.ssh_url)

        return sorted(repos)
