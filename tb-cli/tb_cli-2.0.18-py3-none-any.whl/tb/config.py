import os
import re
import sys
from typing import Dict, Callable

from cement.core.config import ConfigHandler

from tb.core.exc import TbError
import site

LOCALLY_INSTALLED_TB = os.path.join(sys.prefix, "tb")
LOCALLY_USER_INSTALLED_TB = os.path.join(site.USER_BASE, "tb") if site.USER_BASE else None


def get_bundle_dir():
    if getattr(sys, 'frozen', False):
        # we are running in a bundle
        return sys._MEIPASS
    elif os.path.isdir(LOCALLY_INSTALLED_TB):
        return LOCALLY_INSTALLED_TB
    elif LOCALLY_USER_INSTALLED_TB and os.path.isdir(LOCALLY_USER_INSTALLED_TB):
        return LOCALLY_USER_INSTALLED_TB
    else:
        # we are running in a normal Python environment
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_default_config_tb_path():
    return os.path.join(get_default_config_dir(), 'tb.yml')


def get_default_config_dir():
    return os.path.join(get_bundle_dir(), 'config')


def configured_org_repo_dir(config):
    if 'src_dir' in config['tb']:
        return os.path.join(config['tb']['src_dir'], re.search('.*/([^.]+)(?=(\\.git)?)', config['tb']['org_repo']).group(1))
    else:
        return None


class ConfigObject:
    def __init__(self, name: str, config: Dict):
        self._config = config
        self.name = name

    def __getattr__(self, name: str):
        return self._config.get(name.replace('_', '-'))


class Repository(ConfigObject):
    def __init__(self, name: str, root_config: Dict, config: Dict, team_resolver: Callable[[str], 'Team']):
        super().__init__(name, config)
        self._team_resolver = team_resolver
        if 'url' not in config:
            url_pattern = root_config.get('tb').get('repo', {}).get('default-url-pattern')
            if url_pattern:
                self.url = url_pattern.format(name=name)
            else:
                raise TbError(f"Missing url for repository {name}")
        else:
            self.url = config.get('url')

        self.team_name = config.get('team')

    @property
    def team(self) -> 'Team':
        return self._team_resolver(self.team_name)


class Person(ConfigObject):
    def __init__(self, name: str, config: Dict):
        super().__init__(name, config)
        self.username = config.get('username')
        self.email = config.get('email')
        self.atlassian_id = config.get('atlassian-id')
        self.github_username = config.get('github-username')


class Team(ConfigObject):
    def __init__(self, name: str, config: Dict, person_resolver: Callable[[str], Person]):
        super().__init__(name, config)
        self._member_names = config.get('members', {})
        self.bitbucket_project = config.get('bitbucket-project')
        self._person_resolver = person_resolver

    @property
    def members(self):
        return [self._person_resolver(m) for m in self._member_names]


class Stage(ConfigObject):
    def __init__(self, name: str, config):
        super().__init__(name, config)


class Environment(ConfigObject):
    def __init__(self, name: str, config):
        super().__init__(name, config)


class ConfigManager:
    def __init__(self, app_config: ConfigHandler):
        cfg = app_config.get_dict()
        self.people: Dict[str, Person] = {name: Person(name, config)
                                          for name, config in cfg.get('people', {}).items()}
        self.teams: Dict[str, Team] = {name: Team(name, config, self.people.get)
                                       for name, config in cfg.get('teams', {}).items()}
        self.repositories: Dict[str, Repository] = {name: Repository(name, cfg, config, self.teams.get)
                                                    for name, config in cfg.get('repositories', {}).items()}
        self.stages: Dict[str, Stage] = {name: Stage(name, config)
                                         for name, config in cfg.get('stages', {}).items()}
        self.environments: Dict[str, Environment] = {name: Environment(name, config)
                                                     for name, config in cfg.get('environments', {}).items()}

        self.src_dir = cfg['tb'].get('src_dir')
        self.org_repo_dir = configured_org_repo_dir(cfg)

        if self.org_repo_dir:
            self.org_repo = Repository(os.path.basename(self.org_repo_dir), cfg, {
                'url': cfg['tb'].get('org_repo')}, self.teams.get)
        else:
            self.org_repo = None

        self.selected_teams = [t for t in self.teams.values() if t.name in cfg['tb'].get('teams', {})]






