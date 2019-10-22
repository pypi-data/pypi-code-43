import copy
import pprint
import sys
from test_junkie.debugger import LogJunkie
from tests.junkie_suites.SkipSuites import SkipTests

LogJunkie.enable_logging(10)
# from tests.cli.CliTestSuite import AuthApiSuite
#
# sys.path.insert(1, "E:/Development/test_junkie/")
# # from tests.junkie_suites.IgnoreSuite import IgnoreSuiteWrongDatatype
# from playground.suiteB import ShoppingCartSuite
from playground.suiteC import AuthApiSuite
from playground.suiteD import NewProductsSuite
# from test_junkie.objects import Limiter
#
# sys.path.insert(1, __file__.split("playground")[0])
# from test_junkie.reporter.html_reporter import Reporter
#
#
# # from playground.suiteA import LoginSuite
from test_junkie.runner import Runner
# Limiter.ACTIVE = False
# Limiter.SUITE_THROTTLING = 10
# Limiter.TEST_THROTTLING = 1

runner = Runner([AuthApiSuite, NewProductsSuite])
aggregator = runner.run(features=["Store"])

# runner = Runner([NewProductsSuite, AuthApiSuite], tests=[NewProductsSuite.edit_product])
#
# aggregator = runner.run()

# pprint.pprint(aggregator.get_report_by_suite())
# suite_objects = runner.get_executed_suites()

# for suite in suite_objects:
#     print("=============")
#     new_suite = copy.deepcopy(suite)
#     print(new_suite.get_class_name())
#     tests = new_suite.get_test_objects()
#     print(tests)
#     print(new_suite.metrics)
#     print(new_suite.metrics.get_metrics())
#     print(new_suite.get_data_by_tags())
#     for test in tests:
#         new_test = copy.deepcopy(test)
#         pprint.pprint(new_test.metrics.get_metrics())
#
# # tags = aggregator.get_report_by_tags()
# # features = aggregator.get_report_by_features()
# # totals = aggregator.get_basic_report()
# # owners = aggregator.get_report_by_owner()
# # reporter = Reporter("E:\Development\\test_junkie\\test_junkie\.resources", features, totals)
# # pprint.pprint(reporter.get_dataset_per_feature())
# # pprint.pprint(reporter.get_absolute_results())
# # pprint.pprint(aggregator.get_report_by_owner())
