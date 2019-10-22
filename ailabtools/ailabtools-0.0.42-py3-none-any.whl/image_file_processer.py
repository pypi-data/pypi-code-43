import magic
import hashlib
import nmslib
from subprocess import call
from PIL import Image
from send2trash import send2trash
from tqdm import tqdm
import numpy as np
from collections import Counter
from .ailab_multiprocessing import pool_worker

import warnings
warnings.simplefilter("ignore")
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from multiprocessing import cpu_count

def __hashfile(path, blocksize = 65536):
    afile = open(path, 'rb')
    hasher = hashlib.md5()
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    afile.close()
    return hasher.hexdigest()

def __change_namge(cur_name, new_name):
    call(['mv', cur_name, new_name])
    log = 'change name file {} to {}'.format(cur_name, new_name)
    return log
    
def __adj_extension(path):
    real_ex = magic.from_file(path, mime=True).split('/')[1]
    cur_ex = path.split('.')[-1]
    if cur_ex != real_ex:
        return __change_namge(path, '{}.{}'.format(path, real_ex))
    else:
        return ''

def __get_p_hash(path):
    im = Image.open(path).convert('L')
    temp = imagehash.phash(im).hash.flatten()
    result = ' '.join([str(int(item)) for item in temp])
    im.close()
    del im, temp
    return result

def adj_extension(paths, num_worker=None, verbose=True):
    """Adjust extension of files
    wrong_name => wrong_name.true_extension

    Parameters
    ----------
    paths : list
        list of path
    num_worker: int
        number of worker
    verbose: bool
        True: progress bar
        False: silent

    Returns
    -------
    logs: list of str
        list name files adjusted extension and new name
    """
    logs = pool_worker(__adj_extension, paths, num_worker, verbose)
    return [log for log in logs if log != '']
        
        
def __rm_unreadable(path):
    try:
        Image.open(path)
        return ''
    except:
        send2trash(path)
        log = 'remove file: {}'.format(path)
        return log
        
def rm_unreadable(paths, num_worker=None, verbose=True):
    """Remove file witch PIL.Image faile to read

    Parameters
    ----------
    paths : list
        list of path
    num_worker: int
        number of worker
    verbose: bool
        True: progress bar
        False: silent

    Returns
    -------
    logs: list of str
        list name files removed
    """
    logs = pool_worker(__rm_unreadable, paths, num_worker, verbose)
    return [log for log in logs if log != '']
        
def rm_duplicate(paths, num_worker=None, verbose=True):
    """Remove duplicate file

    Parameters
    ----------
    paths : list
        list of path
    num_worker: int
        number of worker
    verbose: bool
        True: progress bar
        False: silent

    Returns
    -------
    logs: list of str
        list name files removed
    """
    hashes = pool_worker(__hashfile, paths, num_worker, verbose)
        
    filted = {}
    remove_list = []
    logs = []
    for i in range(len(hashes)):
        if hashes[i] not in filted:
            filted[hashes[i]] = paths[i]
        else:
            send2trash(paths[i])
            logs.append('remove file: {} duplicate with: {}'.format(paths[i], filted[hashes[i]]))
    return logs

def rm_perceptual_duplicate(new_paths, old_paths=None, threshold=5, num_threads=None):
    """Extract imgs that perceptualy duplicated with another

    Parameters
    ----------
    new_paths : list
        list of path of new images
    old_paths: list
        list of path of old images
    threshold: int ~ [0, 64]
        minimum distant of perceptual hash of frame (http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html)
    num_threads: int
        number of worker

    Returns
    -------
    None
    """
    k=100 #k nearest neighbor
    if num_threads is None:
        num_threads = cpu_count()
    
    new_hashes = pool_worker(__get_p_hash, new_paths)
    
    index = nmslib.init(method='hnsw', 
                        space='bit_hamming', 
                        dtype=nmslib.DistType.INT, 
                        data_type=nmslib.DataType.OBJECT_AS_STRING)

    index.addDataPointBatch(new_hashes)
    index.createIndex({'post': 2}, print_progress=True)
        
    neighbours = index.knnQueryBatch(new_hashes, k=k, num_threads=num_threads)
    
    similar = {}
    for i, item in enumerate(neighbours):
        similar[i] = []
        ids, distances = item
        for id, distance in zip(ids, distances):
            if distance <= threshold:
                if i != id:
                    similar[i].append(id)
            else:
                break

    cats = [None]*len(new_hashes)
    cur_cat = 0
    for im_id in range(len(new_hashes)):
        if cats[im_id] is None:
            cats[im_id] = cur_cat
            cur_cat += 1

        for child_im_id in similar[im_id]:
            if cats[child_im_id] is None:
                cats[child_im_id] = cats[im_id]
                
    rm_indexes = []
    cat_set = set()
    for i, cat in enumerate(cats):
        if cat in cat_set:
            rm_indexes.append(i)
        else:
            cat_set.add(cat)

    rm_paths = list(np.array(new_paths)[rm_indexes])
    new_paths = list(np.array(new_paths)[list(set(list(range(len(new_paths)))) - set(rm_indexes))])
    new_hashes = list(np.array(new_hashes)[list(set(list(range(len(new_paths)))) - set(rm_indexes))])
    
    if old_paths is None:
        return rm_paths
    
    old_hashes = pool_worker(__get_p_hash, old_paths)
    index = nmslib.init(method='hnsw', 
                        space='bit_hamming', 
                        dtype=nmslib.DistType.INT, 
                        data_type=nmslib.DataType.OBJECT_AS_STRING)

    index.addDataPointBatch(old_hashes)
    index.createIndex({'post': 2}, print_progress=True)
    
    neighbours = index.knnQueryBatch(new_hashes, k=k, num_threads=num_threads)
    
    rm_indexes = []
    for i, item in enumerate(neighbours):
        ids, distances = item
        if min(distances) <= threshold:
            rm_indexes.append(i)
            
    rm_paths += list(np.array(new_paths)[rm_indexes])
    
    return rm_paths