

def parallelize_preprocess(func, iterator, processes, progress_bar=False):
    from joblib import Parallel, delayed
    from tqdm import tqdm
    
    iterator = tqdm(iterator) if progress_bar else iterator
    return Parallel(n_jobs=processes)(delayed(func)(line) for line in iterator)
