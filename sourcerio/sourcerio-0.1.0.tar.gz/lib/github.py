from github import Github

class GithubWrapper(object):
    def __init__(self, api_key):
        self.api_key = api_key

    def list_repositories(self):
        repos = []

        client = Github(self.api_key)
        for repo in client.get_user().get_repos():
            repos.append(repo.ssh_url)

        return repos