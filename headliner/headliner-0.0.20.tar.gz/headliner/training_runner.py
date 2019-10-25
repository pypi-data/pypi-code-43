import json
import logging
from typing import Tuple, List

import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow_datasets.core.features.text import SubwordTextEncoder
from transformers import BertTokenizer

from headliner.model.summarizer_bert import SummarizerBert
from headliner.preprocessing import Preprocessor, Vectorizer
from headliner.trainer import Trainer


def read_data_json(file_path: str,
                   max_sequence_length: int) -> List[Tuple[str, str]]:
    with open(file_path, 'r', encoding='utf-8') as f:
        data_out = json.load(f)
        return [d for d in zip(data_out['desc'], data_out['heads']) if len(d[0].split(' ')) <= max_sequence_length]


def read_data(file_path: str) -> List[Tuple[str, str]]:
    data_out = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for l in f.readlines():
            x, y = l.strip().split('\t')
            data_out.append((x, y))
        return data_out


if __name__ == '__main__':
    data_raw = read_data('/Users/cschaefe/datasets/en_ger.txt')[:10000]
    train_data, val_data = train_test_split(data_raw, test_size=500, shuffle=True, random_state=42)
    logging.getLogger("transformers.tokenization_utils").setLevel(logging.ERROR)

    tokenizer_input = BertTokenizer.from_pretrained('bert-base-uncased')
    preprocessor = Preprocessor(start_token='[CLS]',
                                end_token='[SEP]',
                                hash_numbers=False,
                                punctuation_pattern=None,
                                filter_pattern=None)
    train_prep = [preprocessor(t) for t in train_data]
    inputs_prep = [t[0] for t in train_prep]
    targets_prep = [t[1] for t in train_prep]
    """
    tokenizer_input = SubwordTextEncoder.build_from_corpus(
        inputs_prep, target_vocab_size=2 ** 13,
        reserved_tokens=[preprocessor.start_token, preprocessor.end_token])
    """
    tokenizer_target = SubwordTextEncoder.build_from_corpus(
        targets_prep, target_vocab_size=2 ** 13,
        reserved_tokens=[preprocessor.start_token, preprocessor.end_token])

    vectorizer = Vectorizer(tokenizer_input, tokenizer_target)

    summarizer = SummarizerBert(num_heads=2,
                                num_layers_encoder=0,
                                num_layers_decoder=1,
                                feed_forward_dim=512,
                                embedding_size_encoder=768,
                                embedding_size_decoder=64,
                                bert_embedding_encoder='bert-base-uncased',
                                embedding_encoder_trainable=False,
                                embedding_decoder_trainable=True,
                                dropout_rate=0,
                                max_prediction_len=20)

    summarizer.init_model(preprocessor, vectorizer)


    trainer = Trainer(steps_per_epoch=100,
                      batch_size=32,
                      steps_to_log=5,
                      tensorboard_dir='/tmp/tens_bert/en_ger_bert_0_preproc'
                      )

    trainer.train(summarizer, train_data, val_data=val_data)


