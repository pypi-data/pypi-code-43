from functools import wraps
import inspect
import numbers
import socket
from os import getenv
from datetime import datetime

from opentsdb_http_client import http_client

import logging
from requests.exceptions import ConnectionError

project_name = None
global_tags = None
# Environment variable for test mode - defaults to False. Set to True
test_mode = getenv('OPENTSDB_PYTHON_METRICS_TEST_MODE', False)
# Environment variables for opentsdb host to send metrics to.
opentsdb_hostname = getenv('OPENTSDB_HOSTNAME', 'fill_me_in.com')

hostname = socket.gethostname()
try:
    if not test_mode:
        tsdb_client = http_client.OpenTSDBClient(opentsdb_hostname, qsize=1000, host_tag=True, mps=100, check_host=True)
except ConnectionError as e:
    logging.error(repr(e))

'''
    This class mixin is used to provide a convenience function for sending metrics from within a class method. It
    automatically adds tags for class_name, method_name and module_name to the metric being sent
'''
class SendMetricMixin():
    def send_metric(self, metric_name, value, asynchronous=True, **kwargs):
        class_path = '{}.{}.{}'.format(self.__class__.__module__, self.__class__.__name__, inspect.stack()[1][3])
        send_tsdb_metric(metric_name, value, asynchronous=asynchronous, class_path=class_path, **kwargs)


def send_tsdb_metric(metric_name, value, asynchronous=True, **kwargs):
    if test_mode:
        return
    full_metric_name = metric_name
    if project_name:
        full_metric_name = '{}.{}'.format(project_name, full_metric_name)
    if global_tags and isinstance(global_tags, dict):
        kwargs.update(global_tags)
    try:
        tsdb_client.put(full_metric_name, value, asynchronous=asynchronous, host=hostname, **kwargs)
    except (ConnectionError, NameError) as er:
        logging.error(repr(er))


def metric_timer(metric_name=None, asynchronous=True, **retval_functions):
    return metric_timer_with_tags(metric_name=metric_name, retval_functions=retval_functions, asynchronous=asynchronous)


def metric_wrapper(metric_name=None, asynchronous=True, **retval_functions):
    '''
    This decorator takes in an optional parameter for the metric name, and then any number of key/value arguments
    of the format key = metric type, value = function mapping from return value to numeric metric. This can be used
    to specify any number of additional metrics to be saved off from the return data of the function being wrapped.
    '''
    return metric_wrapper_with_tags(
        metric_name=metric_name, retval_functions=retval_functions, asynchronous=asynchronous
    )


def metric_timer_with_tags(metric_name=None, retval_functions=None, asynchronous=True, **metric_tags):
    '''
    This decorator uses the base and inserts the key value pair to automatically record runtime
    '''
    if not retval_functions:
        retval_functions = {}
    retval_functions['runtime'] = True

    return metric_wrapper_with_tags(
        metric_name=metric_name,
        retval_functions=retval_functions,
        asynchronous=asynchronous,
        **metric_tags
    )


def metric_wrapper_with_tags(metric_name=None, retval_functions=None, asynchronous=True, **metric_tags):
    '''
    This decorator takes an optional parameter of metric name and of the retval_function dictionary, which should be
    a dictionary of key/value pairs where key = metric type and value = function mapping from the return value to a
    numeric metric. An example of this would be 'value':(lambda x: x) to record just the return value as
    metric_name.value. The decorator then takes any number of kwargs as additional tag_name/tag_value pairs to use when
    saving the metric in opentsdb. Keep in mind that 2 tags are used by default (class_path and host), and that you can
    never exceed 8 tags total in a metric (limited by opentsdb), so only up to 6 additional tags should be used here.
    '''
    def metric_wrapper_decorator(method):
        @wraps(method)
        def wrapper(*args, **kwargs):
            if test_mode:
                return method(*args, **kwargs)
            start_time = datetime.utcnow()
            only_runtime = False
            try:
                result = method(*args, **kwargs)
            except Exception:
                only_runtime = True
                raise
            finally:
                end_time = datetime.utcnow()

                args_map = {}
                if args or kwargs:
                    args_map = inspect.getcallargs(method, *args, **kwargs)

                if 'self' in args_map:
                    class_n = args_map['self'].__class__.__name__
                else:
                    class_n = method.__name__

                set_class = False
                combined_metric_name = metric_name
                if not metric_name:
                    set_class = True
                    combined_metric_name = '{}'.format(method.__name__)

                combined_metric_name = metric_name_modifier(combined_metric_name, method.__name__, *args, **kwargs)

                if set_class:
                    combined_metric_name = '{}.{}'.format(class_n, combined_metric_name)

                # derive the class_path tag from module_name.class_name.method_name
                class_path = '{}.{}.{}'.format(method.__module__, class_n, method.__name__)

                # append the metric tags as kwargs for the send_tsdb_metric method
                if 'class_path' not in metric_tags:
                    metric_tags['class_path'] = class_path

                runtime = (end_time - start_time).total_seconds() * 1000.0
                if retval_functions and 'runtime' in retval_functions and retval_functions['runtime']:
                    send_tsdb_metric(
                        '{}.runtime'.format(combined_metric_name),
                        runtime,
                        asynchronous=asynchronous,
                        **metric_tags
                    )

                if (not only_runtime) and retval_functions:
                    for metric_type, retval_mapping_function in iter(retval_functions.items()):
                        if hasattr(retval_mapping_function, '__call__'):
                            mapped_value = retval_mapping_function(result)
                            if isinstance(mapped_value, numbers.Number):
                                # Special case of a metric called 'rate', this metric will give ms per X
                                if metric_type == 'rate' and mapped_value > 0:
                                    mapped_value = runtime / mapped_value
                                # Special case of a metric called 'frequency', this metric will give X per second
                                if metric_type == 'frequency':
                                    if runtime > 0:
                                        mapped_value /= (runtime / 1000.0)
                                    else:
                                        continue
                                send_tsdb_metric('{}.{}'.format(combined_metric_name, metric_type),
                                                 mapped_value, asynchronous=asynchronous, **metric_tags)

            return result
        return wrapper
    return metric_wrapper_decorator


def metric_name_modifier(metric_name, method, *args, **kwargs):
    '''
    Method can be re-implemented by any project using this library
    This is called from within the metric_timer decorator, and takes in
    the metric_name and the method and its arguments, and should output a
    new metric_name to use (if it must be transformed based on the method)
    '''
    return metric_name
