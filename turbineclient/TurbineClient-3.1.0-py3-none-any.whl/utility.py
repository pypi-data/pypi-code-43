#!/usr/bin/env python
##########################################################################
# $Id: utility.py 4480 2013-12-20 23:20:21Z boverhof $
# Joshua R. Boverhof, LBNL
# See LICENSE.md for copyright notice!
#
#   $Author: boverhof $
#   $Date: 2013-12-20 15:20:21 -0800 (Fri, 20 Dec 2013) $
#   $Rev: 4480 $
#
###########################################################################
import json
import time
import dateutil.parser
import datetime


states = set(['submit', 'create', 'setup', 'running', 'success', 'warning',
              'error', 'expired', 'cancel', 'terminate', 'pause'])


def basic_job_stats(fd, **job_d):
    """
    """
    if not job_d.get('Setup'):
        return
    print("===================================", file=fd)
    print("=  Basic Stats Job %s" % job_d['Id'], file=fd)
    print("===================================", file=fd)

    t1 = dateutil.parser.parse(
        job_d['Setup']) - dateutil.parser.parse(job_d['Create'])
    print("\t%12s -- %s" % ('Queue', t1), file=fd)

    if not job_d.get('Running'):
        t2 = datetime.datetime.utcnow() - dateutil.parser.parse(job_d['Setup'])
        print("\t%12s -- %s" % ('Setup(Active)', t2), file=fd)
        return

    t2 = dateutil.parser.parse(
        job_d['Running']) - dateutil.parser.parse(job_d['Setup'])
    print("\t%12s -- %s" % ('Setup', t2), file=fd)

    if not job_d.get('Finished'):
        t3 = datetime.datetime.utcnow(
        ) - dateutil.parser.parse(job_d['Running'])
        print("\t%12s -- %s" % ('Running', t3), file=fd)
    else:
        t3 = dateutil.parser.parse(
            job_d['Finished']) - dateutil.parser.parse(job_d['Running'])
        print("\t%12s -- %s" % ('Runtime', t3), file=fd)
        print("\t%12s" % ('Done'), file=fd)


def runtime_stats(all_jobs, startName, endName):
    """
    Takes an array of jobs. (Could be all in a session, all successful, all errors, etc.
    Calculates min, max, mean, and total between a starting status and ending status.
    For example, running->finished will give you min, max, etc. for the runtime

    """
    returnDict = {}
    queue_l = map(lambda i: dateutil.parser.parse(i[endName]) -
                  dateutil.parser.parse(i[startName]), all_jobs)

    if queue_l:
        t_max = max(queue_l)
        t_mean = datetime.timedelta(
            0, sum(map(lambda m: m.total_seconds(), queue_l))/len(queue_l))
        t_min = min(queue_l)

        # Can't get min and max of dateutils so sort
        last_to_finish = list(map(
            lambda i: dateutil.parser.parse(i[endName]), all_jobs))
        last_to_finish.sort()
        first_to_setup = list(map(
            lambda i: dateutil.parser.parse(i[startName]), all_jobs))
        first_to_setup.sort()
        total_time = last_to_finish[-1] - first_to_setup[0]

        returnDict['min'] = t_min
        returnDict['max'] = t_max
        returnDict['mean'] = t_mean
        returnDict['total'] = total_time

    else:
        returnDict['min'] = None
        returnDict['max'] = None
        returnDict['mean'] = None
        returnDict['total'] = None

    return returnDict


def print_single_stats(fd, runtime_dict):
    print("\t%12s -- %s" % ("Total", str(runtime_dict['total'])), file=fd)
    print("\t%12s -- %s" % ("Min", str(runtime_dict['min'])), file=fd)
    print("\t%12s -- %s" % ("Mean", str(runtime_dict['mean'])), file=fd)
    print("\t%12s -- %s" % ("Max", str(runtime_dict['max'])), file=fd)


def print_runtime_stats(fd, runtime_dict):
    returnDict = {}

    print("Queue:", file=fd)
    returnDict["Queue"] = runtime_stats(runtime_dict, "Submit", "Setup")
    print_single_stats(fd, returnDict["Queue"])

    print("Setup:", file=fd)
    returnDict["Setup"] = runtime_stats(runtime_dict, "Setup", "Running")
    print_single_stats(fd, returnDict["Setup"])

    print("RunTime:", file=fd)
    returnDict["RunTime"] = runtime_stats(runtime_dict, "Running", "Finished")
    print_single_stats(fd, returnDict["RunTime"])

    print("Total:", file=fd)
    returnDict["Total"] = runtime_stats(runtime_dict, "Submit", "Finished")
    print_single_stats(fd, returnDict["Total"])

    return returnDict


def basic_session_stats(fd, all, verbose=True):
    """
    """
    if len(all) == 0:
        print(all, file=fd)
        return

    print("Basic Statistics", file=fd)
    for s in states:
        c = len(filter(lambda i: i['State'] == s, all))
        if c > 0 or verbose:
            print("\t%12s -- %d" % (s, c), file=fd)

    all_l = filter(lambda i: ("Running" in i and "Setup" in i and "Finished" in i), all)
    success_l = filter(lambda i: (i['State'] == 'success'), all_l)
    error_l = filter(lambda i: i['State'] == 'error', all_l)

    all_l = filter(lambda i: i['State'] in ['error', 'success', 'running'],
                   all)

    queue_l = map(lambda i: dateutil.parser.parse(i['Setup']) -
                  dateutil.parser.parse(i['Submit']), all_l)

    if queue_l:
        print("Queue", file=fd)
        t_max = max(queue_l)

        t_mean = datetime.timedelta(
            0, sum(map(lambda m: m.total_seconds(), queue_l))/len(queue_l))
        t_min = min(queue_l)

        print("\t%12s -- %s" % ('max', t_max), file=fd)
        print("\t%12s -- %s" % ('mean', t_mean), file=fd)
        print("\t%12s -- %s" % ('min', t_min), file=fd)

    all_l = filter(lambda i: ('Running' in i), all_l)
    queue_l = map(lambda i: dateutil.parser.parse(
        i['Running']) - dateutil.parser.parse(i['Setup']), all_l)

    if queue_l:
        t_max = max(queue_l)
        t_mean = datetime.timedelta(
            0, sum(map(lambda m: m.total_seconds(), queue_l))/len(queue_l))
        t_min = min(queue_l)

        print("Setup", file=fd)
        print("\t%12s -- %s" % ('max', t_max), file=fd)
        print("\t%12s -- %s" % ('mean', t_mean), file=fd)
        print("\t%12s -- %s" % ('min', t_min), file=fd)

    queue_l = map(lambda i: dateutil.parser.parse(i['Finished']) -
                  dateutil.parser.parse(i['Running']), success_l)
    if queue_l:
        t_max = max(queue_l)
        t_mean = datetime.timedelta(
            0, sum(map(lambda m: m.total_seconds(), queue_l))/len(queue_l))
        t_min = min(queue_l)

        print("Success Runtime (%d)" % len(queue_l), file=fd)
        print("\t%12s -- %s" % ('max', t_max), file=fd)
        print("\t%12s -- %s" % ('mean', t_mean), file=fd)
        print("\t%12s -- %s" % ('min', t_min), file=fd)

    # if len(success_l) < 2: return

    last_to_finish = list(map(
        lambda i: dateutil.parser.parse(i['Finished']), success_l))
    last_to_finish.sort()
    first_to_setup = list(map(
        lambda i: dateutil.parser.parse(i['Setup']), success_l))
    first_to_setup.sort()

    try:
        run_time = last_to_finish[-1] - first_to_setup[0]
        print("Total Runtime Session (success only): %s" %
              str(run_time), file=fd)
    except:
        pass

    if verbose:
        tail = int(0.10 * len(all_l))
        print("Slowest Runtime Individuals (%d/%d)" %
              (tail, len(all_l)), file=fd)
        print("\t%10s %18s %18s %18s %18s" %
              ("Id", "Queue", "Setup", "Runtime", "Total"), file=fd)
        all_times = list(map(lambda i: (i['Id'],
                                   dateutil.parser.parse(
                                       i['Setup'])-dateutil.parser.parse(i['Submit']),
                                   dateutil.parser.parse(
                                       i['Running'])-dateutil.parser.parse(i['Setup']),
                                   dateutil.parser.parse(
                                       i['Finished'])-dateutil.parser.parse(i['Running']),
                                   dateutil.parser.parse(i['Finished'])-dateutil.parser.parse(i['Submit'])),
                        success_l))
        all_times.sort(lambda x, y: int((y[3]-x[3]).total_seconds()))
        for i in all_times[:tail]:
            print('\t%10s -- %15s -- %15s -- %15s -- %15s' % i, file=fd)

    if error_l:
        print("Total Errors (%d)" % len(error_l), file=fd)
        print("", file=fd)
        l = filter(lambda i: i.get('Running') is None, error_l)
        print("  Error Setup (%d)" % len(l), file=fd)
        if len(l):
            print(": setup time stats", file=fd)
            queue_l = map(lambda i: dateutil.parser.parse(
                i['Finished']) - dateutil.parser.parse(i['Setup']), l)
            print("\t%12s -- %s" % ('max', max(queue_l)), file=fd)
            print("\t%12s -- %s" % ('mean', datetime.timedelta(0,
                                                               sum(map(lambda m: m.total_seconds(), queue_l))/len(queue_l))), file=fd)
            print("\t%12s -- %s" % ('min', min(queue_l)), file=fd)
        else:
            print("", file=fd)

        l = filter(lambda i: i.get('Running') is not None and i.get(
            'Finished') is not None, error_l)
        print("  Error Running (%d)" % len(l), file=fd)
        if len(l):
            print(": runtime stats", file=fd)
            queue_l = map(lambda i: dateutil.parser.parse(
                i['Finished']) - dateutil.parser.parse(i['Running']), l)
            print("\t%12s -- %s" % ('max', max(queue_l)), file=fd)
            print("\t%12s -- %s" % ('mean', datetime.timedelta(0,
                                                               sum(map(lambda m: m.total_seconds(), queue_l))/len(queue_l))), file=fd)
            print("\t%12s -- %s" % ('min', min(queue_l)), file=fd)
        else:
            print("", file=fd)

    if not verbose:
        return

    print("== Consumers Job Success", file=fd)
    total_d = {}
    count_d = {}
    setup_d = {}
    end_d = {}
    for i in success_l:
        k = i['Consumer']
        finished = dateutil.parser.parse(i['Finished'])
        setup = dateutil.parser.parse(i['Setup'])
        if k not in total_d:
            count_d[i['Consumer']] = 0
            total_d[i['Consumer']] = datetime.timedelta(0)
            setup_d[i['Consumer']] = setup
            end_d[i['Consumer']] = finished

        count_d[i['Consumer']] += 1
        total_d[i['Consumer']] += (finished - setup)
        if setup < setup_d[i['Consumer']]:
            setup_d[i['Consumer']] = setup
        if finished > end_d[i['Consumer']]:
            end_d[i['Consumer']] = finished
        end_d[i['Consumer']] = dateutil.parser.parse(i['Finished'])

    print("    %30s  %5s   %14s   %14s   %14s" %
          ("Consumer", "Count", "Total", "Runtime", "Overhead"), file=fd)

    i = 1
    items = count_d.items()

    def cmp(i, j):
        if i[1] > j[1]:
            return -1
        if i[1] == j[1]:
            return 0
        return 1
    items.sort(cmp)

    for k, count in items:
        v = total_d[k]
        total = end_d[k]-setup_d[k]
        print("%2d %12s  |  %5s  |  %12s  |  %12s  |  %12s" %
              (i, k, count, total, v, total-v), file=fd)
        i += 1
