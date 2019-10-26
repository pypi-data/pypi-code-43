import os
import pickle

from ..tf_tagger import TFTagger
from ..utils.extract_entities import extract_entities

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"


def test():

    it = TFTagger(embedding_size=100)

    x = ['我要去北京', '我要去巴黎', '今天天气不错', '明天天气不知道怎么样']
    y = [['O', 'O', 'O', 'Bcity', 'Icity'], ['O', 'O', 'O', 'Bcity', 'Icity'],
         ['Bdate', 'Idate', 'O', 'O', 'O', 'O'],
         ['Bdate', 'Idate', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']]

    # from torch_tagger import Tagger
    # it = Tagger(epochs=100, batch_size=4)
    it.fit(x, y, x, y)
    pred = it.predict(x)
    print(pred)
    for i in range(len(x)):
        print(f'sentence: {x[i]}')
        print(extract_entities(pred[i], x[i]))
    with open('/tmp/test.model', 'wb') as fp:
        pickle.dump(it, fp)
    with open('/tmp/test.model', 'rb') as fp:
        it = pickle.load(fp)
    print(it.predict(x))


if __name__ == '__main__':
    test()
