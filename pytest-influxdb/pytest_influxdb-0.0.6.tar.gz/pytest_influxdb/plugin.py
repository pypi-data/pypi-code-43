import pytest

from pytest_influxdb.data_manager import DataManager
from pytest_influxdb.influxdb_components import Influxdb_Components

data_manager = DataManager()
test_result_dto_session_dict = dict()
session_dict = {'test_result_dto_session_dict': test_result_dto_session_dict}
db_measurement_name_for_test = 'test_result'


@pytest.mark.tryfirst
def pytest_runtest_makereport(item, call, __multicall__):
    if item.config.option.pytest_influxdb:
        report = __multicall__.execute()
        setattr(item, "rep_" + report.when, report)
        return report


@pytest.fixture(scope='function', autouse=True)
def test_result(request, run, pytestconfig, get_influxdb, project, version, influxdb_values, db_host, db_port, db_name,
                db_user, db_password):
    test_name = request.node.nodeid
    test_result_dto = data_manager.get_test_result_dto(test_name, session_dict)

    if pytestconfig.getoption('--pytest-influxdb'):
        def send_test_data_to_db():
            # Generating test data
            data_manager.generate_test_result_data(test_result_dto, project, version, run,
                                                   data_manager.get_report(request))
            data_manager.collect_user_properties(test_result_dto, request)
            data_manager.collect_custom_values(test_result_dto, influxdb_values)

            send_data_to_db(test_result_dto, get_influxdb)

            data_manager.save_db_data_in_properties(request, db_host, db_port, db_user, db_password, db_name,
                                                    influxdb_values)

        request.addfinalizer(send_test_data_to_db)


def pytest_exception_interact(node, call, report):
    if report.failed:
        test_name = node.nodeid
        test_result_dto = session_dict.get('test_result_dto_session_dict').get(test_name)
        if test_result_dto:
            stack_trace = node.repr_failure(call.excinfo)
            stack_trace = str(stack_trace).replace('"', "'")
            test_result_dto.set_exception(stack_trace)


def pytest_configure(config):
    config.getini("influxdb_run_id")
    config.getini("influxdb_project")
    config.getini("influxdb_version")
    config.getini("influxdb_host")
    config.getini("influxdb_port")
    config.getini("influxdb_user")
    config.getini("influxdb_password")
    config.getini("influxdb_name")
    config.getini("influxdb_project")
    config.getini("influxdb_values")


def pytest_addoption(parser):
    group = parser.getgroup('pytest-influxdb')
    group.addoption("--pytest-influxdb", action="store_true",
                    help="pytest-influxdb: enable influxdb data collection")
    parser.addoption(
        "--influxdb_run_id", action="store", default=None, help="my option: run_id"
    )
    parser.addoption(
        "--influxdb_host", action="store", default=None, help="my option: db_host"
    )
    parser.addoption(
        "--influxdb_port", action="store", default=None, help="my option: db_port"
    )
    parser.addoption(
        "--influxdb_user", action="store", default=None, help="my option: db_username"
    )
    parser.addoption(
        "--influxdb_password", action="store", default=None, help="my option: db_password"
    )
    parser.addoption(
        "--influxdb_name", action="store", default=None, help="my option: db_name"
    )
    parser.addoption(
        "--influxdb_project", action="store", default=None, help="my option: project name"
    )
    parser.addoption(
        "--influxdb_version", action="store", default=None, help="my option: version"
    )
    parser.addoption(
        "--influxdb_values", action="store", default=None, help="my option: version"
    )
    parser.addini(
        'influxdb_run_id',
        help='my option: run_id')
    parser.addini(
        'influxdb_project',
        help='my option: project')
    parser.addini(
        'influxdb_version',
        help='my option: version')
    parser.addini(
        'influxdb_host',
        help='my option: db_host')
    parser.addini(
        'influxdb_port',
        help='my option: db_port')
    parser.addini(
        'influxdb_name',
        help='my option: db_name')
    parser.addini(
        'influxdb_user',
        help='my option: db_user')
    parser.addini(
        'influxdb_password',
        help='my option: db_password')
    parser.addini(
        'influxdb_values',
        help='my option: db_values')


@pytest.fixture
def run(request, pytestconfig):
    run_id = request.config.getoption("--influxdb_run_id")
    if not run_id:
        run_id = pytestconfig.getini('influxdb_run_id')
    return run_id


@pytest.fixture
def db_host(request, pytestconfig):
    db_host = request.config.getoption("--influxdb_host")
    if not db_host:
        db_host = pytestconfig.getini("influxdb_host")
    return db_host


@pytest.fixture
def db_port(request, pytestconfig):
    db_port = request.config.getoption("--influxdb_port")
    if not db_port:
        db_port = pytestconfig.getini("influxdb_port")
    if not db_port:
        db_port = 8086
    return db_port


@pytest.fixture
def db_user(request, pytestconfig):
    db_user = request.config.getoption("--influxdb_user")
    if not db_user:
        db_user = pytestconfig.getini("influxdb_user")
    return db_user


@pytest.fixture
def db_password(request, pytestconfig):
    db_password = request.config.getoption("--influxdb_password")
    if not db_password:
        db_password = pytestconfig.getini("influxdb_password")
    return db_password


@pytest.fixture
def db_name(request, pytestconfig):
    db_name = request.config.getoption("--influxdb_name")
    if not db_name:
        db_name = pytestconfig.getini("influxdb_name")
    return db_name


@pytest.fixture
def project(request, pytestconfig):
    project_name = request.config.getoption("--influxdb_project")
    if not project_name:
        project_name = pytestconfig.getini('influxdb_project')
    return project_name


@pytest.fixture
def version(request, pytestconfig):
    version = request.config.getoption("--influxdb_version")
    if not version:
        version = pytestconfig.getini('influxdb_version')
    return version


@pytest.fixture
def influxdb_values(request, pytestconfig):
    values = request.config.getoption("--influxdb_values")
    if not values:
        values = custom_values = pytestconfig.getini("influxdb_values")
    return values


@pytest.fixture()
def get_influxdb(pytestconfig, db_host, db_port, db_name, db_user, db_password):
    if pytestconfig.getoption('--pytest-influxdb'):
        influxdb_components = Influxdb_Components(db_host, db_port, db_user, db_password, db_name)
        return influxdb_components


# Fixture for generating a screenshot from conftest
@pytest.fixture()
def screenshot_url(request, pytestconfig):
    if pytestconfig.getoption('--pytest-influxdb'):
        current_test = request.node.nodeid

        def _foo(*args, **kwargs):
            test_result_dto = session_dict.get('test_result_dto_session_dict').get(current_test)
            if pytestconfig.getoption('--pytest-influxdb'):
                test_result_dto.set_screenshot(args[0])
            return (args, kwargs)

        return _foo


@pytest.hookimpl(hookwrapper=True)
def pytest_terminal_summary(config, terminalreporter):
    yield
    influxdb_test_host = None
    influxdb_test_port = None
    influxdb_test_user = None
    influxdb_test_password = None
    influxdb_test_name = None
    influxdb_test_values = None


def send_data_to_db(test_result_dto, influxdb):
    ##Sending the test results to influxdb
    test_json = test_result_dto.get_test_json(db_measurement_name_for_test)
    data_manager.get_test_influxdb_components(influxdb, session_dict).write_points(test_json)
