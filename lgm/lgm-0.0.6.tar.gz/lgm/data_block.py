import html
import os
import numpy as np
import re
import spacy
import torch
from collections import defaultdict, Counter
from concurrent.futures import ProcessPoolExecutor
from fastprogress import progress_bar
# from functools import partial
from pathlib import Path
from spacy.symbols import ORTH
from torch import tensor, LongTensor
from torch.utils.data import Sampler, Dataset, DataLoader
from .utils import compose, listify, uniqueify, read_file, sched_exp, get_files, df_names_to_idx


# general data block utility functions

def parent_labeler(filename):
    return filename.parent.name

def get_dls(train_ds, valid_ds, batch_size, **kwargs):
    return (DataLoader(train_ds, batch_size=batch_size, shuffle=True, **kwargs),
            DataLoader(valid_ds, batch_size=batch_size*2, **kwargs))

def grandparent_splitter(filename, valid_name='valid', train_name='train'):
    grandparent = filename.parent.parent.name
    return True if grandparent==valid_name else \
           False if grandparent==train_name else \
           None

def split_by_func(items, f):
    mask = [f(item) for item in items]
    # `None` values will be filtered out
    false_items = [item for item, m in zip(items, mask) if m==False]
    true_items = [item for item, m in zip(items, mask) if m==True]
    return false_items, true_items

def label_by_func(splitdata, func, processor_x=None, processor_y=None):
    train = LabeledData.label_by_func(splitdata.train, func,
                                      processor_x=processor_x, processor_y=processor_y)
    valid = LabeledData.label_by_func(splitdata.valid, func,
                                      processor_x=processor_x, processor_y=processor_y)
    return SplitData(train, valid)

def parallel(func, arr, max_workers=16):
    if max_workers < 2:
        results = list(progress_bar(map(func, enumerate(arr)), total=len(arr)))
    else:
        with ProcessPoolExecutor(max_workers=max_workers) as ex:
            return list(progress_bar(ex.map(func, enumerate(arr)), total=len(arr)))
    if any([result is not None for result in results]):
        return results

# utility functions for text

#special tokens
UNK, PAD, BOS, EOS, TK_REP, TK_WREP, TK_ALLCAPS, TK_CAP = "_UNK_ _PAD_ _BOS_ _EOS_ _REP_ _WREP_ _ALLCAPS_ _CAP_".split()
default_spec_tok = [UNK, PAD, BOS, EOS, TK_REP, TK_WREP, TK_ALLCAPS, TK_CAP]

def sub_br(text):
    "Replaces the <br /> by \n"
    re_br = re.compile(r'<\s*br\s*/?>', re.IGNORECASE)
    return re_br.sub("\n", text)

def spec_add_spaces(text):
    "Add spaces around / and #"
    return re.sub(r'([/#])', r' \1 ', text)

def rm_useless_spaces(text):
    "Remove multiple spaces"
    return re.sub(' {2,}', ' ', text)

def replace_rep(text):
    "Replace repetitions at the character level: cccc -> TK_REP 4 c"
    def _replace_rep(match):
        character, characters = match.groups()
        return f' {TK_REP} {len(characters)+1} {character} '
    re_rep = re.compile(r'(\S)(\1{3,})')
    return re_rep.sub(_replace_rep, text)

def replace_wrep(text):
    "Replace word repetitions: word word word -> TK_WREP 3 word"
    def _replace_wrep(match):
        word, words = match.groups()
        return f' {TK_WREP} {len(words.split())+1} {word} '
    re_wrep = re.compile(r'(\b\w+\W+)(\1{3,})')
    return re_wrep.sub(_replace_wrep, text)

def fixup_text(text):
    "Various messy things we've seen in documents"
    re1 = re.compile(r'  +')
    text = text.replace('#39;', "'").replace('amp;', '&').replace('#146;', "'").replace(
        'nbsp;', ' ').replace('#36;', '$').replace('\\n', "\n").replace('quot;', "'").replace(
        '<br />', "\n").replace('\\"', '"').replace('<unk>',UNK).replace(' @.@ ','.').replace(
        ' @-@ ','-').replace('\\', ' \\ ')
    return re1.sub(' ', html.unescape(text))

# rules to apply before tokenization
default_pre_rules = [fixup_text, replace_rep, replace_wrep, spec_add_spaces, rm_useless_spaces, sub_br]

def replace_all_caps(text):
    "Replace tokens in ALL CAPS by their lower version and add `TK_ALLCAPS` before."
    results = []
    for token in text:
        if token not in default_spec_tok and token.isupper() and len(token) > 1:
            results.append(TK_ALLCAPS); results.append(token.lower())
        else: results.append(token)
    return results

def replace_caps(text):
    "Replace all Capitalized tokens in by their lower version and add `TK_CAP` before."
    results = []
    for token in text:
        if token == '':
            continue
        if token not in default_spec_tok and token[0].isupper() and len(token) > 1 and token[1:].islower():
            results.append(TK_CAP)
        results.append(token.lower())
    return results

def add_eos_bos(text):
    "adds 'beginning of string' and 'end of string' tokens"
    # return [BOS] + text + [EOS]
    return [BOS] + text # adding only BOS; EOS seems redundant

# rules to apply after tokenization
default_post_rules = [replace_caps, replace_all_caps, add_eos_bos]

def get_lm_dls(train_ds, valid_ds, batch_size, bptt, **kwargs):
    return (DataLoader(LM_PreLoader(train_ds, batch_size, bptt, shuffle=True),
                       batch_size=batch_size, **kwargs),
            DataLoader(LM_PreLoader(valid_ds, batch_size, bptt, shuffle=False),
                       batch_size=2*batch_size, **kwargs))

def lm_databunchify(splitdata, batch_size, bptt, **kwargs):
    return DataBunch(*get_lm_dls(splitdata.train, splitdata.valid, batch_size, bptt, **kwargs))

def pad_collate(samples, pad_idx=1, pad_first=False):
    # identify the longest document in the minibatch
    max_len = max([len(sample[0]) for sample in samples])
    # create rectangular tensor that can accommodate all documents
    # in the batch up to that max_len, and fill it with padding.
    results = torch.zeros(len(samples), max_len).long() + pad_idx
    # take documents in the minibatch and put them in the tensor
    # keeping padding either at the beginning or at the end
    for i, sample in enumerate(samples):
        if pad_first:
            results[i, -len(sample[0]):] = LongTensor(sample[0])
        else:
            results[i, :len(sample[0]) ] = LongTensor(sample[0])
    return results, tensor([sample[1] for sample in samples])

def get_clas_dls(train_ds, valid_ds, batch_size, **kwargs):
    train_sampler = SortishSampler(train_ds.x,
                                   key=lambda t: len(train_ds.x[t]),
                                   batch_size=batch_size)
    valid_sampler = SortSampler(valid_ds.x,
                                key=lambda t: len(valid_ds.x[t]))
    return (DataLoader(train_ds, batch_size=batch_size, sampler=train_sampler,
                       collate_fn=pad_collate, **kwargs),
            DataLoader(valid_ds, batch_size=batch_size*2, sampler=valid_sampler,
                       collate_fn=pad_collate, **kwargs))

def clas_databunchify(splitdata, batch_size, **kwargs):
    return DataBunch(*get_clas_dls(splitdata.train, splitdata.valid, batch_size, **kwargs))


# classes

class DataBunch():
    """
    Bunches together a train dataloader and a validation dataloader.
    """
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
    """
    Base class for indepedents and dependent variables (vectors of observations).
    """
    def __init__(self, items):
        self.items = listify(items)

    def __getitem__(self, idx):
        try:
            return self.items[idx]
        except TypeError:
            if isinstance(idx[0], bool):
                # check that the idx are a boolean mask
                assert len(idx) == len(self)
                return [item for mask, item in zip(idx, self.items) if mask]
            return [self.items[i] for i in idx]

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        return iter(self.items)

    def __setitem__(self, i, o):
        self.items[i] = o

    def __delitem__(self, i):
        del(self.items[i])

    def __repr__(self, n=3):
        results = f'{self.__class__.__name__} ({len(self)} items)\n[{", ".join(str(self.items[i]) for i in range(n))}]'
        if len(self) > n:
            results = results[:-1] + ', ...]'
        return results

class ItemList(ListContainer):
    def __init__(self, items, path='.', transforms=None):
        super().__init__(items)
        self.path = Path(path)
        self.transforms = transforms

    def __repr__(self):
        return f'{super().__repr__()}\nPath: {self.path}'

    def new(self, items, cls=None):
        if cls is None:
            cls=self.__class__
        return cls(items, self.path, transforms=self.transforms)

    def  get(self, i):
        return i

    def _get(self, i):
        return compose(self.get(i), self.transforms)

    def __getitem__(self, idx):
        results = super().__getitem__(idx)
        if isinstance(results, list):
            return [self._get(result) for result in results]
        return self._get(results)

class TextList(ItemList):
    @classmethod
    def from_files(cls, path, extensions='.txt',
                   recurse=True, include=None, **kwargs):
        return cls(get_files(path, extensions, recurse=recurse, include=include),
                   path, **kwargs)

    @classmethod
    def from_df(cls, path, df, col_names, **kwargs):
        "Create an ItemList in path from the inputs in the col_names of df."
        cols = df.iloc[:, df_names_to_idx(col_names, df)]
        assert not cols.isna().any().any(), f"You have NaN values in column(s) {col_names} of your dataframe, please fix it."
        return cls(_maybe_squeeze(cols.values), path, **kwargs)

    def get(self, i):
        if isinstance(i, Path):
            return read_file(i)
        return i

class SplitData():
    def __init__(self, train, valid):
        self.train = train
        self.valid = valid

    def __getattr__(self, k):
        return getattr(self.train, k)

    # this is needed if we want to pickle SplitData and
    # load it back without recursion errors
    def __setstate__(self, data):
        self.__dict__.update(data)

    @classmethod
    def split_by_func(cls, itemlist, func):
        """
        creates a SplitData object by splitting an itemlist intro a train and
        validation set using func, then feeding the 2 sets into SplitData
        """
        lists = map(itemlist.new, split_by_func(itemlist.items, func))
        return cls(*lists)

    def __repr__(self):
        return f'{self.__class__.__name__}\nTrain: {self.train}\nValid: {self.valid}\n'

def _label_by_func(dataset, func, cls=ItemList):
    return cls([func(item) for item in dataset.items], path=dataset.path)

def _label_from_list(dataset, labels, cls=ItemList):
    labels = listify(labels)
    return cls(labels, path=dataset.path)

class LabeledData():
    """
    Associates an itemlist x (the independent variable)
    with an itemlist y of labels (the dependent variable).
    Assumes x and y are itemlists.
    """
    def __init__(self, x, y, processor_x=None, processor_y=None):
        self.x = self.process(x, processor_x)
        self.y = self.process(y, processor_y)
        self.processor_x = processor_x
        self.processor_y = processor_y

    def __repr__(self):
        return f'{self.__class__.__name__}\nx: {self.x}\ny: {self.y}\n'

    def __getitem__(self,idx):
        return self.x[idx], self.y[idx]

    def __len__(self):
        return len(self.x)

    def process(self, itemlist, processor):
        return itemlist.new(compose(itemlist.items, processor))

    def obj(self, items, idx, processors):
        isint = isinstance(idx, int) or \
                (isinstance(idx, torch.LongTensor) and not idx.ndim)
        item = items[idx]
        for processor in reversed(listify(processors)):
            item = processor.deprocess_one(item) if isint else processor.deprocess(item)
        return item

    def x_obj(self, idx):
        return self.obj(self.x, idx, self.processor_x)

    def y_obj(self, idx):
        return self.obj(self.y, idx, self.processor_y)

    @classmethod
    def label_by_func(cls, itemlist, func, processor_x=None, processor_y=None):
        return cls(itemlist, _label_by_func(itemlist, func),
                   processor_x=processor_x, processor_y=processor_y)

    @classmethod
    def label_from_df(cls, itemlist, df, col_names, processor_x=None, processor_y=None):
        labels = df.iloc[:, df_names_to_idx(col_names, df)]
        assert labels.isna().sum().sum() == 0, f"You have NaN values in column(s) {cols} of your dataframe, please fix it."
        return cls(itemlist, _label_from_list(itemlist, _maybe_squeeze(labels)),
                   processor_x=processor_x, processor_y=processor_y)

class Processor():
    def process(self, items):
        return items

class CategoryProcessor(Processor):
    """
    Converts a factor (vector of categorical levels) to an int-based vector.
    """
    def __init__(self):
        self.level_dict = None

    def __call__(self, items):
        # The level_dict which contains all the levels of the factor
        # is defined on the first use.
        if self.level_dict is None:
            self.level_dict = uniqueify(items)
            self.otoi = {level:idx for idx,level in enumerate(self.level_dict)}
        return [self.process_one(item) for item in items]

    def process_one(self, item):
        "process one item"
        return self.otoi[item]

    def deprocess(self, idxs):
        assert self.level_dict is not None
        return [self.deprocess_one(idx) for idx in idxs]

    def deprocess_one(self, idx):
        "deprocess one index"
        return self.level_dict[idx]

class TokenizeProcessor(Processor):
    def __init__(self, lang="en", chunksize=2000, pre_rules=None,
                 post_rules=None, max_workers=8):
        self.chunksize = chunksize
        self.max_workers = max_workers
        self.tokenizer = spacy.blank(lang).tokenizer
        for word in default_spec_tok:
            self.tokenizer.add_special_case(word, [{ORTH: word}])
        self.pre_rules = default_pre_rules if pre_rules is None else pre_rules
        self.post_rules = default_post_rules if post_rules is None else post_rules

    def process(self, chunk):
        i, chunk = chunk # needed because parallel has an enumerate inside
        chunk = [compose(text, self.pre_rules) for text in chunk]
        texts = [[d.text for d in doc] for doc in self.tokenizer.pipe(chunk)]
        texts = [compose(text, self.post_rules) for text in texts]
        return texts

    def __call__(self, items):
        toks = []
        if isinstance(items[0], Path):
            items = [read_file(i) for i in items]
        chunks = [items[i: i+self.chunksize]
                  for i in (range(0, len(items), self.chunksize))]
        toks = parallel(self.process, chunks, max_workers=self.max_workers)
        return sum(toks, [])

    def deprocess(self, toks):
        return [self.deprocess_one(tok) for tok in toks]

    def deprocess_one(self, tok):
        "deprocess one index"
        return " ".join(tok)

class NumericalizeProcessor(Processor):
    def __init__(self, vocab=None, max_vocab=60000, min_freq=2):
        self.vocab = vocab
        self.max_vocab = max_vocab
        self.min_freq = min_freq

    def __call__(self, texts):
        #The vocab is defined on the first use.
        if self.vocab is None:
            freq = Counter(word for text in texts for word in text)
            self.vocab = [word for word,frequency in freq.most_common(self.max_vocab) \
                          if frequency >= self.min_freq]
            for word in reversed(default_spec_tok):
                if word in self.vocab:
                    self.vocab.remove(word)
                self.vocab.insert(0, word)
        if getattr(self, 'otoi', None) is None:
            self.otoi = defaultdict(int, {v:k for k,v in enumerate(self.vocab)})
        return [self.process_one(word) for word in texts]

    def process_one(self, text):
        "process one text"
        return [self.otoi[word] for word in text]

    def deprocess(self, idxs):
        assert self.vocab is not None
        return [self.deprocess_one(idx) for idx in idxs]

    def deprocess_one(self, idx):
        "deprocess one index"
        if isinstance(idx, list):
            return [self.vocab[i] for i in idx]
        return self.vocab[idx]

class LM_PreLoader():
    """
    Creates independent and dependent variables for language models.
    Assumes the data coming in is LabeledData with the texts stored
    in the independent variable slot x.
    We concatenate all texts in a stream, then break it into batch_size
    many texts, which are contiguous pieces of text of length text_len.
    We generate x and y labels (text to be ingested, and to be predicted)
    by tiling every text with adjacent, non-overlapping windows that are
    bptt wide, i.e., have bptt many words in them.
    The sequence of words in each bptt-wide window is the independent variable,
    and the dependent variable is the indep. var. sequence shifted by 1 word.
    See __getitem__ below, where:
    -- indep. var. (text to ingested): text[seq_idx:seq_idx+self.bptt]
    -- dep. var. (text to be predicted): text[seq_idx+1:seq_idx+self.bptt+1]
    """
    def __init__(self, data, batch_size=64, bptt=70, shuffle=False):
        self.data = data
        # batch_size: number of data points (bptt-wide windows of words) per batch
        self.batch_size = batch_size
        # back-propagation through time (bptt), that is, the length of
        # the ingested sequence of words before we predict next word
        self.bptt = bptt
        self.shuffle = shuffle
        # total length of concatenated text in words
        total_len = sum([len(text) for text in data.x])
        # we will break the concatenated text into batch_size
        # contiguous pieces of text, each of which will have length text_len
        self.text_len = total_len // batch_size
        self.batchify()

    def __len__(self):
        """
        We obtain total length by calculating length per text first.
        Each text has text_len words, and we need to count how many adjacent,
        non-overlapping bptt-wide windows we can tile the text with.
        Specifically, we need to tile text_len - 1 words only, because that
        final word can only be part of the dependent variable (it can only be
        predicted, not ingested).
        Once we have the length of a text, which is (self.text_len-1) // self.bptt,
        that is, the number of bptt-wide tiles, we multiply by batch_size, which
        is the number of indepedent bptt windows we'll have in a batch.
        """
        return ((self.text_len-1) // self.bptt) * self.batch_size

    def __getitem__(self, idx):
        """
        idx is an index limited to the total length of the dataset, given by
        __len__ above. Recall that each data point in the dataset consists of
        a bptt-wide window of words that we tiled the text with.
        When we index into the dataset with the index idx, we need to retrieve
        a bptt window of words (text to be ingested), paired with that same
        window shifted by 1 word to the right.


        To see what how the indexation works with a simple example, create a dataset
        of total length 120, set batch_size to 10 and break it into batch_size contiguous
        sequences:

        x = list(range(1, 121))
        batch_size = 10
        x = torch.tensor(x).view(batch_size, -1)

        The dataset x is now:

        tensor([[  1,   2,   3,   4,   5,   6,   7,   8,   9,  10,  11,  12],
                [ 13,  14,  15,  16,  17,  18,  19,  20,  21,  22,  23,  24],
                [ 25,  26,  27,  28,  29,  30,  31,  32,  33,  34,  35,  36],
                [ 37,  38,  39,  40,  41,  42,  43,  44,  45,  46,  47,  48],
                [ 49,  50,  51,  52,  53,  54,  55,  56,  57,  58,  59,  60],
                [ 61,  62,  63,  64,  65,  66,  67,  68,  69,  70,  71,  72],
                [ 73,  74,  75,  76,  77,  78,  79,  80,  81,  82,  83,  84],
                [ 85,  86,  87,  88,  89,  90,  91,  92,  93,  94,  95,  96],
                [ 97,  98,  99, 100, 101, 102, 103, 104, 105, 106, 107, 108],
                [109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120]])

        Now assume a bptt window of 3. Suppose we want to find the datapoint,
        that is, the 3-word-wide window, at index 23:

        bptt = 3
        idx = 23

        To get the text in that window, we first find the continuous piece of text:

        text = x[idx % batch_size]

        The text is:

        tensor([37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48])

        Then, we find the first word in that text that has not been consumed yet:

        seq_idx = (idx // batch_size) * bptt

        This is word number 6. So the two tensors we return are:

        text[seq_idx:seq_idx+bptt]
        text[seq_idx+1:seq_idx+bptt+1]

        Namely:
         -- tensor([43, 44, 45]) -- window to be ingested
         -- tensor([44, 45, 46]) -- window containing the prediction (the last word)
        """
        # We consume bptt windows from the dataset in batches of batch_size. So,
        # to identify the piece of contiguous text associated with the bptt window
        # at the index idx, we take the remainder idx % self.batch_size, then we
        # get the text that the current bptt window comes from
        text = self.batched_data[idx % self.batch_size]

        # Now we need to find out how much of this contiguous text
        # we already consumed by the time we got to the bptt window at index idx.
        # To find this, we need to compute the number of complete batches we went
        # through up to this point, which is idx // self.batch_size.
        # In each of those batches, we consumed one bptt-wide window of words from
        # the contiguous text, so the total number of consumed words is
        # number of complete batches (idx // self.batch_size) multiplied by bptt.
        seq_idx = (idx // self.batch_size) * self.bptt

        # we now have the bptt window to be ingested, and the window to be predicted
        return text[seq_idx:seq_idx+self.bptt], text[seq_idx+1:seq_idx+self.bptt+1]

    def batchify(self):
        texts = self.data.x
        if self.shuffle:
            texts = texts[torch.randperm(len(texts))]
        stream = torch.cat([tensor(text) for text in texts])
        # each column is a batch that has batch_size words
        # every row is a contiguous piece of text of length text_len
        self.batched_data = stream[:self.text_len * self.batch_size].view(self.batch_size, self.text_len)

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
    We create random megabatches (50 times bigger than batch_size) and
    sort each of them in reverse order of length.
    Example usage, sorting on the length of the documents:
    SortishSampler(ll.train.x,
                   key=lambda t: len(ll.train[int(t)][0]),
                   batch_size=batch_size)
    """
    def __init__(self, data_source, key, batch_size):
        self.data_source = data_source
        self.key = key
        self.batch_size = batch_size

    def __len__(self):
        return len(self.data_source)

    def __iter__(self):
        idxs = torch.randperm(len(self.data_source))
        megabatches = [idxs[i:i+self.batch_size*50] for i in range(0, len(idxs), self.batch_size*50)]
        sorted_idx = torch.cat([tensor(sorted(s, key=self.key, reverse=True)) for s in megabatches])
        batches = [sorted_idx[i:i+self.batch_size] for i in range(0, len(sorted_idx), self.batch_size)]
        # find the chunk with the largest key
        max_idx = torch.argmax(tensor([self.key(ck[0]) for ck in batches]))
        # then make sure it goes first
        batches[0], batches[max_idx] = batches[max_idx], batches[0]
        batch_idxs = torch.randperm(len(batches)-2)
        sorted_idx = torch.cat([batches[i+1] for i in batch_idxs]) if len(batches) > 1 else LongTensor([])
        sorted_idx = torch.cat([batches[0], sorted_idx, batches[-1]])
        return iter(sorted_idx)

