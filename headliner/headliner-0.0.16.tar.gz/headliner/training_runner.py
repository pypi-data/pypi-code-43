import json
from typing import Tuple, List

from sklearn.model_selection import train_test_split

from headliner.model.summarizer_transformer import SummarizerTransformer
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
    data_raw = read_data('/Users/cschaefe/datasets/en_ger.txt')[:1000]
    train_data, val_data = train_test_split(data_raw, test_size=500, shuffle=True, random_state=42)

    summarizer = SummarizerTransformer(num_heads=8,
                                       num_layers=4,
                                       feed_forward_dim=512,
                                       embedding_size=128,
                                       embedding_encoder_trainable=True,
                                       embedding_decoder_trainable=True,
                                       dropout_rate=0.1,
                                       max_prediction_len=20)

    trainer = Trainer(steps_per_epoch=500,
                      batch_size=32,
                      steps_to_log=5)

    trainer.train(summarizer, train_data, val_data=val_data)


