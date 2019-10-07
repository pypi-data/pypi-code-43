import multiprocessing as mp
import os
import sys


def serial_call(jobs):
    results = []
    try:
        for job in jobs:
            func, args = job[0], job[1:]
            r = func(*args)
            results.append(r)
    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, exiting")

    return results


def parallel_call(jobs, processes=8):
    pool = mp.Pool(processes=processes)
    output = None
    try:
        results = []
        for job in jobs:
            func, args = job[0], job[1:]
            r = pool.apply_async(func, args)
            results.append(r)
        output = [res.get() for res in results]
    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, terminating workers")
        pool.terminate()
        pool.join()
    else:
        pool.close()
        pool.join()

    return output


def restore_original_env(kwargs = None):
    if getattr(sys, 'frozen', False):
        env = dict(os.environ)  # make a copy of the environment
        lp_key = 'LD_LIBRARY_PATH'  # for Linux and *BSD.
        lp_orig = env.get(lp_key + '_ORIG')  # pyinstaller >= 20160820 has this
        if lp_orig is not None:
            env[lp_key] = lp_orig  # restore the original, unmodified value
        else:
            env.pop(lp_key, None)  # last resort: remove the env var
        actual_env = env
    else:
        actual_env = os.environ

    if kwargs and 'env' in kwargs:
        actual_env.update(kwargs['env'])
        del kwargs['env']

    return actual_env
