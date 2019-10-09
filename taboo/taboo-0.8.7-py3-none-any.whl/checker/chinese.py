import jieba


class TabooChineseChecker:
    def __init__(self):
        pass

    def check(self, sent, word):
        segmentation = list(jieba.cut(sent))
        if word in segmentation:
            return True
        else:
            return False
