# encoding: utf-8


class Search(object):


    def __init__(self):

        self.context = None


    def preprocess(self, X):

        pass


    def rule_terminate(self, X):

        pass


    def action_terminate(self, X):

        pass


    def rule(self, X):

        while(True):

            if self.rule_terminate(X):
                return self.action_terminate(X)


    def find(self, X):

        self.preprocess(X)
        return self.rule(X)
