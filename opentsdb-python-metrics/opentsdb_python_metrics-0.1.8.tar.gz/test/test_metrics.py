from nose.tools import assert_equal
import opentsdb_python_metrics.metric_wrappers
from opentsdb_python_metrics.metric_wrappers import (SendMetricMixin, metric_timer, metric_wrapper,
                                                     metric_timer_with_tags, metric_wrapper_with_tags)
import time


class Metric(object):
    '''
    Class to contain a metrics representation
    '''
    def __init__(self, metric_name, value, asynchronous=True, **kwargs):
        self.metric_name = metric_name
        self.value = value
        self.kwargs = kwargs
        self.asynchronous = asynchronous

    def __eq__(self, other):
        return self.metric_name == other.metric_name and \
               self.asynchronous == other.asynchronous and \
               self.kwargs == other.kwargs


# Global variable to store the last saved metric (instead of sending it to opentsdb)
last_saved_metric = Metric(None, None)


# method to fake out sending metric to tsdb and instead record it so we can check it out and verify parameters are good
def fake_send_tsdb_metric(metric_name, value, **kwargs):
    global last_saved_metric
    last_saved_metric = Metric(metric_name, value, **kwargs)


def fill_in_str(text, value):
    return "you called this function with text = {} and value = {}".format(text, value)


def class_path_tag(module_name, class_name, method_name):
    return '{}.{}.{}'.format(module_name, class_name, method_name)


@metric_timer("test_simple_function")
def simple_function(text, value):
    return fill_in_str(text, value)


class SimpleClass(SendMetricMixin):
    '''
    Class of simple functions to test different aspects of the library
    '''
    def __init__(self):
        pass

    @metric_timer("test_simple_method")
    def simple_method(self, text, value):
        return fill_in_str(text, value)

    @metric_timer("test_synchronous_timer", asynchronous=False)
    def simple_method_synchronous(self, text, value):
        return fill_in_str(text, value)

    @metric_timer_with_tags(metric_name="test_simple_method_with_tags", tag1=324, tag2='hodor')
    def simple_method_with_tags(self, text, value):
        return fill_in_str(text, value)

    @metric_timer_with_tags(
        metric_name="test_simple_method_with_tags_with_retval",
        retval_functions={'value': (lambda x: x)}, tag1=324, tag2='hodor'
    )
    def simple_method_with_tags_and_retval(self, text, value):
        return value

    @metric_wrapper_with_tags(metric_name="test_simple_method_with_tags_no_retval", tag1=324, tag2='hodor')
    def simple_method_with_tags_no_retval(self, text, value):
        return fill_in_str(text, value)

    @metric_timer("test_method_with_exception", value=lambda x: x)
    def method_with_exception(self, text, value):
        raise RuntimeError("error")
        return value

    @metric_wrapper("test_method_with_exception2", value=lambda x: x)
    def method_with_exception2(self, text, value):
        raise RuntimeError("error")
        return value

    @metric_timer("test_method_rate", rate=lambda x: x)
    def simple_rate_method(self, value):
        return value

    @metric_timer("test_method_frequency", frequency=lambda x: x)
    def simple_frequency_method(self, value):
        time.sleep(1)
        return value


class TestSendingMetrics(object):
    def setup(self):
        self.simpleClass = SimpleClass()
        opentsdb_python_metrics.metric_wrappers.send_tsdb_metric = fake_send_tsdb_metric

    def test_plain_function_metric_timer(self):
        retval = simple_function("test_plain_metric_timer", 1)
        assert_equal(retval, fill_in_str("test_plain_metric_timer", 1))

        comparison_metric = Metric(
            "test_simple_function.runtime",
            1,
            class_path=class_path_tag(
                simple_function.__module__,
                simple_function.__name__,
                simple_function.__name__)
            )

        assert_equal(comparison_metric, last_saved_metric)

    def test_plain_method_metric_timer(self):
        retval = self.simpleClass.simple_method("test_plain_metric_timer", 1)
        assert_equal(retval, fill_in_str("test_plain_metric_timer", 1))

        comparison_metric = Metric("test_simple_method.runtime", 1,
                                   class_path=class_path_tag(self.simpleClass.simple_method.__module__,
                                                             self.simpleClass.__class__.__name__,
                                                             self.simpleClass.simple_method.__name__))

        assert_equal(comparison_metric, last_saved_metric)

    def test_rate_method_metric_timer(self):
        retval = self.simpleClass.simple_rate_method(1)
        assert_equal(retval, 1)

        comparison_metric = Metric("test_method_rate.rate", 1,
                                   class_path=class_path_tag(self.simpleClass.simple_rate_method.__module__,
                                                             self.simpleClass.__class__.__name__,
                                                             self.simpleClass.simple_rate_method.__name__))

        assert_equal(comparison_metric, last_saved_metric)

    def test_zero_rate_method_metric_timer(self):
        retval = self.simpleClass.simple_rate_method(0)
        assert_equal(retval, 0)

        comparison_metric = Metric("test_method_rate.rate", 1,
                                   class_path=class_path_tag(self.simpleClass.simple_rate_method.__module__,
                                                             self.simpleClass.__class__.__name__,
                                                             self.simpleClass.simple_rate_method.__name__))

        assert_equal(comparison_metric, last_saved_metric)
        assert_equal(last_saved_metric.value, 0)

    def test_frequency_method_metric_timer(self):
        retval = self.simpleClass.simple_frequency_method(1)
        assert_equal(retval, 1)

        comparison_metric = Metric("test_method_frequency.frequency", 1,
                                   class_path=class_path_tag(self.simpleClass.simple_frequency_method.__module__,
                                                             self.simpleClass.__class__.__name__,
                                                             self.simpleClass.simple_frequency_method.__name__))

        assert_equal(comparison_metric, last_saved_metric)

    def test_zero_frequency_method_metric_timer(self):
        retval = self.simpleClass.simple_frequency_method(0)
        assert_equal(retval, 0)

        comparison_metric = Metric("test_method_frequency.frequency", 0,
                                   class_path=class_path_tag(self.simpleClass.simple_frequency_method.__module__,
                                                             self.simpleClass.__class__.__name__,
                                                             self.simpleClass.simple_frequency_method.__name__))

        assert_equal(comparison_metric, last_saved_metric)
        assert_equal(last_saved_metric.value, 0)

    def test_exception_still_log_runtime(self):
        try:
            retval = self.simpleClass.method_with_exception("test_method_with_exception", 1)
        except Exception:
            pass

        assert 'retval' not in locals()

        comparison_metric = Metric("test_method_with_exception.runtime", 1,
                                   class_path=class_path_tag(self.simpleClass.method_with_exception.__module__,
                                                             self.simpleClass.__class__.__name__,
                                                             self.simpleClass.method_with_exception.__name__))

        assert_equal(comparison_metric, last_saved_metric)

    def test_exception_wont_log_value(self):
        # clear out last saved metric
        global last_saved_metric
        last_saved_metric = Metric(None, None)
        try:
            retval = self.simpleClass.method_with_exception2("test_method_with_exception2", 1)
        except Exception:
            pass

        assert 'retval' not in locals()

        comparison_metric = Metric(None, None)

        assert_equal(comparison_metric, last_saved_metric)

    def test_saving_metric_tags_no_retval(self):
        # clear out last saved metric
        global last_saved_metric
        last_saved_metric = Metric(None, None)

        retval = self.simpleClass.simple_method_with_tags("test_saving_metric_tags_no_retval", 1)
        assert_equal(retval, fill_in_str("test_saving_metric_tags_no_retval", 1))

        comparison_metric = Metric("test_simple_method_with_tags.runtime", 1,
                                   class_path=class_path_tag(self.simpleClass.simple_method_with_tags.__module__,
                                                             self.simpleClass.__class__.__name__,
                                                             self.simpleClass.simple_method_with_tags.__name__),
                                   tag1=324, tag2='hodor')

        assert_equal(comparison_metric, last_saved_metric)

    def test_saving_metric_tags_and_retval(self):
        # clear out last saved metric
        global last_saved_metric
        last_saved_metric = Metric(None, None)

        retval = self.simpleClass.simple_method_with_tags_and_retval("test_saving_metric_tags_and_retval", 1)
        assert_equal(retval, 1)

        comparison_metric = Metric(
            "test_simple_method_with_tags_with_retval.value",
            1,
            class_path=class_path_tag(
                self.simpleClass.simple_method_with_tags_and_retval.__module__,
                self.simpleClass.__class__.__name__,
                self.simpleClass.simple_method_with_tags_and_retval.__name__
            ),
            tag1=324,
            tag2='hodor'
        )

        assert_equal(comparison_metric, last_saved_metric)

    def test_saving_metric_tags_no_retval_doesnt_fill_in_last_saved(self):
        # clear out last saved metric
        global last_saved_metric
        last_saved_metric = Metric(None, None)

        retval = self.simpleClass.simple_method_with_tags_no_retval("test_saving_metric_tags_no_retval", 1)

        assert_equal(retval, fill_in_str("test_saving_metric_tags_no_retval", 1))

        assert_equal(Metric(None, None), last_saved_metric)

    def test_saving_synchronous_metric(self):
        retval = self.simpleClass.simple_method_synchronous("test_synchronous_timer", 1)
        assert_equal(retval, fill_in_str("test_synchronous_timer", 1))

        comparison_metric = Metric("test_synchronous_timer.runtime", 1, asynchronous=False,
                                   class_path=class_path_tag(self.simpleClass.simple_method_synchronous.__module__,
                                                             self.simpleClass.__class__.__name__,
                                                             self.simpleClass.simple_method_synchronous.__name__))

        assert_equal(comparison_metric, last_saved_metric)
