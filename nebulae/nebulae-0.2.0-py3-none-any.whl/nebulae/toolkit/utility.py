#!/usr/bin/env python
'''
utility
Created by Seria at 14/11/2018 8:33 PM
Email: zzqsummerai@yeah.net

                    _ooOoo_
                  o888888888o
                 o88`_ . _`88o
                 (|  0   0  |)
                 O \   。   / O
              _____/`-----‘\_____
            .’   \||  _ _  ||/   `.
            |  _ |||   |   ||| _  |
            |  |  \\       //  |  |
            |  |    \-----/    |  |
             \ .\ ___/- -\___ /. /
         ,--- /   ___\<|>/___   \ ---,
         | |:    \    \ /    /    :| |
         `\--\_    -. ___ .-    _/--/‘
   ===========  \__  NOBUG  __/  ===========
   
'''
# -*- coding:utf-8 -*-

import json
import numpy as np
import subprocess as subp
import h5py
import os

from ..law import Law

def toDenseLabel(labels, nclasses, on_value=1, off_value=0):
    batch_size = labels.shape[0]
    # initialize dense labels
    dense = off_value * np.ones((batch_size * nclasses))
    indices = []
    if isinstance(labels[0], str):
        for b in range(batch_size):
            indices += [int(s) + b * nclasses for s in labels[b].split(Law.CHAR_SEP)]
    else: # labels is a nested array
        for b in range(batch_size):
            indices += [l + b * nclasses for l in labels[b]]
        dense[indices] = on_value
    return np.reshape(dense, (batch_size, nclasses))


def getAvailabelGPU(ngpus, least_mem):
    p = subp.Popen('nvidia-smi', stdout=subp.PIPE)
    gpu_id = 0  # next gpu we are about to probe
    flag_gpu = False
    id_mem = []  # gpu having avialable memory greater than least requirement
    qualified = 0  # number of gpus that meet requirement
    for l in p.stdout.readlines():
        line = l.decode('utf-8').split()
        if len(line) < 1:
            break
        elif len(line) < 2:
            continue
        if line[1] == str(gpu_id):
            flag_gpu = True
            continue
        if flag_gpu:
            vacancy = int(line[10].split('M')[0]) - int(line[8].split('M')[0])
            if vacancy > least_mem:
                if qualified < ngpus:
                    id_mem.append((gpu_id, vacancy)) # (id, mem) of gpu
                else:
                    id_mem.sort(key=lambda x: x[1])
                    if vacancy > id_mem[0][0]:
                        id_mem[0] = (gpu_id, vacancy)
            gpu_id += 1
            flag_gpu = False
    return [elem[0] for elem in id_mem]

def parseConfig(config_path):
    with open(config_path, 'r') as config_file:
        return json.load(config_file)

def recordConfig(config_path, config):
    with open(config_path, 'w') as config_file:
        json.dump(config, config_file, indent=4)

def _mergeFuel(src_dir, src, dst, dtype, keep_src=True):
    data = {}
    info_keys = []
    shards = len(src)
    print('+' + (23 + 2 * shards + len(dst)) * '-' + '+')
    # read
    ending_char = '\r'
    for i, f in enumerate(src):
        hdf5 = h5py.File(os.path.join(src_dir, f), 'r')
        if i == 0:
            for key in hdf5.keys():
                info_keys.append(key)
            for key in info_keys:
                if key == Law.FRAME_KEY:
                    data[key] = 0
                else:
                    data[key] = []
        for key in info_keys:
            if key == Law.FRAME_KEY:
                frames = hdf5[key]
                data[key] = frames if frames>data[key] else data[key]
            else:
                data[key].extend(hdf5[key][()].tolist())
        hdf5.close()
        if not keep_src:
            os.remove(os.path.join(src_dir, f))

        progress = i+1
        yellow_bar = progress * '❖-'
        space_bar = (shards - progress) * '◇-'
        if progress == shards:
            ending_char = '\n'
        print('| Merging data  \033[1;35m%s\033[0m  ⊰⟦-%s%s⟧⊱ |'
              % (dst, yellow_bar, space_bar), end=ending_char)
    # write
    hdf5 = h5py.File(os.path.join(src_dir, dst), 'w')
    for key in info_keys:
        if dtype[key].startswith('v'):  # dealing with encoded / varied data
            dt = h5py.special_dtype(vlen=dtype[key])
            hdf5.create_dataset(key, dtype=dt, data=np.array(data[key]))
        elif key == Law.FRAME_KEY:
            hdf5[key] = data[key]
        else:
            hdf5[key] = np.array(data[key]).astype(dtype[key])
    hdf5.close()
    print('+' + (23 + 2 * shards + len(dst)) * '-' + '+')

def _fillFuel(src, key, data):
    hdf5 = h5py.File(src, 'a')
    hdf5[key] = data
    hdf5.close()

def _deductFuel(src, key):
    hdf5 = h5py.File(src, 'a')
    del hdf5[key]
    hdf5.close()