import pytest

from azureml.studio.common.version import Version


def test_version_equal():
    assert Version.parse('1.0.0') == Version(1, 0, 0)
    assert not Version.parse('1.0.0') == Version(0, 0, 1)


def test_version_str_check():
    assert str(Version.parse('1.0.0')) == '1.0.0'


def test_version_check():
    with pytest.raises(ValueError, match="Input version cannot be empty."):
        assert Version.parse(None)
    with pytest.raises(ValueError, match="Input version cannot be empty."):
        assert Version.parse('')
    with pytest.raises(TypeError, match="Expected version to be a string but got a <class 'int'>."):
        assert Version.parse(1)
    with pytest.raises(ValueError, match="Version string '1.0' must be in 3 digital segments."):
        assert Version.parse('1.0')
    with pytest.raises(ValueError, match="Version string '1.0.0.1' must be in 3 digital segments."):
        assert Version.parse('1.0.0.1')
    with pytest.raises(ValueError, match="Version string '1.0.a' must contains only digits in each segment."):
        assert Version.parse('1.0.a')
    with pytest.raises(ValueError, match="Version string '1.0.+10' must contains only digits in each segment."):
        assert Version.parse('1.0.+10')

    assert Version.parse('1.0.0') == Version(1, 0, 0)
    assert Version.parse('000.010.100') == Version(0, 10, 100)
    assert Version.parse('0.0.50') == Version(0, 0, 50)


def test_metaphysical_check():
    with pytest.raises(ValueError, match="Bad version '0.0.4': Should not contain '4'."):
        Version.parse('0.0.4')
    with pytest.raises(ValueError, match="Bad version '0.0.14': Should not contain '4'."):
        Version.parse('0.0.14')
    with pytest.raises(ValueError, match="Bad version '0.0.40': Should not contain '4'."):
        Version.parse('0.0.40')
    with pytest.raises(ValueError, match="Bad version '1.4.0': Should not contain '4'."):
        Version.parse('1.4.0')
    with pytest.raises(ValueError, match="Bad version '1.13.0': Should not contain '13'."):
        Version.parse('1.13.0')
    with pytest.raises(ValueError, match="Bad version '0.0.13': Should not contain '13'."):
        Version.parse('0.0.13')
    with pytest.raises(ValueError, match="Bad version '13.2.1': Should not contain '13'."):
        Version.parse('13.2.1')

    Version.parse('1.130.0')
