import datetime

import requests

from ioflow.performance_reporter.metric import Metric

task_status_registry = {}


def get_performance_metrics_class(config):
    return task_status_registry[config.get('metrics_report_scheme', 'local')]


def registry_performance_metrics_class(schema, class_):
    task_status_registry[schema] = class_


class BasePerformanceMetrics(object):
    epoch = datetime.datetime.utcfromtimestamp(0)

    def __init__(self, config):
        self.config = config

    def send_metrics(self, metrics, step=None):
        timestamp = datetime.datetime.now()
        for k, v in metrics.items():
            self.log_metric(k, v, timestamp=timestamp, step=step)

    def log_metric(self, key, value, timestamp=None, step=None):
        """ learned from MLflow log_metrics"""
        timestamp = timestamp if timestamp is not None else datetime.datetime.now()
        step = step if step is not None else 0

        metric = Metric(key, value, timestamp, step)
        self.post_metric(metric)

    def post_metric(self, metric):
        raise NotImplementedError


class LocalPerformanceMetrics(BasePerformanceMetrics):
    def post_metric(self, metric):
        print('[{}]{}: {} => {}'.format(
            self.config['task_id'],
            metric.timestamp, metric.key, metric.value))


registry_performance_metrics_class('local', LocalPerformanceMetrics)


class HttpPerformanceMetrics(BasePerformanceMetrics):
    def post_metric(self, metric):
        data = {
            'id': self.config['task_id'],
            'key': metric.key,
            'value': metric.value,
            'step': metric.step,
            'timestamp': (metric.timestamp - self.epoch) / datetime.timedelta(microseconds=1)
        }

        r = requests.post(self.config['metrics_report_url'], json=data)
        assert r.ok


registry_performance_metrics_class('http', HttpPerformanceMetrics)


def get_performance_metrics(config):
    pm_class = get_performance_metrics_class(config)
    pm = pm_class(config)
    return pm
