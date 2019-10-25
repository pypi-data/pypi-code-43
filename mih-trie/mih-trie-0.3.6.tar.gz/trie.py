# encoding: utf-8

# import _pickle as pickle
import pickle
import traceback
import progressbar

from node        import Node
from collections import defaultdict


class Trie(object):


    def __init__(self):

        self._tree    = Node()
        self._counter = defaultdict(int)


    def add(self, s):

        node_current = self._tree
        length       = len(s) - 1

        for i, w in enumerate(s):
            # child node
            node_child = node_current.children.get(w, Node(parent=node_current, key=w))

            if length == i:
                node_child.value += 1

            # current node
            node_current.children[w] = node_child

            # update current ref
            node_current = node_child



    def delete(self, s):
        # TODO:

        pass



    def search(self, s):

        node_current = self._tree

        for w in s:
            if w not in node_current.children.keys():
                return False
            node_current = node_current.children[w]

        if 0 == node_current.value:
            return False

        return True



    def trace(self, node):

        t = []

        n = node
        while(n.parent is not None):
            t.append(n.key)
            n = n.parent

        return ''.join(t[::-1])



    def traverse_broad(self):

        current_nodes = [self._tree]

        cnt = 0
        bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)
        while(current_nodes):
            # visit current node
            node = current_nodes.pop(0)
            yield(self.trace(node), node.value)

            # add children
            current_nodes.extend(list(node.children.values()))

            cnt += 1
            bar.update(cnt)



    def revise(self, s, cnt):
        # TODO:

        pass



    @property
    def counter(self):

        self._counter = defaultdict(int)

        for k, v in self.traverse_broad():
            self._counter[v] += 1

        try:
            self._counter.pop(0)
        except:
            traceback.print_exc()

        return self._counter



    def save(self, fn):

        with open(fn, 'wb') as f:
            pickle.dump(self.__dict__, f)


    def load(self, fn):

        with open(fn, 'rb') as f:
            d = pickle.load(f)
            self.__dict__.update(d)
