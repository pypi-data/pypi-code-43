import json
import logging
from typing import Tuple, List

import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow_datasets.core.features.text import SubwordTextEncoder

from headliner.evaluation import BleuScorer
from headliner.model.summarizer_transformer import SummarizerTransformer
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
    from headliner.preprocessing import Preprocessor

    train_data = [('Some inputs.', 'Some outputs.')] * 10

    preprocessor = Preprocessor(filter_pattern='',
                                lower_case=True,
                                hash_numbers=False)
    train_prep = [preprocessor(t) for t in train_data]
    inputs_prep = [t[0] for t in train_prep]
    targets_prep = [t[1] for t in train_prep]

    # Build tf subword tokenizers. Other custom tokenizers can be implemented
    # by subclassing headliner.preprocessing.Tokenizer

    tokenizer_input = SubwordTextEncoder.build_from_corpus(
        inputs_prep, target_vocab_size=2 ** 13)
    tokenizer_target = SubwordTextEncoder.build_from_corpus(
        targets_prep, target_vocab_size=2 ** 13)

    vectorizer = Vectorizer(tokenizer_input, tokenizer_target)
    summarizer = SummarizerTransformer(embedding_size=64, max_prediction_len=50)
    summarizer.init_model(preprocessor, vectorizer)

    trainer = Trainer(batch_size=2)
    trainer.train(summarizer, train_data, num_epochs=3)

    """
    logging.basicConfig(level=logging.INFO)

    class DataIterator:
        def __iter__(self):
            for i in range(100):
                yield ('You are the stars, earth and sky for me!', 'I love you.')

    data_iter = DataIterator()
    summarizer = SummarizerAttention(lstm_size=16, embedding_size=10)

    trainer = Trainer(batch_size=32, steps_per_epoch=100)
    trainer.train(summarizer, data_iter, num_epochs=3)

    pred_vectors = summarizer.predict_vectors('You are great, but I have other plans.', '')
    print(pred_vectors)
    """



