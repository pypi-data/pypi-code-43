import time


def tic():
    """Mimics Matlab's tic toc"""
    global __start_time_for_tictoc__
    __start_time_for_tictoc__ = time.time()


def toc():
    """Mimics Matlab's tic toc"""
    if '__start_time_for_tictoc__' in globals():
        elapsed = time.time() - __start_time_for_tictoc__
        print(f"Elapsed time is {elapsed} seconds.")
    else:
        print("Toc: start time not set")
