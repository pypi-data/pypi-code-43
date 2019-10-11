import os
from collections import OrderedDict
from typing import MutableMapping

import yaml

from dataclasses import dataclass

from .exceptions import ConfigNotFoundError
from .uploaders.base import BaseUploader

DEFAULT_CONFIG_LOCATIONS = [
    './.package_uploader.yml',
    '~/.package_uploader.yml',
]


@dataclass
class RepositorySettings:
    type: str
    location: dict
    auth: dict


@dataclass
class Settings:
    repositories: MutableMapping[str, RepositorySettings] = None

    def __init__(self, *args, **kwargs):
        self.repositories = OrderedDict()
        super().__init__(*args, **kwargs)

    def config_setup(self, config_dict):
        for repository, config in config_dict['repositories'].items():
            self.repositories[repository] = RepositorySettings(**config)

    def get_repository(self, repository_name):
        if not hasattr(self, '_repositories_cache'):
            self._repositories_cache = {}
        if repository_name not in self._repositories_cache:
            repository_conf = self.repositories[repository_name]
            self._repositories_cache[repository_name] = BaseUploader.registry.get_uploader_class(repository_conf.type)(
                location=repository_conf.location, auth=repository_conf.auth,
            )
        return self._repositories_cache[repository_name]


def setup(locations=None):
    if locations is None:
        locations = DEFAULT_CONFIG_LOCATIONS
    locations = (
        os.path.abspath(os.path.expanduser(location)) for location in locations
    )
    try:
        location = next(
            location for location in locations
            if os.path.exists(location)
        )
    except StopIteration:
        raise ConfigNotFoundError

    with open(location) as fd:
        settings.config_setup(yaml.safe_load(fd))


settings = Settings()
