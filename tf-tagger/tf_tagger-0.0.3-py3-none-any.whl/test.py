import os
import pickle

from .tf_tagger import TFTagger

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"


def test():

    # import nltk
    # train_sents = list(nltk.corpus.conll2002.iob_sents('esp.train'))
    # # test_sents = list(nltk.corpus.conll2002.iob_sents('esp.testb'))

    it = TFTagger()
    # x = [
    #     [xxx[0] for xxx in xx] for xx in train_sents
    # ]
    # y = [
    #     [xxx[2] for xxx in xx] for xx in train_sents
    # ]
    x = ['我要去北京', '我要去巴黎', '今天天气不错', '明天天气不知道怎么样']
    y = [['O', 'O', 'O', 'Bcity', 'Icity'], ['O', 'O', 'O', 'Bcity', 'Icity'],
         ['Bdate', 'Idate', 'O', 'O', 'O', 'O'],
         ['Bdate', 'Idate', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']]

    it.fit(x, y)
    print(it.predict(x))
    with open('/tmp/test.model', 'wb') as fp:
        pickle.dump(it, fp)
    with open('/tmp/test.model', 'rb') as fp:
        it = pickle.load(fp)
    print(it.predict(x))


if __name__ == '__main__':
    test()
