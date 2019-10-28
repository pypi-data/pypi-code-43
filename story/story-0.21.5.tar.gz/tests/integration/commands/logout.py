# -*- coding: utf-8 -*-
import os

from story.commands.logout import logout


def test_logout(runner):
    with runner.runner.isolated_filesystem():
        our_config_file = 'my_super_cool_config_file.json'
        with open(our_config_file, 'w') as f:
            f.write('my_config_file')

        assert os.path.exists(our_config_file)

        result = runner.run(logout, exit_code=0,
                            init_with_config_path=our_config_file,
                            write_default_config=False)

        assert os.path.exists(our_config_file) is False

        assert 'Storyscript CLI installation reset' in result.stdout
        assert 'story login' in result.stdout
