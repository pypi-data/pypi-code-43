from multiprocessing import Pool, cpu_count
from tqdm import tqdm

def pool_worker(target, inputs, num_worker=None, verbose=True):
    """Run target function in multi-process

    Parameters
    ----------
    target : func
        function to excute multi process
    inputs: list
        list of argument of target function
    num_worker: int
    number of worker
    verbose: bool
        True: progress bar
        False: silent

    Returns
    -------
    list of output of func
    """
    if num_worker is None:
        num_worker = cpu_count()

    if verbose:
        with Pool(num_worker) as p:
            res = list(tqdm(p.imap(target, inputs), total=len(inputs)))
    else:
        with Pool(num_worker) as p:
            res = p.map(target, inputs)
    return res