'''
    wrapper of Girvan-Newman community detection algorithm
'''
import networkx as nx
import numpy as np
from ete3 import Tree

from pygncd import gn_inner_routine

def label_list_to_partition_list(label_list):
    partition_list = []
    for labels in label_list:
        dic = {}
        for pos, i in enumerate(labels):
            if dic.get(i) is None:
                dic[i] = set()
            dic[i].add(pos)
        partition = [grp for grp in dic.values()]            
        partition_list.append(partition)
    return partition_list

class GN:
    def __init__(self):
        self.reinit()
        
    def reinit(self):
        self.partition_num_list = []
        self.partition_list = []
        self.tree = Tree()
        self.tree_depth = 0
        
    def fit(self, G_outer, initialize_tree = True):
        '''
            G_outer: nx.Graph like object
            returns the partition
        '''    
        self.reinit()
        self.G = G_outer.copy()

        labels_list = gn_inner_routine(self.G)
        self.partition_list = label_list_to_partition_list(labels_list)
        self.partition_num_list = [len(i) for i in self.partition_list]
        if(initialize_tree):
            self._get_hierarchical_tree()
        return self        

    def get_category(self, i):
        index = 0
        for ind,val in enumerate(self.partition_num_list):
            if(val >= i):
                index = ind
                break
        cat = np.zeros(len(self.G.nodes))
        t = 0
        for j in self.partition_list[index]:
            for r in j:
                cat[r] = t
            t += 1
        return cat

    def get_tree_depth(self):
        return 0

    def _add_node(self, root, node_list, num_index):

        label_list = self.get_category(self.partition_num_list[num_index])
        cat_list = []
        for i in node_list:
            if(cat_list.count(label_list[i]) == 0):
                cat_list.append(label_list[i])
        max_cat = len(cat_list)
        label_list_list = [[] for i in range(max_cat)]
        for i in node_list:
            j = cat_list.index(label_list[i])
            label_list_list[j].append(i)
        for node_list_i in label_list_list:
            node_name = ''.join([str(ii) for ii in node_list_i])
            if(node_name != root.name):
                root_i = root.add_child(name= node_name)
            else:
                root_i = root
            if(len(node_list_i)>1):
                self._add_node(root_i, node_list_i, num_index+1)
                
    def _get_hierarchical_tree(self):
        max_num = self.partition_num_list[-1]
        node_list = [ i for i in range(0, max_num)]
        self._add_node(self.tree, node_list, 1)

    def _set_tree_depth(self, node, depth):
        if(node.is_leaf()):
            if(depth > self.tree_depth):
                self.tree_depth = depth
            return
        for node_i in node.children: # depth first search
            self._set_tree_depth(node_i, depth+1)
            
    def get_tree_depth(self):
        if(self.tree.is_leaf()):
            self._get_hierarchical_tree()
        if(self.tree_depth != 0):
            return self.tree_depth
        self._set_tree_depth(self.tree, 0)
        return self.tree_depth
