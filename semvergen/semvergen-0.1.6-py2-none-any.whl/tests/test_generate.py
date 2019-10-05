from semvergen.generate import version, _get_latest_tag

try:
    from unittest import mock
except ImportError:
    import mock


@mock.patch('semvergen.generate._get_latest_tag')
def test_version(get_latest_mock):
    test_hash = 'fds880'
    get_latest_mock.return_value = (test_hash, None)

    stdout, stderr = version()

    assert stdout == test_hash
    assert stderr is None


class MockPopen(object):
    def communicate(self):
        return (b'di321ocij\n', None)


@mock.patch('subprocess.Popen')
def test_get_latest_tag(get_latest_mock):
    get_latest_mock.return_value = MockPopen()

    assert _get_latest_tag() == 'di321ocij'
