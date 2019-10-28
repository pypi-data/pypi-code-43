# -*- coding: utf-8 -*-
import os
import pickle
from appdirs import user_cache_dir
from ..tf_tagger import TFTagger
from ..utils.text_reader import text_reader


def test():
    
    cache_dir = user_cache_dir(appname='tf-tagger')

    train_path, dev_path, test_path = [
        os.path.join(cache_dir, x)
        for x in [
            'conll2003_eng_train.txt',
            'conll2003_eng_valid.txt',
            'conll2003_eng_test.txt'
        ]
    ]

    x_train, y_train = text_reader(train_path)
    x_test, y_test = text_reader(test_path)

    it = TFTagger(
        embedding_size=768,
        hidden_size=768,
        layer_size=2,
        batch_size=8 * 2,
        epoch=200,
        bert=True,
        bert_model_dir='./multi_cased_L-12_H-768_A-12',
        bert_max_length=4096,
        bert_vocab_file='./multi_cased_L-12_H-768_A-12/vocab.txt')

    it.fit(x_train, y_train, x_test, y_test)
    pred = it.predict(x_test, verbose=True)
    print(pred[:3])
    print(it.score_table(x_test, y_test))


if __name__ == '__main__':
    test()
