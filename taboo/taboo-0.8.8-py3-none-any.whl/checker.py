import nltk
import jieba


class TabooEnglishChecker:
    def __init__(self):
        pass

    def check(self, sent, word):
        segmentation = nltk.word_tokenize(sent)
        if word in segmentation:
            return True
        else:
            return False


class TabooChineseCheck:
    def __init__(self):
        pass

    def check(self, sent, word):
        segmentation = list(jieba.cut(sent))
        if word in segmentation:
            return True
        else:
            return False
