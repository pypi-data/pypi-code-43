from publishing_boy.plugins import register_plugin, PLUGINS
import pytest


@pytest.mark.skip
def test_register_plugin():

    PLUGINS.clear()

    @register_plugin
    def func(content):
        return 'test', content

    assert len(PLUGINS) == 1
    assert PLUGINS.pop()('func') == (
        'test',
        'func',
    )
