from aiPool.text_classification.OssUtils import OSSUtils
from aiPool.text_classification.ZipUtils import *

oss = OSSUtils()
oss.getBucket()

'''上传训练好的数据模型'''


def upload():
    zip_no_dir("train_word_bag/", "train_word_bag.zip")
    zipDir("train_corpus/", "train_corpus.zip")

    oss.uploadFile("data/TextClassification/train_word_bag.zip", "train_word_bag.zip")
    oss.uploadFile("data/TextClassification/train_corpus.zip", "train_corpus.zip")


'''
下载并解压训练好的数据模型
'''


def download_train_word_bag():
    oss.download("data/TextClassification/train_word_bag.zip", "train_word_bag.zip")
    unzip("train_word_bag", "train_word_bag.zip")


'''下载待训练的语料库'''


def download_train_corpus():
    oss.download("data/TextClassification/train_corpus.zip", "train_corpus.zip")
    unzip("", "train_corpus.zip")


if __name__ == '__main__':
    # download_train_corpus()
    # download()
    upload()
