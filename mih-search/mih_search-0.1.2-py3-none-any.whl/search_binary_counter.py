# encoding: utf-8

import time
import numpy as np

from search import Search


class SearchBinaryCounter(Search):


    def __init__(self, ratio):

        super(SearchBinaryCounter, self).__init__()
        self.context = {}
        self.ratio   = ratio


    def preprocess(self, X):

        t1 = time.time()
        X_sorted = sorted(X.items(), key=lambda x: x[0])
        t2 = time.time()
        print('search.preprocess.sort', t2-t1)

        X_value, X_count = list(zip(*X_sorted))
        t3 = time.time()
        print('search.preprocess.split', t3-t2)

        X_value = np.array(X_value)
        X_count = np.array(X_count)

        return X_value, X_count


    def rule(self, X):

        # preprocess
        t1 = time.time()
        X_value, X_count = self.preprocess(X)
        t2 = time.time()
        print('search.rule.preprocess', t2-t1)

        # init
        X_sum = sum(X_value * X_count)
        X_len = len(X_value)
        t3 = time.time()
        print('search.rule.sum', t3-t2)

        self.context['X_sum']   = X_sum
        self.context['low']     = 0
        self.context['high']    = X_len - 1
        self.context['current'] = (self.context['low'] + self.context['high']) // 2
        self.context['best']    = 0

        # rule
        while(True):
            
            print(self.context)

            if self.rule_terminate():
                print('search end!')
                return self.action_terminate(X_value)
            elif self.rule1(X_value, X_count):
                t4 = time.time()
                self.action1()
                print('search.rule.rule1', time.time()-t4)
            else:
                t5 = time.time()
                self.action2()
                print('search.rule.rule1', time.time()-t5)



    def rule_terminate(self):

        return self.context['low'] > self.context['high']


    def action_terminate(self, X_value):

        return X_value[self.context['best']]


    def rule1(self, X_value, X_count):

        condition = X_value >= X_value[self.context['best']]
        current   = sum(X_value[condition] * X_count[condition]) / self.context['X_sum'] 
        return current >= self.ratio


    def action1(self):

        self.context['best']    = self.context['current']
        self.context['low']     = self.context['current'] + 1
        self.context['current'] = (self.context['low'] + self.context['high']) // 2


    def action2(self):

        self.context['high']    = self.context['current'] - 1
        self.context['current'] = (self.context['low'] + self.context['high']) // 2
