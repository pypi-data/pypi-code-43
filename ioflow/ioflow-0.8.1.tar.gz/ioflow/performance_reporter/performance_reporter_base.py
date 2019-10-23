class PerformanceReporterBase(object):
    def __init__(self, config):
        self.config = config

    def send_performances(self, metrics):
        for k, v in metrics.items():
            self.log_performance(k, v)

    def log_performance(self, key, value):
        raise NotImplementedError
