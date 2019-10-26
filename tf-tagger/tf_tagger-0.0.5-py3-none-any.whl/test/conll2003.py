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
        batch_size=64,
        embedding_size=300,
        hidden_size=300,
        layer_size=3,
        epoch=200
    )

    it.fit(x_train, y_train, x_test, y_test)
    pred = it.predict(x_test, verbose=True)
    print(pred[:3])
    print(it.score_table(x_test, y_test))


if __name__ == '__main__':
    test()
