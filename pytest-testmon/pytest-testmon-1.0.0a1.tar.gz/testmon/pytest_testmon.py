
import os
from collections import defaultdict

import pytest
from _pytest.python import Function

from testmon.testmon_core import Testmon, eval_environment, TestmonData, home_file
from _pytest import runner


def serialize_report(rep):
    import py
    d = rep.__dict__.copy()
    if hasattr(rep.longrepr, 'toterminal'):
        d['longrepr'] = str(rep.longrepr)
    else:
        d['longrepr'] = rep.longrepr
    for name in d:
        if isinstance(d[name], py.path.local):
            d[name] = str(d[name])
        elif name == "result":
            d[name] = None  
    return d


def pytest_addoption(parser):
    group = parser.getgroup('testmon')

    group.addoption(
        '--testmon',
        action='store_true',
        dest='testmon',
        help="Select only tests affected by recent changes.",
    )

    group.addoption(
        '--testmon-tlf',
        action='store_true',
        dest='tlf',
        help="Re-execute last failures regardless of source change status",
    )

    group.addoption(
        '--testmon-off',
        action='store_true',
        dest='testmon_off',
        help="Turn off (even if activated from config by default)"
    )


    group.addoption(
        '--testmon-readonly',
        action='store_true',
        dest='testmon_readonly',
        help="Don't track, just deselect based on existing .testmondata"
    )

    group.addoption(
        '--testmon-project-directory',
        action='append',
        dest='project_directory',
        help="Top level directory of project",
        default=None
    )

    parser.addini("environment_expression", "environment expression",
                  default='')


def testmon_options(config):
    result = []
    for label in ['testmon', 'testmon_off', 'testmon_readonly',
                  ]:
        if config.getoption(label):
            result.append(label.replace('testmon_', ''))
    return result


def init_testmon_data(config, read_source=True):
    if not hasattr(config, 'testmon_data'):
        environment = eval_environment(config.getini('environment_expression'))
        config.project_dirs = config.getoption('project_directory') or [config.rootdir.strpath]
        testmon_data = TestmonData(config.project_dirs[0],
                                   environment=environment)
        testmon_data.read_data()
        if read_source:
            testmon_data.determine_stable()
        config.testmon_data = testmon_data


def is_active(config):
    return (config.getoption('testmon') or config.getoption('testmon_readonly')) and not (
        config.getoption('testmon_off'))


def pytest_configure(config):
    if is_active(config):
        config.option.continue_on_collection_errors = True
        init_testmon_data(config)
        config.pluginmanager.register(TestmonSelect(config, config.testmon_data),
                                      "TestmonSelect")
        config.pluginmanager.register(TestmonCollect(Testmon(config.project_dirs,
                                                             testmon_labels=testmon_options(config)),
                                                     config.testmon_data,
                                                     config.getoption('testmon_readonly')),
                                      "TestmonCollect")


def pytest_unconfigure(config):
    if hasattr(config, 'testmon_data'):
        config.testmon_data.close_connection()


def sort_items_by_duration(items, reports):
    durations = defaultdict(lambda: {'node_count': 0, 'duration': 0})
    for item in items:
        if item.nodeid in reports:
            item.duration = sum([report['duration'] for report in reports[item.nodeid].values()])
        else:
            item.duration = 0
        item.module_name = item.location[0]
        item_hierarchy = item.location[2].split('.')
        item.node_name = item_hierarchy[-1]
        item.class_name = item_hierarchy[0]

        durations[item.class_name]['node_count'] += 1
        durations[item.class_name]['duration'] += item.duration
        durations[item.module_name]['node_count'] += 1
        durations[item.module_name]['duration'] += item.duration

    for key, stats in durations.items():
        durations[key]['avg_duration'] = stats['duration'] / stats['node_count']

    items.sort(key=lambda item: item.duration)
    items.sort(key=lambda item: durations[item.class_name]['avg_duration'])
    items.sort(key=lambda item: durations[item.module_name]['avg_duration'])


class TestmonCollect(object):
    def __init__(self, testmon, testmon_data, read_only=False):
        self.testmon_data = testmon_data
        self.testmon = testmon

        self.reports = defaultdict(lambda: {})
        self.read_only = read_only

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_protocol(self, item, nextitem):
        if self.read_only or not isinstance(item, Function):
            yield
        else:
            self.testmon.start()
            result = yield
            if result.excinfo and issubclass(result.excinfo[0], BaseException):
                self.testmon.stop()
            else:
                self.testmon.stop_and_save(self.testmon_data, item.config.rootdir.strpath, item.nodeid,
                                           self.reports[item.nodeid])

    def pytest_runtest_logreport(self, report):
        assert report.when not in self.reports,            "{} {} {}".format(report.nodeid, report.when, self.reports)
        self.reports[report.nodeid][report.when] = serialize_report(report)

    def pytest_sessionfinish(self, session):
        self.testmon.close()


def did_fail(reports):
    return bool([True for report in reports.values() if report.get('outcome') == u'failed'])


def get_failing(all_nodes):
    failing_files, failing_nodes = set(), {}
    for nodeid, result in all_nodes.items():
        if did_fail(all_nodes[nodeid]):
            failing_files.add(home_file(nodeid))
            failing_nodes[nodeid] = result
    return failing_files, failing_nodes


class TestmonSelect():

    def __init__(self, config, testmon_data):
        self.testmon_data = testmon_data
        self.config = config

        self.deselected_files = testmon_data.stable_files
        self.deselected_nodes = testmon_data.stable_nodeids

        failing_files, failing_nodes = get_failing(testmon_data.all_nodes)

        if self.config.getoption('tlf'):
            self.deselected_files -= failing_files
            self.deselected_nodes -= failing_nodes.keys()

        self.failing_nodes = failing_nodes

    def report_from_db(self, nodeid):
        node_reports = self.failing_nodes.get(nodeid, {})
        if node_reports:
            for phase in ('setup', 'call', 'teardown'):
                if phase in node_reports:
                    test_report = runner.TestReport(**node_reports[phase])
                    self.config.hook.pytest_runtest_logreport(report=test_report)

    def pytest_report_header(self, config):
        changed_files = ",".join(self.testmon_data.unstable_files)
        if changed_files == '' or len(changed_files) > 100:
            changed_files = len(self.testmon_data.unstable_files)

        active_message = "testmon={}, ".format(config.getoption('testmon'))
        if changed_files == 0 and len(self.deselected_files) == 0:
            active_message += "new testmon DB"
        else:
            active_message += "changed files: {}, skipping collection of {} files".format(
                changed_files, len(self.deselected_files))

        if self.testmon_data.environment:
            return active_message + ", environment: {}".format(self.testmon_data.environment)
        else:
            return active_message + "."

    def pytest_ignore_collect(self, path, config):
        strpath = os.path.relpath(path.strpath, config.rootdir.strpath)
        if strpath in self.deselected_files:
            return True

    @pytest.mark.hookwrapper
    def pytest_collection_modifyitems(self, session, config, items):
        self.testmon_data.sync_db_fs_nodes(retain={item.nodeid for item in items})

        yield

        for item in items:
            assert item.nodeid not in self.deselected_files, (item.nodeid, self.deselected_files)

        selected = []
        for item in items:
            if item.nodeid not in self.deselected_nodes:
                selected.append(item)
        items[:] = selected

        if self.testmon_data.all_nodes:
            sort_items_by_duration(items, self.testmon_data.all_nodes)

        session.config.hook.pytest_deselected(
            items=([FakeItemFromTestmon(session.config)] *
                   len(self.deselected_nodes)))

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtestloop(self, session):
        yield
        for nodeid in self.deselected_nodes:
            self.report_from_db(nodeid)


class FakeItemFromTestmon(object):
    def __init__(self, config):
        self.config = config
