# encoding=utf8
from _pytest.mark import MarkDecorator, MarkInfo
from allure import MASTER_HELPER as ALLURE_HELPER
from ConfigParser import ConfigParser, NoSectionError
import re

from allure.structure import TestLabel

ALLURE_PREFIX_MARKER = 'allure_prefix'
TESTRAIL_PREFIX_MARKER = 'testrail'
CASE_URL = "{}/index.php?/cases/view/"
DEFAULT_TESTRAIL_CONFIG_FILE = "testrail.cfg"


def pytest_runtest_makereport(item, call):
    """Добавление префикса теста и ссылки на TestRail в allure."""
    if call.when == 'call' and ALLURE_HELPER._allurelistener:
        request = item._request
        prefixes = ""
        parameters = ""
        allure_prefix_marker = request.keywords.get(ALLURE_PREFIX_MARKER)
        if isinstance(allure_prefix_marker, (MarkDecorator, MarkInfo)):
            for prefix in allure_prefix_marker.kwargs.get('ids'):
                prefixes += "[{}]".format(prefix)
            prefixes += " "
        for key, value in sorted(request._arg2fixturedefs.iteritems()):
            if value and value[0].params:
                parameters = "{parameters}, {key}={value}".format(parameters=parameters,
                                                                  key=key,
                                                                  value=request.getfuncargvalue(key))
        parameters = re.sub('^,\s', '', parameters)
        method_name = re.search("(?<=\.)[^\[]*", str(ALLURE_HELPER._allurelistener.test.name)).group(0)
        test_name = "{prefixes}{method_name}({parameters})".format(prefixes=prefixes,
                                                                   method_name=method_name,
                                                                   parameters=parameters)
        ALLURE_HELPER._allurelistener.test.name = test_name

        testrail_prefix_marker = request.keywords.get(TESTRAIL_PREFIX_MARKER)
        if isinstance(testrail_prefix_marker, (MarkDecorator, MarkInfo)):
            try:
                cfg_file_path = request.config.getoption('--tr-config', DEFAULT_TESTRAIL_CONFIG_FILE)
                url = request.config.getoption('--tr-url', None)
                if not url:
                    configparser = ConfigParser()
                    configparser.read(cfg_file_path)
                    url = configparser.get('API', 'url')
                case_url = CASE_URL.format(url)
                for testrail_id in testrail_prefix_marker.kwargs.get('ids'):
                    link = case_url + re.sub('\D', '', str(testrail_id))
                    ALLURE_HELPER._allurelistener.test.labels.append(TestLabel(name='testId', value=link))
            except NoSectionError as e:
                print("Can't add testrail link. Make sure that you have testrail.cfg in the "
                      "project root or set testrail.cfg path via --tr-config", e)
