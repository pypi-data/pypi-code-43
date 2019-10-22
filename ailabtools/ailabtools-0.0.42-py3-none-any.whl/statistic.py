import os
import numpy as np

import random
from random import shuffle
import matplotlib.pyplot as plt

from tqdm import tqdm
from glob import glob

def get_raw_data(path):
    '''Get raw data pair from path
    
    Parameters
    ----------
    path : str
        target path
    
    Returns
    -------
    tuple
        data pair xs, ys
    '''

    paths = glob(os.path.join(path, '**/*.*'), recursive=True)
    
    data_dict = {}
    for p in paths:
        ppp = p.split('/')
        cat = ppp[-2]
        if cat in data_dict:
            data_dict[cat].append(p)
        else:
            data_dict[cat] = [p]
    
    return convert_dict_to_pair(data_dict)

def stat(arr, name=''):
    '''Print statistic of given array
    
    Parameters
    ----------
    arr : list
        list of number for statistic
    
    '''
    arr = np.array(arr)
    print((name, arr.shape, 'min:', np.min(arr), 'max:', np.max(arr), 'std:', np.std(arr), 'mean:', np.mean(arr), 'median:', np.median(arr)))

def get_weight_dict(xs, ys, multiply=10):
    '''Automatically generate dictionary of weight for each class
    
    Parameters
    ----------
    xs : list
        list of every x value
    ys : list
        list of label for every given x value
    multiply : int, optional
        each of weight will be multiply by this value (the default is 10)
    
    Returns
    -------
    dict
        dictionary of class weight
    '''

    _, stat_key, stat_num = statistic_data(xs, ys)
    maxx = np.max(stat_num)
    stat_weights = maxx/stat_num
    stat_weights = stat_weights*multiply/np.sum(stat_weights)

    weights_dict = {}
    for k, w in zip(stat_key, stat_weights):
        weights_dict[k] = w
        
    return weights_dict

def statistic_data(xs, ys, title=None):
    '''Combine raw value to dictionary
    
    Parameters
    ----------
    xs : list
        list of all x value
    ys : list
        list of class of all given x value
    title : bool, optional
        Wheather plot graph or not (the default is None, which is not draw graph by default)
    
    Returns
    -------
    tuple
        Data dictionary, all classes, number of item of each class
    '''

    data_dic = {}
    for y, p in zip(ys, xs):
        if y in data_dic:
            data_dic[y] = data_dic[y] + [p]
        else:
            data_dic[y] = [p]

    keys = list(data_dic.keys())
    nums = [len(data_dic[k]) for k in keys]
    
    if title:
        print(title, 'sum:', np.sum(nums))
        plt.bar(keys, nums)
        plt.show()

        print(nums)
        stat(nums)
    
    return data_dic, keys, nums

def divide_data(xs, ys, chunk_num=5, keeps=[]):
    '''Divide given raw data to several chunk, which have same distribution
    
    Parameters
    ----------
    xs : list
        all item of x value
    ys : list
        all class of every given x value
    chunk_num : int, optional
        number of divided chunk (the default is 5)
    keeps : list, optional
        all data of given class indice will be keep when devide
    
    Returns
    -------
    list
        list of divided dictionary
    '''

    assert chunk_num > 2, 'Chunnk size must greater than 2'
    
    def get_sample(arr, chunk_num):
        shuffle(arr)
        
        percent = float(1/chunk_num)
        size = int(percent*len(arr))
        
        f = arr[:size]
        if chunk_num == 3:
            s = arr[size:size+size]
            l = arr[size + size:]
            return [f, s, l]
        
        res = [f]
        for i in range(1,chunk_num - 1):
            res.append(arr[size*i:size*i + size])
        
        res.append(arr[(chunk_num - 1)*size:])
        
        return res
    
    stat_dic, _, _ = statistic_data(xs, ys)
    
    res = []
    for _ in range(0, chunk_num):
        res.append({})
        
    for k in stat_dic:
        if k in keeps:
            for d in res:
                d[k] = stat_dic[k]
        else:
            samples = get_sample(stat_dic[k], chunk_num)
            for d, s in zip(res, samples):
                d[k] = s
    
    return res

def upsample_data(xs, ys):
    '''Upsampling data
    
    Parameters
    ----------
    xs : list
        All data item x
    ys : list
        All class for each given data x
    
    Returns
    -------
    tuple
        Upsampled data, number item of each class will be balanced
    '''

    data_dic, keys, nums = statistic_data(xs, ys, title='before')

    nums_arr = np.array(nums)
    maxx = np.max(nums_arr)
    scalenum = (maxx/nums_arr + 0.5).astype(np.uint8)

    for key, scale in zip(keys, scalenum):
        data_dic[key] = (data_dic[key]*scale)[:maxx]

    numdata11, numdata22 = convert_dict_to_pair(data_dic)

    _, _, _ = statistic_data(numdata11, numdata22, title='after')
    
    return numdata11, numdata22

def convert_dict_to_pair(data_dic):
    '''Convert dictionary to raw data
    
    Parameters
    ----------
    data_dic : dict
        target data dictionary, keys of data_dic is class name, while value of each keys is array of x values belong to that class
    
    Returns
    -------
    tuple
        tuple of raw data
    '''

    numdata1 = []
    numdata2 = []
    for k in data_dic:
        numdata1.extend(data_dic[k])
        numdata2.extend([k]*len(data_dic[k]))

    pair = [(a, b) for a, b in zip(numdata1, numdata2)]
    shuffle(pair)
    numdata11 = [a[0] for a in pair]
    numdata22 = [a[1] for a in pair]
    
    return numdata11, numdata22

def split_data(xs, ys, alpha=0.9, maxx=None):
    '''Split given raw data into 2 chunk
    
    Parameters
    ----------
    xs : list
        All data x
    ys : list
        Class of each given x
    alpha : float, optional
        Split ratio if alpha < 1.0, otherwise is the number of item for each classes in first chunk (the default is 0.9, which means first chunk will contain 90% data of given xs, second chunk contain the rest)
    maxx : int, optional
        Maximum number of item for each first chunk, maxx will not makes any affect if alpha > 1 (the default is None, which means no affect)
    
    Returns
    -------
    tuple
        tuple of raw dataof 2 chunks
    '''

    data_dic, _, _ = statistic_data(xs, ys)
    
    assert alpha > 0, 'alpha must be greater than 0'
    if maxx is not None:
        assert maxx > 0, 'maxx must be greater than 0'

    if alpha < 1.0:
        def get_sample(arr, alpha=0.9, maxx=None):
            shuffle(arr)
            i = int(alpha*len(arr))
            if maxx:
                if alpha <= 0.5:
                    if i > maxx:
                        i=maxx
                else:
                    if len(arr) - i > maxx:
                        i = len(arr) - maxx
            return arr[:i], arr[i:]
    else:
        def get_sample(arr, alpha=1000, maxx=None):
            shuffle(arr)
            i = alpha
            return arr[:i], arr[i:]

    sdict_1, sdict_2 = {}, {}
    for k in data_dic:
        a1, a2 = get_sample(data_dic[k], alpha, maxx)
        sdict_1[k] = a1
        sdict_2[k] = a2
    
    x1, y1 = convert_dict_to_pair(sdict_1)
    x2, y2 = convert_dict_to_pair(sdict_2)
    return x1, y1, x2, y2
