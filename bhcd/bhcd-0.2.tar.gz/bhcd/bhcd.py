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

def parse_predict_file(filename):
    dic = {}
    with open(filename) as f:
        csv_r = csv.reader(f, delimiter=',')
        for r in csv_r:
            index_i = int(r[1])
            index_j = int(r[2])
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
        
    def _write_gml(self, G):
        '''write to tmp dir
        '''
        _G = nx.Graph()
        for node in G.nodes():
            _G.add_node(node)
        for edge in G.edges():
            i,j = edge
            _G.add_edge(i,j)
        return '\n'.join(nx.generate_gml(_G))

    def _write_gml_test(self, node_num):
        _G = nx.Graph()
        for i in range(node_num):
            for j in range(i+1, node_num):
                _G.add_edge(i, j)
        _, filename = tempfile.mkstemp()
        self.test_gml = filename
        nx.write_gml(_G, filename)

    def fit(self, G, initialize_tree = True, predict=True):
        # write files to build directory, replace the last run of fit
        parameter_dic = {'gamma': self._gamma, 'alpha': self._alpha,
            'beta': self._beta, 'delta': self._delta, '_lambda': self._lambda,
            'binary_only': False, 'restarts': self.restart, 'sparse': self.sparse
        }
        output_json = pybhcd.bhcd(G, **parameter_dic)
        if(initialize_tree):
            self.tree = parse_tree(output_json)

            
