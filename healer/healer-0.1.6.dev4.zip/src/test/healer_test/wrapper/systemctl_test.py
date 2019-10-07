
from healer.wrapper.systemctl import *


def test_version_number():
    print()
    sysctl = SystemCtl()
    version = sysctl.property_VersionNumber()
    print(f"version={version}")


def test_status_present():
    print()
    sysctl = SystemCtl()
    service = 'systemd-journald.service'
    result = sysctl.response(service)
    print(result)
    assert sysctl.has_unit(service)
    assert sysctl.has_active(service)
    assert sysctl.has_enabled(service)


def test_status_missing():
    print()
    sysctl = SystemCtl()
    service = 'systemd-answer-42.service'
    result = sysctl.response(service)
    print(result)
    assert not sysctl.has_unit(service)
    assert not sysctl.has_active(service)
    assert not sysctl.has_enabled(service)


def test_parse_ExecInfo():
    print()
    value = """{ path=/usr/bin/systemd-nspawn ; argv[]=/usr/bin/systemd-nspawn --machine=alpa-base --directory=/var/lib/machines/alpa-base --kill-signal=SIGUSR1 --setenv=TEST_1=solid-value --setenv=TEST_2=value with space --setenv=TEST_3=value : with : colon --setenv=TEST_4=value " with " double quote --quiet --keep-unit --register=yes --network-macvlan=wire0 /sbin/init ; ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; library=(null) ; response=0/0 }"""
    exec_info = parse_ExecInfo(value)
    print(exec_info)


def test_show_exec_info():
    print()
    sysctl = SystemCtl()
    service = 'systemd-journald.service'
    exec_start = sysctl.show_exec_info('ExecStart', service)
    print(exec_start)
    has_stop = sysctl.has_property('ExecStop', service)
    print(has_stop)
    assert has_stop == False
