import operator
import os
import re
import math
import numpy as np
import random
import torch
from collections import OrderedDict
from collections.abc import Iterable
from functools import partial
from torch import nn
from torch import tensor
from pathlib import Path


# The inventory of all possible callback functions
ALL_CALLBACKS = {'begin_batch', 'after_pred', 'after_loss', 'after_backward',
            'after_step', 'after_cancel_batch', 'after_batch',
            'after_cancel_epoch', 'begin_fit', 'begin_epoch', 'begin_epoch',
            'begin_validate', 'after_epoch', 'after_cancel_train',
            'after_fit'}

# learner exceptions

class CancelTrainException(Exception): pass
class CancelEpochException(Exception): pass
class CancelBatchException(Exception): pass

# tests

def test(a, b, cmp, cname=None):
    if cname is None: cname = cmp.__name__
    assert cmp(a, b), f"{cname}:\n{a}\n{b}"

def test_eq(a, b): test(a, b, operator.eq, '==')

def near(a, b): return torch.allclose(a, b, rtol=1e-3, atol=1e-5)
def test_near(a, b): test(a, b, near)


# renaming attrs

_camel_re1 = re.compile('(.)([A-Z][a-z]+)')
_camel_re2 = re.compile('([a-z0-9])([A-Z])')

def camel2snake(name):
    s1 = re.sub(_camel_re1, r'\1_\2', name)
    return re.sub(_camel_re2, r'\1_\2', s1).lower()


# lr schedulers

def annealer(f):
    def _inner(start, end): return partial(f, start, end)
    return _inner

@annealer
def sched_cos(start, end, pos):
    return start + (1 + math.cos(math.pi*(1-pos))) * (end-start) / 2

@annealer
def sched_lin(start, end, pos): return start + pos*(end-start)
@annealer
def sched_no(start, end, pos):  return start
@annealer
def sched_exp(start, end, pos): return start * (end/start) ** pos

def cos_1cycle_anneal(start, high, end):
    return [sched_cos(start, high), sched_cos(high, end)]

def combine_scheds(pcts, scheds):
    """
    pcts are the percentages of time the schedules in sched should be
    active.
    """
    assert len(pcts) == len(scheds)
    assert sum(pcts) == 1.
    pcts = tensor([0] + listify(pcts))
    assert torch.all(pcts >= 0)
    pcts = torch.cumsum(pcts, 0)
    def _inner(pos):
        idx = (pos >= pcts).nonzero().max()
        actual_pos = (pos-pcts[idx]) / (pcts[idx+1]-pcts[idx])
        return scheds[idx](actual_pos)
    return _inner

def create_phases(phases):
    phases = listify(phases)
    return phases + [1-sum(phases)]


# data block / dataset related functions

def read_file(filename):
    with open(filename, 'r', encoding = 'utf8') as f: return f.read()

def _get_files(path, filenames, extensions=None):
    path = Path(path)
    results = [path/filename for filename in filenames \
               if not filename.startswith('.') and \
               ((not extensions) or \
                f'.{filename.split(".")[-1].lower()}' in extensions)]
    return results

def get_files(path, extensions=None, recurse=False, include=None):
    path = Path(path)
    extensions = setify(extensions)
    extensions = {extension.lower() for extension in extensions}
    if recurse:
        results = []
        for i, (root, dirs, files) in enumerate(os.walk(path)):
            if include is not None and i == 0:
                dirs[:] = [dir for dir in dirs if dir in include]
            else:
                dirs[:] = [dir for dir in dirs if not dir.startswith('.')]
            results += _get_files(root, files, extensions)
        return results
    else:
        files = [item.name for item in os.scandir(path) if item.is_file()]
        return _get_files(path, files, extensions)

def df_names_to_idx(col_names, df):
    "Return the column indexes of col_names in df."
    if isinstance(col_names[0], int):
        return col_names
    return [df.columns.get_loc(col_name) for col_name in col_names]

def is1d(arraylike_object):
    "Return `True` if `arraylike_object` is one-dimensional"
    return len(arraylike_object.shape) == 1 if hasattr(arraylike_object, 'shape') else len(np.array(arraylike_object).shape) == 1

def _maybe_squeeze(array):
    return (array if is1d(array) else np.squeeze(array))

def match_embeds(old_wgts, old_vocab, new_vocab):
    """
    Matches embeddings from an old_vocab to a new_vocab when transfer learning:
    -- old_vocab is the vocab associated with the pretrained model
    -- new_vocab is the vocab associated with the new corpus
    -- old_wgts are the weights from the old pretrained model (a state dict)
    We end up with embeddings for the new_vocab that are the same as the old
    ones whenever an item is both in the new_vocab and in the old_vocab. When an
    item in the new_vocab is missing from the old_vocab, it is assigned an
    average embedding.
    The old_wgts are updated with respect to the relevant layers. The parameters
    of the other layers are kept the same. The updated old_wgts are returned in
    full so that they can be loaded into the new model.
    """
    wgts = old_wgts['0.emb.weight']
    bias = old_wgts['1.decoder.bias']
    # compute mean weights; we'll assign them to new vocab items
    wgts_m, bias_m = wgts.mean(dim=0), bias.mean()
    # initialize new weights
    new_wgts = wgts.new_zeros(len(new_vocab), wgts.size(1))
    new_bias = bias.new_zeros(len(new_vocab))
    # reverse old vocab so that we can index into the old weights
    otoi = {v:k for k,v in enumerate(old_vocab)}
    # we check every item in the new vocab
    for i,w in enumerate(new_vocab):
        # if the item is in the old_vocab, we transfer the old weights
        if w in otoi:
            idx = otoi[w]
            new_wgts[i], new_bias[i] = wgts[idx], bias[idx]
        # if the item is not in the old_vocab, we give it average weights
        else: new_wgts[i], new_bias[i] = wgts_m, bias_m
    old_wgts['0.emb.weight']        = new_wgts
    old_wgts['0.emb_dp.emb.weight'] = new_wgts
    old_wgts['1.decoder.weight']    = new_wgts
    old_wgts['1.decoder.bias']      = new_bias
    return old_wgts

# misc

def listify(collection):
    if collection is None:
        return []
    if isinstance(collection, list):
        return collection
    if isinstance(collection, str):
        return [collection]
    if isinstance(collection, Iterable):
        return list(collection)
    return [collection]

def setify(collection):
    return collection if isinstance(collection,set) else \
           set(listify(collection))

def uniqueify(x, sort=False):
    results = list(OrderedDict.fromkeys(x).keys())
    if sort:
        results.sort()
    return results

def compose(x, funcs, *args, order_key='_order', **kwargs):
    """
    Composes the functions in funcs and applies them to x.
    More expplicitly:
    -- we sort the functions in funcs according to order_key
    -- we apply them successively to the input x
    """
    key = lambda o: getattr(o, order_key, 0)
    for f in sorted(listify(funcs), key=key):
        x = f(x, **kwargs)
    return x

def param_getter(m):
    return m.parameters()

def random_splitter(filename, proportion_valid):
    return random.random() < proportion_valid

# def normalize(x, m, s):
    # return (x-m)/s

# def normalize_to(train, valid):
    # m,s = train.mean(),train.std()
    # return normalize(train, m, s), normalize(valid, m, s)

# class Lambda(nn.Module):
    # def __init__(self, func):
        # super().__init__()
        # self.func = func

    # def forward(self, x):
        # return self.func(x)

# def flatten(x):
    # return x.view(x.shape[0], -1)

# class Flatten(nn.Module):
    # def forward(self, x):
        # return x.view(x.size(0), -1)

# def lin_comb(v1, v2, beta): return beta*v1 + (1-beta)*v2

def unsqueeze(input, dims):
    for dim in listify(dims): input = torch.unsqueeze(input, dim)
    return input

def reduce_loss(loss, reduction='mean'):
    return loss.mean() if reduction == 'mean' else \
           loss.sum() if reduction == 'sum' else \
           loss

def set_grad(model, boolean_value):
    "(de)activates gradient for layers in model if not linear or batchnorm"
    if isinstance(model, (nn.Linear, nn.BatchNorm1d)):
        return
    if hasattr(model, 'weight'):
        for param in model.parameters():
            param.requires_grad_(boolean_value)

# def apply_mod(model, func):
    # "applies func to layers in model recursively"
    # func(model)
    # for child in model.children():
        # apply_mod(child, func)

# example usage:
# apply_mod(learn.model, partial(set_grad, boolean_value=False))

# but pytorch already has a version of apply_mod:
# learn.model.apply(partial(set_grad, boolean_value=False))
