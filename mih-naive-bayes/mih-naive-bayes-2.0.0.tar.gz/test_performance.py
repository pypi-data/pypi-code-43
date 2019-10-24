# encoding: utf-8

from naive_bayes_pulearning1 import NaiveBayesPULearning1


D1 = [['just', 'plain', 'boring'],
      ['entirely', 'predictable', 'and', 'lacks', 'energy'],
      ['no', 'surprises', 'and', 'very', 'few', 'laughs'],
      ['very', 'powerful'],
      ['the', 'most', 'fun', 'film', 'of', 'the', 'summer']]

C1 = ['-', '-', '-', '+', '+']
D2 = [['just', 'like', 'you', 'see'],
      ['so', 'far'],
      ['until', 'now']]
d  = ['predictable', 'with', 'no', 'fun']
nb = NaiveBayesPULearning1()


C12, llds = nb.fit(D1, D2, C1, n_iterations=5)

print '-' * 80

import time

s = time.time()

for i in range(1000):
    #[nb.predict(d) for d in D2]
    nb.predict(D2)

print time.time() - s



# if __name__ == '__main__':
#     import cProfile
#     cProfile.run('nb.predict(D2)')
