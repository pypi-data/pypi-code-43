# -*- coding: utf-8 -*-
import click

from story.commands.feedback import feedback


def test_feedback(runner, patch):
    patch.object(click, 'launch')

    with runner.runner.isolated_filesystem():
        result = runner.run(feedback, exit_code=0)

    feedback_url = 'https://asyncy.click/feedback'
    click.launch.assert_called_with(feedback_url)
    assert feedback_url in result.stdout
