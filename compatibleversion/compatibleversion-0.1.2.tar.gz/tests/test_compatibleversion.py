# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""test_compatibleversion module."""
import packaging
import pytest
from compatibleversion import check_version


def test_problems():
    """Tests for expected exceptions."""
    with pytest.raises(ValueError):
        check_version('', '<1.0.0')

    with pytest.raises(ValueError):
        check_version('1.0.0', '')

    with pytest.raises(packaging.version.InvalidVersion):
        check_version('very bad version', '<1.0.0')

    with pytest.raises(packaging.version.InvalidVersion):
        check_version('very.bad.version', '<1.0.0')

    with pytest.raises(packaging.version.InvalidVersion):
        check_version('very.1.0', '<1.0.0')

    with pytest.raises(packaging.specifiers.InvalidSpecifier):
        check_version('1.0.0', 'very bad specifier')

    with pytest.raises(packaging.specifiers.InvalidSpecifier):
        check_version('0.0.0', '0.0.0')

    with pytest.raises(packaging.specifiers.InvalidSpecifier):
        check_version('0.0.0', '=0.0.0')

    with pytest.raises(packaging.specifiers.InvalidSpecifier):
        check_version('0.0.0', '!0.0.0')


def test_versions():
    """Tests for a variety of version types."""
    assert check_version('1.2.0', '==1.2.0')
    assert check_version('0.0.0', '==0.0.0')
    assert check_version('0.9', '==0.9')
    assert check_version('0.9.1', '==0.9.1')
    assert check_version('0.9.2', '==0.9.2')
    assert check_version('0.9.10', '==0.9.10')
    assert check_version('0.9.11', '==0.9.11')
    assert check_version('1.0', '==1.0')
    assert check_version('1.0.1', '==1.0.1')
    assert check_version('1.1', '==1.1')
    assert not check_version('2.0', '!=2.0')
    assert check_version('2.0.1', '==2.0.1')
    assert check_version('1.0a1', '==1.0a1')
    assert check_version('1.0a2', '==1.0a2')
    assert check_version('1.0b1', '==1.0b1')
    assert check_version('1.0rc1', '==1.0rc1')
    assert check_version('1.0.dev1', '==1.0.dev1')
    assert check_version('1.0.dev2', '==1.0.dev2')
    assert check_version('1.0.dev3', '==1.0.dev3')
    assert check_version('1.0.dev4', '==1.0.dev4')
    assert check_version('1.0b2.post345.dev456', '==1.0b2.post345.dev456')
    assert check_version('1.0b2.post345', '==1.0b2.post345')
    assert check_version('1.0rc1.dev456', '==1.0rc1.dev456')


def test_specifiers():
    """Tests for a variety of specifier types."""
    assert not check_version('1.0rc1.dev456', '==1.0.1')

    assert not check_version('1.0rc1.dev456', '< 1.2, > 1.3')   # no version
    assert not check_version('2.9.9', '< 1.2, > 1.3')           # can match
    assert not check_version('1.2.5', '< 1.2, > 1.3')

    assert check_version('1.3.0', '> 1.2, < 3.3')
    assert check_version('2.5', '> 1.2, < 3.3')
    assert not check_version('4.9.9', '> 1.2, < 3.3')
    assert not check_version('1.1.0.1', '> 1.2, < 3.3')

    assert check_version('1.0.0.0', '>= 1.0, != 1.3.4.*, < 2.0')
    assert check_version('1.9.9', '>= 1.0, != 1.3.4.*, < 2.0')
    assert not check_version('1.3.4.99', '>= 1.0, != 1.3.4.*, < 2.0')
    assert not check_version('2.0.0.0', '>= 1.0, != 1.3.4.*, < 2.0')

    assert check_version('1.4.5.9', '~= 1.4.5.0')
    assert not check_version('1.4.6', '~= 1.4.5.0')

    assert check_version('1.0rc1.dev456', '>= 1.*')
    assert check_version('1.999.1', '>= 1.*')

    assert check_version('2.3', '~= 2.2')
    assert not check_version('2.1', '~= 2.2')
    assert not check_version('3.0', '~= 2.2')

    assert check_version('2.3', '>= 2.2, == 2.*')
    assert not check_version('2.1', '>= 2.2, == 2.*')
    assert not check_version('3.0', '>= 2.2, == 2.*')

    # version 3.1 or later, but not version 4.0 or later.
    assert check_version('3.2', '~=3.1')
    assert not check_version('4.0', '~=3.1')

    # version 3.1.2 or later, but not version 3.2.0 or later.
    assert check_version('3.1.2.99', '~= 3.1.2')
    assert not check_version('3.2.0.0', '~= 3.1.2')

    # version 3.1a1 or later, but not version 4.0 or later.
    assert check_version('3.1a2', '~= 3.1a1')
    assert not check_version('3.2a3', '~= 3.1a1')
    assert not check_version('4.0a1', '~= 3.1a1')

    # specifically version 3.1 (or 3.1.0), excludes all pre-releases, post
    # releases, developmental releases and any 3.1.x maintenance releases.
    assert check_version('3.1', '== 3.1')
    assert check_version('3.1.0', '== 3.1')
    assert not check_version('3.1.1', '== 3.1')

    # any version that starts with 3.1. Equivalent to the ~=3.1.0 compatible
    # release clause.
    assert not check_version('1.0rc1.dev456', '== 3.1.*')
    assert check_version('3.1.99.9999', '== 3.1.*')
    assert not check_version('3.2.99.9999', '== 3.1.*')

    # version 3.1.0 or later, but not version 3.1.3 and not version 3.2.0 or
    # later.
    assert check_version('3.1.0', '~=3.1.0, != 3.1.3')
    assert check_version('3.1.3.99', '~=3.1.0, != 3.1.3')
    assert not check_version('3.2', '~=3.1.0, != 3.1.3')
