#!/usr/bin/env python
"""Helper functions to multiprocess functions easily"""
########################################################################
# File: multiprocess.py
#  executable: multiprocess.py
#
# Author: Andrew Bailey, Most work was originally done by Trevor Pesout
# History: 03/05/18 Created
########################################################################

import time
from multiprocessing import Manager, Process, current_process
from timeit import default_timer as timer
from py3helpers.utils import convert_seconds

TOTAL_KEY = "total"
FAILURE_KEY = "failure"
MEM_USAGE_KEY = "mem_usage"


def run_service(service, iterable, arguments, iterable_argument_names, worker_count,
                service_arguments={}, log_function=print):
    """Take in a service (function) with an iterable list, arguments to be passed to
        the "work" function done on each element, and an argument to append to these 'work' arguments as name of
        the element.

        :param service: function which will extract arguments from a work queue and put return values in done queue
        :param iterable: iterable list of arguments to be passed in
        :param arguments: all non iterable arguments
        :param iterable_argument_names: names of the arguments which are being zipped with the
        :param worker_count: number of workers or processes to spin up
        :param service_arguments: arguments to be passed to Process
        :param log_function: usually just print but will pass logging string info if log function is used
        :return: total, failure, messages, output
    """

    start = timer()
    args = list(arguments.keys())
    args.extend(iterable_argument_names)
    if log_function is not None:
        log_function("[run_service] running service {} with {} workers".format(service, worker_count))

    # setup workers for multiprocessing
    work_queue = Manager().Queue()
    done_queue = Manager().Queue()

    # add everything to work queue
    jobs = []
    for x in iterable:
        if type(x) is not tuple:
            x = [x]
        args = dict(dict(zip(iterable_argument_names, x)),
                    **arguments)
        work_queue.put(args)

    # start workers
    for w in range(worker_count):
        p = Process(target=service, args=(work_queue, done_queue), kwargs=service_arguments)
        p.start()
        jobs.append(p)
        work_queue.put('STOP')

    # wait for threads to finish, then stop the done queue
    for p in jobs:
        p.join()
    done_queue.put('STOP')

    # if example service model is used, metrics can be gathered in this way
    messages = []
    output = []
    total = 0
    failure = 0
    no_stop = True
    while no_stop:
        f = done_queue.get()
        if isinstance(f, str):
            if f == "STOP":
                no_stop = False
            elif f.startswith(TOTAL_KEY):
                total += int(f.split(":")[1])
            elif f.startswith(FAILURE_KEY):
                failure += int(f.split(":")[1])
            else:
                messages.append(f)
        else:
            output.append(f)
    stop = timer()
    run_time = stop - start
    d, h, m, s = convert_seconds(run_time)
    log_time = "{} days {} hr {} min {} sec".format(d, h, m, s)
    log_function("[run_service] Completed in {} seconds.".format(stop - start))
    # if we should be logging and if there is material to be logged
    if log_function is not None and (total + failure + len(messages)) > 0:
        log_function(
            "[run_service] Summary {}:\n[run_service]\tTime: {}\n[run_service]\tTotal: {}\n[run_service]\tFailure: {}"
            .format(service, log_time, total, failure))
        log_function("[run_service]\tMessages:\n[run_service]\t\t{}".format("\n[run_service]\t\t".join(messages)))
    # return relevant info
    return total, failure, messages, output


class BasicService(object):

    def __init__(self, function, service_name="example_service"):
        self.function = function
        self.service_name = service_name

    def run(self, work_queue, done_queue):

        """
        Service used by the multiprocess module for an example of what should be created for multiprocessing
        :param work_queue: arguments to be done
        :param done_queue: errors and returns to be put
        :param service_name: name of the service
        """
        # prep
        total_handled = 0
        failure_count = 0

        # catch overall exceptions
        try:
            for f in iter(work_queue.get, 'STOP'):
                # catch exceptions on each element
                try:
                    return_value = self.function(**f)
                    done_queue.put(return_value)
                except Exception as e:
                    # get error and log it
                    message = "{}:{}".format(type(e), str(e))
                    error = "{} '{}' failed with: {}".format(self.service_name, current_process().name, message)
                    print("[{}] ".format(self.service_name) + error)
                    done_queue.put(error)
                    failure_count += 1

                # increment total handling
                total_handled += 1

        except Exception as e:
            # get error and log it
            message = "{}:{}".format(type(e), str(e))
            error = "{} '{}' critically failed with: {}".format(self.service_name, current_process().name, message)
            print("[{}] ".format(self.service_name) + error)
            done_queue.put(error)

        finally:
            # logging and final reporting
            print("[%s] '%s' completed %d calls with %d failures"
                  % (self.service_name, current_process().name, total_handled, failure_count))
            done_queue.put("{}:{}".format(TOTAL_KEY, total_handled))
            done_queue.put("{}:{}".format(FAILURE_KEY, failure_count))
