import glob
import os
import sys
from importlib import reload
from os.path import join, expanduser, isfile, isdir
from typing import Any, Dict

import yaml
from cement.utils import shell
from prompt_toolkit.validation import ValidationError, Validator

from tb.config import configured_org_repo_dir
from tb.term import ColoredTerminal


class GitUrlValidator(Validator):

    def __init__(self, term):
        self._term = term

    def validate(self, document):
        url = document.text
        if url:
            self._term.action("\nValidating", url)
            out, err, code = shell.cmd(f'git ls-remote {url}')
            if code:
                raise ValidationError(message='Git url is either invalid or not accessible')
        else:
            raise ValidationError(message='Git url is required')


def ensure_user_tb_config(config: Dict[str, Any]):
    term = ColoredTerminal(theme=config.get('tb', {}).get('theme', {}))

    config.setdefault('tb', {})

    action_performed = False

    if 'src_dir' not in config['tb']:
        term.warn("No projects source directory defined.")
        src = term.prompt("Into which directory do you want the repositories cloned?", default=os.getcwd())
        config['tb']['src_dir'] = src
        write_config(config)
        action_performed = True

    if 'org_repo' not in config['tb']:
        term.warn("No organization configuration found.")
        options = dict(example="git@bitbucket.com:mrdon/tb-example.git",
                       atlassian="git@bitbucket.org:atlassian/tb-atlassian.git",
                       reciprocity="git@github.com:reciprocity/tb-reciprocity.git", other="Other")
        org_repo = options[term.prompt_menu(
            "What git repository contains your organization's team and repository configuration?",
            options=options)]

        term.warn(f"Got {org_repo}")
        if org_repo.lower() == "other":
            org_repo = term.prompt("Enter the git repository:", validator=GitUrlValidator(term),
                                   validate_while_typing=False)

        config['tb']['org_repo'] = org_repo
        write_config(config)

        pull_all_repositories(term)
        action_performed = True

    if 'teams' not in config['tb']:
        config_dir = configured_org_repo_dir(config)

        all_teams = []
        for config_file in [join(config_dir, f) for f in glob.glob1(config_dir, "*.yml")]:
            with open(config_file) as cf:
                all_teams += yaml.load(cf.read()).get('teams', {}).keys()

        if all_teams:
            term.info('\nChoose which team repositories to track:')
            teams_input = []
            for team in all_teams:
                if term.yesno("Do you want to track {} repositories?".format(team)):
                    teams_input.append(team)
            if teams_input:
                term.info("To clone the chosen repositories, run 'tb repo sync'")

            config['tb']['teams'] = teams_input
            write_config(config)
            pull_all_repositories(term)
            term.h1("Teams and repositories cloned successfully")
            action_performed = True

    if action_performed:
        term.success("Configuration changed.  Please rerun the command")
        sys.exit(0)


def read_user_config(term=None):
    if not term:
        term = ColoredTerminal(theme={})

    proper_config_path = join(expanduser("~"), '.tb', 'tb.yml')
    old_config_path = join(expanduser("~"), '.tb.yml')
    tb_config = proper_config_path
    migrate = False
    if not isfile(tb_config) and isfile(old_config_path):
        migrate = True
        tb_config = join(expanduser("~"), '.tb.yml')

    config = read_config(term, tb_config)

    if migrate:
        term.action("Migrating configuration to", proper_config_path)
        write_config(config)
        # os.remove(tb_config)
    return config


def read_config(term, path):
    if isfile(path):
        with open(path, 'r') as f:
            try:
                return yaml.load(f)
            except yaml.YAMLError as exc:
                term.error(exc)
    return {'tb': {}}


def pull_all_repositories(term):
    import tb.main
    reload(tb.main)
    with tb.main.TbConfigured(argv=['repo', 'sync']) as app:
        app.run()
        if app.exit_code != 0:
            term.error("Cannot pull repository")
            exit(1)


def write_config(config):
    config_dir = os.path.join(os.path.expanduser('~'), '.tb')
    if not isdir(config_dir):
        os.mkdir(config_dir)

    config_file = os.path.join(os.path.expanduser('~'), '.tb', 'tb.yml')
    with open(config_file, 'w') as outfile:
        yaml.dump(config, outfile, default_flow_style=False)
    print("\n{} saved\n".format(config_file))
