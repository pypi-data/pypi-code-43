from Constants import (
    CUSTOMER_GIT_REPO,
    CUSTOMER_GIT_REPO_DIRECTORY,
    USERNAME,
    CUSTOMER_NAME,
    EMAIL,
)


class RequestInfo:

    def __init__(self, param_dict):
        self._customer_name = param_dict.get(CUSTOMER_NAME)
        self._username = param_dict.get(USERNAME)
        self._email = param_dict.get(EMAIL)
        self._git_repo = param_dict.get(CUSTOMER_GIT_REPO)
        self._git_repo_dir = param_dict.get(CUSTOMER_GIT_REPO_DIRECTORY)
        self.param_dict = param_dict

    @property
    def customer_name(self):
        return self._customer_name

    @property
    def username(self):
        return self._username

    @property
    def email(self):
        return self._email

    @property
    def git_repo(self):
        return self._git_repo

    @property
    def git_repo_dir(self):
        return self._git_repo_dir

    def get(self, parameter, default=None):
        return self.param_dict.get(parameter, default)
