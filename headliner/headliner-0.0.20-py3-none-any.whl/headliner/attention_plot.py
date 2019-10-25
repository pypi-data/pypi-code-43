import json
from typing import Tuple, List

from matplotlib import pyplot as plt
from tensorflow import squeeze

from headliner.model.summarizer_transformer import SummarizerTransformer


def plot_attention_weights(summarizer, pred_vectors, layer_name):
    fig = plt.figure(figsize=(16, 8))
    input_text, _ = pred_vectors['preprocessed_text']
    input_sequence = summarizer.vectorizer.encode_input(input_text)
    pred_sequence = pred_vectors['predicted_sequence']
    attention = squeeze(pred_vectors['attention_weights'][layer_name])
    for head in range(attention.shape[0]):
        ax = fig.add_subplot(1, 2, head + 1)
        ax.matshow(attention[head][:-1, :], cmap='viridis')
        fontdict = {'fontsize': 10}
        ax.set_xticks(range(len(input_sequence)))
        ax.set_yticks(range(len(pred_sequence)))
        ax.set_ylim(len(pred_sequence) - 1.5, -0.5)
        ax.set_xticklabels(
            [summarizer.vectorizer.decode_input([i]) for i in input_sequence],
            fontdict=fontdict,
            rotation=90)
        ax.set_yticklabels([summarizer.vectorizer.decode_output([i])
                               for i in pred_sequence ], fontdict=fontdict)
        ax.set_xlabel('Head {}'.format(head + 1))
    plt.tight_layout()
    plt.show()

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

    summarizer = SummarizerTransformer.load('/tmp/summarizer_20191010_170029')
    pred_vecs = summarizer.predict_vectors('This is old news.', '')
    sentence = pred_vecs['preprocessed_text'][0]
    attention = pred_vecs['attention_weights']
    print(attention)
    plot_attention_weights(summarizer, pred_vecs, 'decoder_layer1_block2')





