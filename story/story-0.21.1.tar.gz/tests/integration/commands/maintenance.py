# -*- coding: utf-8 -*-
from pytest import mark


@mark.parametrize('enabled', [True, False])
def test_check(runner, patch, enabled, init_sample_app_in_cwd):
    with runner.runner.isolated_filesystem():
        init_sample_app_in_cwd()
        from story import api
        from story.commands import maintenance

        patch.object(api.Apps, 'maintenance', return_value=enabled)

        result = runner.run(maintenance.check, exit_code=0)

    assert 'Fetching maintenance mode' in result.stdout
    if enabled:
        assert 'ON. Application is disabled.' in result.stdout
    else:
        assert 'off. Application is running.' in result.stdout

    api.Apps.maintenance.assert_called_with(app='my_app', maintenance=None)


@mark.parametrize('enable,assert_messages', [
    (True, ['Enabling maintenance mode for app my_app',
            'Application is now in maintenance–mode']),
    (False, ['Disabling maintenance mode for app my_app',
             'Application is now running.']),
])
def test_on_and_off(runner, patch, init_sample_app_in_cwd, enable,
                    assert_messages):
    with runner.runner.isolated_filesystem():
        init_sample_app_in_cwd()
        from story import api
        from story.commands import maintenance

        patch.object(api.Apps, 'maintenance')

        if enable:
            result = runner.run(maintenance.on, exit_code=0)
        else:
            result = runner.run(maintenance.off, exit_code=0)

    for m in assert_messages:
        assert m in result.stdout

    api.Apps.maintenance.assert_called_with(app='my_app', maintenance=enable)
