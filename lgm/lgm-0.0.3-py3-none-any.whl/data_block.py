import html
import os
import re
import spacy
import torch
from collections import defaultdict, Counter, OrderedDict
from concurrent.futures import ProcessPoolExecutor
from fastprogress import progress_bar
# from functools import partial
from pathlib import Path
from spacy.symbols import ORTH
from torch import tensor, LongTensor
from torch.utils.data import Sampler, Dataset, DataLoader
from .utils import compose, listify, read_file, sched_exp, get_files


# general data block utility functions

def parent_labeler(fn): return fn.parent.name

def get_dls(train_ds, valid_ds, bs, **kwargs):
    return (DataLoader(train_ds, batch_size=bs, shuffle=True, **kwargs),
            DataLoader(valid_ds, batch_size=bs*2, **kwargs))

def grandparent_splitter(fn, valid_name='valid', train_name='train'):
    gp = fn.parent.parent.name
    return True if gp==valid_name else False if gp==train_name else None

def split_by_func(items, f):
    mask = [f(item) for item in items]
    # `None` values will be filtered out
    false_items = [item for item, m in zip(items, mask) if m==False]
    true_items = [item for item, m in zip(items, mask) if m==True]
    return false_items, true_items

def label_by_func(sd, f, proc_x=None, proc_y=None):
    train = LabeledData.label_by_func(sd.train, f, proc_x=proc_x, proc_y=proc_y)
    valid = LabeledData.label_by_func(sd.valid, f, proc_x=proc_x, proc_y=proc_y)
    return SplitData(train,valid)

def parallel(func, arr, max_workers=16):
    if max_workers<2:
        results = list(progress_bar(map(func, enumerate(arr)), total=len(arr)))
    else:
        with ProcessPoolExecutor(max_workers=max_workers) as ex:
            return list(progress_bar(ex.map(func, enumerate(arr)), total=len(arr)))
    if any([res is not None for res in results]):
        return results

def uniqueify(x, sort=False):
    res = list(OrderedDict.fromkeys(x).keys())
    if sort: res.sort()
    return res

# utility functions for text

#special tokens
UNK, PAD, BOS, EOS, TK_REP, TK_WREP, TK_UP, TK_MAJ = "xxunk xxpad xxbos xxeos xxrep xxwrep xxup xxmaj".split()

def sub_br(t):
    "Replaces the <br /> by \n"
    re_br = re.compile(r'<\s*br\s*/?>', re.IGNORECASE)
    return re_br.sub("\n", t)

def spec_add_spaces(t):
    "Add spaces around / and #"
    return re.sub(r'([/#])', r' \1 ', t)

def rm_useless_spaces(t):
    "Remove multiple spaces"
    return re.sub(' {2,}', ' ', t)

def replace_rep(t):
    "Replace repetitions at the character level: cccc -> TK_REP 4 c"
    def _replace_rep(m):
        c,cc = m.groups()
        return f' {TK_REP} {len(cc)+1} {c} '
    re_rep = re.compile(r'(\S)(\1{3,})')
    return re_rep.sub(_replace_rep, t)

def replace_wrep(t):
    "Replace word repetitions: word word word -> TK_WREP 3 word"
    def _replace_wrep(m):
        c,cc = m.groups()
        return f' {TK_WREP} {len(cc.split())+1} {c} '
    re_wrep = re.compile(r'(\b\w+\W+)(\1{3,})')
    return re_wrep.sub(_replace_wrep, t)

def fixup_text(x):
    "Various messy things we've seen in documents"
    re1 = re.compile(r'  +')
    x = x.replace('#39;', "'").replace('amp;', '&').replace('#146;', "'").replace(
        'nbsp;', ' ').replace('#36;', '$').replace('\\n', "\n").replace('quot;', "'").replace(
        '<br />', "\n").replace('\\"', '"').replace('<unk>',UNK).replace(' @.@ ','.').replace(
        ' @-@ ','-').replace('\\', ' \\ ')
    return re1.sub(' ', html.unescape(x))

default_pre_rules = [fixup_text, replace_rep, replace_wrep, spec_add_spaces, rm_useless_spaces, sub_br]
default_spec_tok = [UNK, PAD, BOS, EOS, TK_REP, TK_WREP, TK_UP, TK_MAJ]

def replace_all_caps(x):
    "Replace tokens in ALL CAPS by their lower version and add `TK_UP` before."
    res = []
    for t in x:
        if t.isupper() and len(t) > 1: res.append(TK_UP); res.append(t.lower())
        else: res.append(t)
    return res

def deal_caps(x):
    "Replace all Capitalized tokens in by their lower version and add `TK_MAJ` before."
    res = []
    for t in x:
        if t == '': continue
        if t[0].isupper() and len(t) > 1 and t[1:].islower(): res.append(TK_MAJ)
        res.append(t.lower())
    return res

def add_eos_bos(x): return [BOS] + x + [EOS]

default_post_rules = [deal_caps, replace_all_caps, add_eos_bos]

def get_lm_dls(train_ds, valid_ds, bs, bptt, **kwargs):
    return (DataLoader(LM_PreLoader(train_ds, bs, bptt, shuffle=True), batch_size=bs, **kwargs),
            DataLoader(LM_PreLoader(valid_ds, bs, bptt, shuffle=False), batch_size=2*bs, **kwargs))

def lm_databunchify(sd, bs, bptt, **kwargs):
    return DataBunch(*get_lm_dls(sd.train, sd.valid, bs, bptt, **kwargs))

def pad_collate(samples, pad_idx=1, pad_first=False):
    # identify the longest document in the minibatch
    max_len = max([len(s[0]) for s in samples])
    # create rectangular tensor that can accommodate all documents
    # in the batch up to that max_len, and fill it with padding.
    res = torch.zeros(len(samples), max_len).long() + pad_idx
    # take documents in the minibatch and put them in the tensor
    # keeping padding either at the beginning or at the end
    for i,s in enumerate(samples):
        if pad_first: res[i, -len(s[0]):] = LongTensor(s[0])
        else:         res[i, :len(s[0]) ] = LongTensor(s[0])
    return res, tensor([s[1] for s in samples])

def get_clas_dls(train_ds, valid_ds, bs, **kwargs):
    train_sampler = SortishSampler(train_ds.x, key=lambda t: len(train_ds.x[t]), bs=bs)
    valid_sampler = SortSampler(valid_ds.x, key=lambda t: len(valid_ds.x[t]))
    return (DataLoader(train_ds, batch_size=bs, sampler=train_sampler, collate_fn=pad_collate, **kwargs),
            DataLoader(valid_ds, batch_size=bs*2, sampler=valid_sampler, collate_fn=pad_collate, **kwargs))

def clas_databunchify(sd, bs, **kwargs):
    return DataBunch(*get_clas_dls(sd.train, sd.valid, bs, **kwargs))


# classes

class DatasetBundle(Dataset):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y

    def __len__(self):
        return len(self.x)

    def __getitem__(self, i):
        return self.x[i], self.y[i]

class DataBunch():
    def __init__(self, train_dl, valid_dl, c_in=None, c_out=None):
        self.train_dl = train_dl
        self.valid_dl = valid_dl
        self.c_in = c_in
        self.c_out = c_out

    @property
    def train_ds(self): return self.train_dl.dataset

    @property
    def valid_ds(self): return self.valid_dl.dataset

class ListContainer():
    def __init__(self, items):
        self.items = listify(items)

    def __getitem__(self, idx):
        try: return self.items[idx]
        except TypeError:
            if isinstance(idx[0],bool):
                assert len(idx)==len(self) # bool mask
                return [o for m,o in zip(idx,self.items) if m]
            return [self.items[i] for i in idx]

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        return iter(self.items)

    def __setitem__(self, i, o):
        self.items[i] = o

    def __delitem__(self, i):
        del(self.items[i])

    def __repr__(self):
        res = f'{self.__class__.__name__} ({len(self)} items)\n{self.items[:10]}'
        if len(self)>10:
            res = res[:-1]+ '...]'
        return res

class ItemList(ListContainer):
    def __init__(self, items, path='.', tfms=None):
        super().__init__(items)
        self.path,self.tfms = Path(path),tfms

    def __repr__(self): return f'{super().__repr__()}\nPath: {self.path}'

    def new(self, items, cls=None):
        if cls is None:
            cls=self.__class__
        return cls(items, self.path, tfms=self.tfms)

    def  get(self, i): return i
    def _get(self, i): return compose(self.get(i), self.tfms)

    def __getitem__(self, idx):
        res = super().__getitem__(idx)
        if isinstance(res,list): return [self._get(o) for o in res]
        return self._get(res)

class SplitData():
    def __init__(self, train, valid):
        self.train = train
        self.valid = valid

    def __getattr__(self,k):
        return getattr(self.train,k)

    # this is needed if we want to pickle SplitData and
    # load it back without recursion errors
    def __setstate__(self,data):
        self.__dict__.update(data)

    @classmethod
    def split_by_func(cls, il, f):
        lists = map(il.new, split_by_func(il.items, f))
        return cls(*lists)

    def __repr__(self):
        return f'{self.__class__.__name__}\nTrain: {self.train}\nValid: {self.valid}\n'

class Processor():
    def process(self, items):
        return items

class CategoryProcessor(Processor):
    def __init__(self):
        self.vocab = None

    def __call__(self, items):
        #The vocab is defined on the first use.
        if self.vocab is None:
            self.vocab = uniqueify(items)
            self.otoi  = {v:k for k,v in enumerate(self.vocab)}
        return [self.proc1(item) for item in items]

    def proc1(self, item):
        return self.otoi[item]

    def deprocess(self, idxs):
        assert self.vocab is not None
        return [self.deproc1(idx) for idx in idxs]

    def deproc1(self, idx):
        return self.vocab[idx]


def _label_by_func(ds, f, cls=ItemList):
    return cls([f(o) for o in ds.items], path=ds.path)

class LabeledData():
    def process(self, il, proc):
        return il.new(compose(il.items, proc))

    def __init__(self, x, y, proc_x=None, proc_y=None):
        self.x,self.y = self.process(x, proc_x),self.process(y, proc_y)
        self.proc_x,self.proc_y = proc_x,proc_y

    def __repr__(self):
        return f'{self.__class__.__name__}\nx: {self.x}\ny: {self.y}\n'
    def __getitem__(self,idx):
        return self.x[idx],self.y[idx]
    def __len__(self):
        return len(self.x)

    def x_obj(self, idx):
        return self.obj(self.x, idx, self.proc_x)
    def y_obj(self, idx):
        return self.obj(self.y, idx, self.proc_y)

    def obj(self, items, idx, procs):
        isint = isinstance(idx, int) or (isinstance(idx,torch.LongTensor) and not idx.ndim)
        item = items[idx]
        for proc in reversed(listify(procs)):
            item = proc.deproc1(item) if isint else proc.deprocess(item)
        return item

    @classmethod
    def label_by_func(cls, il, f, proc_x=None, proc_y=None):
        return cls(il, _label_by_func(il, f), proc_x=proc_x, proc_y=proc_y)

class TextList(ItemList):
    @classmethod
    def from_files(cls, path, extensions='.txt',
                   recurse=True, include=None, **kwargs):
        return cls(get_files(path, extensions, recurse=recurse, include=include),
                   path, **kwargs)

    def get(self, i):
        if isinstance(i, Path):
            return read_file(i)
        return i

class TokenizeProcessor(Processor):
    def __init__(self, lang="en", chunksize=2000, pre_rules=None,
                 post_rules=None, max_workers=16):
        self.chunksize = chunksize
        self.max_workers = max_workers
        self.tokenizer = spacy.blank(lang).tokenizer
        for w in default_spec_tok:
            self.tokenizer.add_special_case(w, [{ORTH: w}])
        self.pre_rules  = default_pre_rules  if pre_rules  is None else pre_rules
        self.post_rules = default_post_rules if post_rules is None else post_rules

    def proc_chunk(self, args):
        i,chunk = args
        chunk = [compose(t, self.pre_rules) for t in chunk]
        docs = [[d.text for d in doc] for doc in self.tokenizer.pipe(chunk)]
        docs = [compose(t, self.post_rules) for t in docs]
        return docs

    def __call__(self, items):
        toks = []
        if isinstance(items[0], Path):
            items = [read_file(i) for i in items]
        chunks = [items[i: i+self.chunksize]
                  for i in (range(0, len(items), self.chunksize))]
        toks = parallel(self.proc_chunk, chunks, max_workers=self.max_workers)
        return sum(toks, [])

    def proc1(self, item):
        return self.proc_chunk([toks])[0]

    def deprocess(self, toks):
        return [self.deproc1(tok) for tok in toks]

    def deproc1(self, tok):
        return " ".join(tok)

class NumericalizeProcessor(Processor):
    def __init__(self, vocab=None, max_vocab=60000, min_freq=2):
        self.vocab = vocab
        self.max_vocab = max_vocab
        self.min_freq = min_freq

    def __call__(self, items):
        #The vocab is defined on the first use.
        if self.vocab is None:
            freq = Counter(p for o in items for p in o)
            self.vocab = [o for o,c in freq.most_common(self.max_vocab)
                          if c >= self.min_freq]
            for o in reversed(default_spec_tok):
                if o in self.vocab: self.vocab.remove(o)
                self.vocab.insert(0, o)
        if getattr(self, 'otoi', None) is None:
            self.otoi = defaultdict(int,{v:k for k,v in enumerate(self.vocab)})
        return [self.proc1(o) for o in items]

    def proc1(self, item):
        return [self.otoi[o] for o in item]

    def deprocess(self, idxs):
        assert self.vocab is not None
        return [self.deproc1(idx) for idx in idxs]

    def deproc1(self, idx):
        return [self.vocab[i] for i in idx]

class LM_PreLoader():
    """
    Creates independent and dependent variables for language models.
    In __getitem__, the dependent variable is the indep. var. sequence
    shifted by 1:
    -- indep. var.: source[seq_idx:seq_idx+self.bptt]
    -- dep. var.: source[seq_idx+1:seq_idx+self.bptt+1]
    """
    def __init__(self, data, bs=64, bptt=70, shuffle=False):
        self.data = data
        self.bs = bs
        self.bptt = bptt
        self.shuffle = shuffle
        total_len = sum([len(t) for t in data.x])
        self.n_batch = total_len // bs
        self.batchify()

    def __len__(self):
        return ((self.n_batch-1) // self.bptt) * self.bs

    def __getitem__(self, idx):
        source = self.batched_data[idx % self.bs]
        seq_idx = (idx // self.bs) * self.bptt
        return source[seq_idx:seq_idx+self.bptt], source[seq_idx+1:seq_idx+self.bptt+1]

    def batchify(self):
        texts = self.data.x
        if self.shuffle:
            texts = texts[torch.randperm(len(texts))]
        stream = torch.cat([tensor(t) for t in texts])
        self.batched_data = stream[:self.n_batch * self.bs].view(self.bs, self.n_batch)

class SortSampler(Sampler):
    """
    This looks at all the documents in data_source and sorts them in reverse
    order according to the key that's passed in.
    Example usage:
    See SortishSampler below.
    SortSampler is used for validation, ordering documents deterministically in
    reverse order of length. SortishSampler should be used for training.
    """
    def __init__(self, data_source, key):
        self.data_source = data_source
        self.key = key

    def __len__(self):
        return len(self.data_source)

    def __iter__(self):
        return iter(sorted(list(range(len(self.data_source))),
                           key=self.key, reverse=True))

class SortishSampler(Sampler):
    """
    Sampler that sorts the documents in reverse order with some random
    shuffling. Every batch has documents of a similar length, but with some
    randomness.
    We create random megabatches (50 times bigger than batch size (bs)) and
    sort each of them in reverse order of length.
    Example usage, sorting on the length of the documents:
    SortishSampler(ll.train.x, key=lambda t: len(ll.train[int(t)][0]), bs=bs)
    """
    def __init__(self, data_source, key, bs):
        self.data_source,self.key,self.bs = data_source,key,bs

    def __len__(self) -> int: return len(self.data_source)

    def __iter__(self):
        idxs = torch.randperm(len(self.data_source))
        megabatches = [idxs[i:i+self.bs*50] for i in range(0, len(idxs), self.bs*50)]
        sorted_idx = torch.cat([tensor(sorted(s, key=self.key, reverse=True)) for s in megabatches])
        batches = [sorted_idx[i:i+self.bs] for i in range(0, len(sorted_idx), self.bs)]
        # find the chunk with the largest key
        max_idx = torch.argmax(tensor([self.key(ck[0]) for ck in batches]))
        # then make sure it goes first
        batches[0], batches[max_idx] = batches[max_idx], batches[0]
        batch_idxs = torch.randperm(len(batches)-2)
        sorted_idx = torch.cat([batches[i+1] for i in batch_idxs]) if len(batches) > 1 else LongTensor([])
        sorted_idx = torch.cat([batches[0], sorted_idx, batches[-1]])
        return iter(sorted_idx)

