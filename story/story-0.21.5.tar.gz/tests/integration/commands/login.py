# -*- coding: utf-8 -*-
from story.commands.login import login


def test_login(runner, init_sample_app_in_cwd):
    with runner.runner.isolated_filesystem():
        init_sample_app_in_cwd()
        result = runner.run(login, exit_code=0)
        assert 'me@me.com' in result.stdout  # me@me.com is automatically set.
