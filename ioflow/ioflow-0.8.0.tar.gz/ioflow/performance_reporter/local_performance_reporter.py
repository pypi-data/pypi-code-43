from ioflow.performance_reporter.performance_reporter_base import \
    PerformanceReporterBase


class LocalPerformanceReporter(PerformanceReporterBase):
    def log_performance(self, key, value):
        print("{} => {}".format(key, value))
