import traceback

from itertools import chain, islice


def concurrent_eval(func, cases, comm, allgather=False, model_mpi=None):
    """
    Run the given function concurrently on all procs in the communicator.

    NOTE: This function should NOT be used if the concurrent function makes
    any internal collective MPI calls.

    Parameters
    ----------
    func : function
        The function to execute in workers.
    cases : iter of function args
        Entries are assumed to be of the form (args, kwargs) where
        kwargs are allowed to be None and args should be a list or tuple.
    comm : MPI communicator or None
        The MPI communicator that is shared between the master and workers.
        If None, the function will be executed serially.
    allgather : bool(False)
        If True, the results will be allgathered to all procs in the comm.
        Otherwise, results will be gathered to rank 0 only.
    model_mpi : None or tuple
        If the function in func runs in parallel, then this will be a tuple containing the total
        number of cases to evaluate concurrently, and the color of the cases to evaluate on this
        rank.
    raise_exceptions : bool(True)
        If True, any exceptions thrown when calling func will simply be raised.

    Returns
    -------
    object
        Return from function.
    """
    results = []

    if comm is None:
        it = cases
    else:
        rank = comm.rank
        if model_mpi is not None:
            size, color = model_mpi
            it = islice(cases, color, None, size)
        else:
            it = islice(cases, rank, None, comm.size)

    for args, kwargs in it:
        try:
            if kwargs:
                retval = func(*args, **kwargs)
            else:
                retval = func(*args)
        except Exception as e:
            err = traceback.format_exc()
            retval = None
        else:
            err = None

        results.append((retval, err))

    if comm is not None:
        if allgather:
            allresults = comm.allgather(results)

            # Limit results to 1 set from each color.
            if model_mpi is not None:
                allresults = allresults[:size]

            results = list(chain(*allresults))
        else:
            allresults = comm.gather(results, root=0)
            if comm.rank == 0:

                # Limit results to 1 set from each color.
                if model_mpi is not None:
                    allresults = allresults[:size]

                results = list(chain(*allresults))
            else:
                results = None

    return results
