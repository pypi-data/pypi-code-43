import functools
import json
import os
import logging

import numpy as np

from ioflow.corpus_processor.corpus_processor_base import CorpusProcessorBase
from ioflow.corpus_processor.download_file import download_file

from tokenizer_tools.tagset.offset.sequence import Sequence
from tokenizer_tools.tagset.offset.span import Span

logger = logging.getLogger(__name__)


# # std corpus format
def parse_std_corpus_to_offset(corpus_item):
    print(corpus_item)
    seq = Sequence(corpus_item['text'], label=corpus_item['classifications']['intent'], id=corpus_item['id'])
    for entity in corpus_item['annotations']['entity']:
        span = Span(
            int(entity['start']), int(entity['start']) + int(entity['length']),
            entity['type']
        )

        # get value which is not in corpus_item object
        span.fill_text(corpus_item['text'])

        seq.span_set.append(span)

    return seq

# real corpus format
def parse_corpus_to_offset(corpus_item):
    logger.debug(corpus_item)
    seq = Sequence([i for i in corpus_item['text']], label=None, id=corpus_item['_id'])
    for annot in corpus_item['annotations']:
        if annot['labels_type'] != 'slot':
            continue

        for entity in annot['entities']:
            span = Span(
                int(entity['start_index']), int(entity['start_index']) + int(entity['slot_len']),
                entity['slot_type'],
                entity['slot_value']
            )

            seq.span_set.append(span)

    return seq


def generator_fn(input_file):
    with open(input_file) as fd:
        for corpus_string in fd:
            corpus_item = json.loads(corpus_string)
            offset_data = parse_corpus_to_offset(corpus_item)

            yield offset_data


def corpus_download(config):
    corpus_file = download_file(config['corpus_download_url'], params={"trainId": config['task_id']})
    return corpus_file


class DownloadCorpusProcessor(CorpusProcessorBase):
    default_split_kwargs = {"train_size": 1.0}

    def __init__(self, config):
        super(DownloadCorpusProcessor, self).__init__(config)

    def prepare(self):
        corpus_file = corpus_download(self.config)

        corpus_list = list(generator_fn(corpus_file))

        train_data, eval_data = self.train_test_split(corpus_list, **self.config.get('corpus_split_kwargs', self.default_split_kwargs))

        self.dataset_mapping[self.TRAIN] = lambda: train_data
        self.dataset_mapping[self.EVAL] = lambda: eval_data

        self.meta_info['tags'] = self.collect_tags(corpus_list)
        self.meta_info['labels'] = self.collect_labels(corpus_list)


def download_corpus_to_path(config, output_file):
    corpus_file = corpus_download(config)
    os.replace(corpus_file, output_file)
