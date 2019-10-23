import functools

import numpy as np
from tokenizer_tools.conllz.reader import read_conllz, read_conllx
from tokenizer_tools.converter.conllz_to_offset import conllz_to_offset

from ioflow.corpus_processor.corpus_processor_base import CorpusProcessorBase


def generator_fn(input_file):
    with open(input_file) as fd:
        # sentence_list = read_conllz(fd)
        sentence_list = read_conllx(fd)

    for sentence in sentence_list:
        offset_data, result = conllz_to_offset(sentence)

        yield offset_data


class LocalCorpusProcessor(CorpusProcessorBase):
    def __init__(self, config):
        super(LocalCorpusProcessor, self).__init__(config)

    def prepare(self):
        self.dataset_mapping[self.TRAIN] = functools.partial(generator_fn, self.config['train'])
        self.dataset_mapping[self.EVAL] = functools.partial(generator_fn, self.config['test'])

        self.meta_info = {
            "tags": np.loadtxt(self.config['tags'], dtype=np.unicode, encoding=None).tolist() if self.config.get('tags') else None,
            "labels": np.loadtxt(self.config['labels'], dtype=np.unicode, encoding=None).tolist() if self.config.get('labels') else None
        }
