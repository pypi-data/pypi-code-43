'''this wrapper runs the bhcd executable, with gml files as argument input and read the output tree files
'''
import os
import json
import tempfile
import subprocess
import sys
import csv
import math

import networkx as nx
from ete3 import Tree

import pybhcd

def parse_tree(json_obj):
    tree = Tree()
    tree.add_features(custom_name='0')
    for i in json_obj["tree"]:
        # parse stem    
        if(i.get("stem")):
            if(i["stem"]["parent"] == 0):
                parent_node = tree
            else:
                stem_parent_name = str(i["stem"]["parent"])
                parent_node = tree.search_nodes(custom_name=stem_parent_name)[0]
            child = parent_node.add_child()
            child.add_features(custom_name=str(i["stem"]["child"]))
        elif(i.get("leaf")):# parse leaf
            leaf_parent_name = str(i["leaf"]["parent"])
            parent_node = tree.search_nodes(custom_name=leaf_parent_name)[0]
            parent_node.add_child(name=str(i["leaf"]["label"]))
    return tree

def parse_predict(json_obj):
    dic = {}
    for r in json_obj['fit']['edge']:
        index_i = int(r[0])
        index_j = int(r[1])
        prob_true = math.exp(float(r[-1]))
        dic[(index_i, index_j)] = prob_true
    return dic
    
class BHCD:
    def __init__(self, restart=1, gamma=0.4, alpha=1.0, beta=0.2, delta=1.0, _lambda=0.2, sparse=True):
        self.tree = Tree()
        self._gamma = gamma
        self._alpha = alpha
        self._beta = beta
        self._delta = delta
        self._lambda = _lambda
        self.sparse = sparse
        self.restart = restart        

    def fit(self, G, initialize_tree = True, predict=True):
        self.node_size = len(G.nodes)
        # write files to build directory, replace the last run of fit
        parameter_dic = {'gamma': self._gamma, 'alpha': self._alpha,
            'beta': self._beta, 'delta': self._delta, '_lambda': self._lambda,
            'binary_only': False, 'restarts': self.restart, 'sparse': self.sparse,
            'predict': predict
        }
        output_json = pybhcd.bhcd(G, **parameter_dic)
        if initialize_tree:
            self.tree = parse_tree(output_json)
        if predict:
            self.predict_dic = parse_predict(output_json)

    def predict(self, node_index_i, node_index_j, weight_added = 1):
        if not(type(node_index_i) is int and type(node_index_j) is int):
            raise ValueError("two index should be int typed")
        if not(node_index_i >= 0 and node_index_i < self.node_size and node_index_j >=0 and node_index_j < self.node_size):
            raise IndexError("index out of range")
        if(node_index_i < node_index_j):
            return self.predict_dic[(node_index_i, node_index_j)] > 0.5 
        else:
            return self.predict_dic[(node_index_j, node_index_i)] > 0.5                
