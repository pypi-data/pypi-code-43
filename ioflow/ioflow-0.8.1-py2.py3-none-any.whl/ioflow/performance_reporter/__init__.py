from ioflow.performance_reporter.db_performance_reporter import \
    DbPerformanceReporter
from ioflow.performance_reporter.performance_reporter_base import \
    PerformanceReporterBase
from ioflow.performance_reporter.local_performance_reporter import \
    LocalPerformanceReporter

performance_reporter_registry = {}


def get_performance_reporter_class(config):
    return performance_reporter_registry[config.get('performance_reporter_schema', 'local')]


def get_performance_reporter(config) -> PerformanceReporterBase:
    task_status_class = get_performance_reporter_class(config)
    return task_status_class(config)


def registry_performance_reporter_class(schema, class_):
    performance_reporter_registry[schema] = class_


registry_performance_reporter_class('http', DbPerformanceReporter)

registry_performance_reporter_class('local', LocalPerformanceReporter)
