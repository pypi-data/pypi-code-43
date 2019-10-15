import json
from time import time
from typing import Tuple, List

from sklearn.model_selection import train_test_split
from tensorflow_datasets.core.features.text import SubwordTextEncoder

from headliner.model import SummarizerAttention
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
    data_raw = read_data_json('/Users/cschaefe/datasets/welt_dedup.json', 2000)
    train_data, val_data = train_test_split(data_raw, test_size=500, shuffle=True, random_state=42)
    """
    time_start = time()
    preprocessor = Preprocessor(lower_case=True)
    train_prep = [preprocessor(t) for t in train_data]
    inputs_prep = [t[0] for t in train_prep]
    targets_prep = [t[1] for t in train_prep]
    tokenizer_input = SubwordTextEncoder.build_from_corpus(
        inputs_prep,
        target_vocab_size=2 ** 15,
        max_subword_length=20)
    tokenizer_target = SubwordTextEncoder.build_from_corpus(
        targets_prep, target_vocab_size=2 ** 15,
        reserved_tokens=[preprocessor.start_token, preprocessor.end_token],
        max_subword_length=20)
    time_end = time()
    print('time tok: {}'.format((time_end - time_start)))

    vectorizer = Vectorizer(tokenizer_input, tokenizer_target)
    'vocab size input {}, target {}'.format(
        vectorizer.encoding_dim, vectorizer.decoding_dim)


    summarizer = SummarizerTransformer(num_heads=2,
                                       num_layers=1,
                                       feed_forward_dim=512,
                                       embedding_size=64,
                                       embedding_encoder_trainable=True,
                                       embedding_decoder_trainable=True,
                                       dropout_rate=0,
                                       max_prediction_len=60)
    """
    summarizer = SummarizerTransformer.load('/tmp/summarizer_20191014_195358')
#    summarizer.init_model(preprocessor, vectorizer)

    trainer = Trainer(steps_per_epoch=500,
                      batch_size=8,
                   #   embedding_path_encoder='/Users/cschaefe/datasets/glove_welt_dedup.txt',
                 #     embedding_path_decoder='/Users/cschaefe/datasets/glove_welt_dedup.txt',
              #        model_save_path='/tmp/summarizer_attention_256',
            #          tensorboard_dir='/tmp/tensorboard_attention_256',
                      steps_to_log=5)

    trainer.train(summarizer, train_data, val_data=val_data)


