# encoding: utf-8

from search import Search


class SearchBinaryList(Search):


    def __init__(self, ratio):

        super(SearchBinaryList, self).__init__()
        self.context = {}
        self.ratio   = ratio



    def preprocess(self, X):

        # TODO: sort

        pass



    def rule(self, X):

        X_sum = sum(X)
        X_len = len(X)

        self.context['X_sum']   = X_sum

        self.context['low']     = 0
        self.context['high']    = X_len - 1
        self.context['current'] = (self.context['low'] + self.context['high']) // 2

        while(True):

            if self.rule_terminate():
                return self.action_terminate(X)
            elif self.rule1(X):
                self.action1()
            else:
                self.action2()



    def rule_terminate(self):

        return self.context['low'] > self.context['high']


    def action_terminate(self, X):

        return X[self.context['best']]



    def rule1(self, X):

        condition = X >= X[self.context['current']]
        current   = sum(X[condition]) / self.context['X_sum']
        return current >= self.ratio


    def action1(self):

        self.context['best'] = self.context['current']
        self.context['low']  = self.context['current'] + 1


    def action2(self):

        self.context['high'] = self.context['current'] - 1
