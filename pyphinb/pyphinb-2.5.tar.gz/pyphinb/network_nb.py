import numpy as np
import logging
from itertools import product
from itertools import combinations
import pandas as pd
import functools
from pyemd import emd
from scipy.spatial.distance import cdist
from scipy.stats import entropy

from .tpm import infer_cm
from .convert import (to_2dimensional,state_by_state2state_by_node, state_by_node2state_by_state)


class Network_nb:
  

    def __init__(self, tpm, cm=None, base=None, node_labels=None):
        
        
        self.node_labels=self._validate_nodes_labels(node_labels)
        self.size=len(self.node_labels)
        self.base=int(base)
        self.states_node=list(range(self.base))
        self.sates_all_nodes=[list(x[::-1])  for x in  list(product(self.states_node, repeat=self.size)) ]
        self.sates_all_nodes=np.transpose(self.sates_all_nodes).tolist()
        self.tpm=self._validate_tpm(tpm)
        self.cm=self._validate_cm(cm)
        np.save('base',self.states_node)
        
        
    def _validate_state(self,state):
        if len(state)!=self.size:
            raise NameError('State of the network does not mach')
            
        for s in state:
            if s<0 or s> self.base-1:
                raise NameError('States in state are incorrect')

                
    def _validate_condition(self,condition):
        
        if type(condition)!= type([]):
            raise NameError('Conditions for conditioning must be lists')
        
        for c in condition:
            if c not in self.node_labels:
                raise NameError('Conditioning on non existing nodes')
        
    def conditioned_tpm(self, state, condition):        
        
        self._validate_state(state)
        self._validate_condition(condition)
        nodes=self.node_labels
        
        df=self.tpm
        for c in condition:
            df=df.iloc[df.index.get_level_values(c) == state[nodes.index(c)]]

        return df.groupby(sorted(list(set(nodes)-set(condition)))[::-1],axis=1).sum().values
    
    def conditioned_cm(self,condition):
        
        self._validate_condition(condition)
        
        condition=[self.node_labels.index(c) for c in condition]
        
        new_cm=np.delete(self.cm,condition,0)
        return np.delete(new_cm,condition,1)
  
    def _validate_cm(self,cm):
        
        if cm is None:
            if self.base==2:
                return  infer_cm(state_by_state2state_by_node(self.tpm.values))        
            else:
                raise NameError('For non binary systems a cm is expected')
        
        if cm.shape[0]!=cm.shape[1] or cm.shape[0]!=self.size or cm.shape[1]!=self.size:
            raise NameError('cm dimensions are incorrect')
        return cm

    def _validate_nodes_labels(self,node_labels):
        
        err=False
        if type(node_labels)!= type([]):
            raise NameError('The node_labels is expected as a list')
        else:
            for c in node_labels:
                if type(c)!=type('char'):
                    raise NameError('The node_labels is expected as a list of chars')

        return node_labels
    
    def _tpm2df(self, tpm):
        
        if tpm.shape[0]!=tpm.shape[1]:
            raise NameError('TPM dimensions are incorrect')
            
        index = pd.MultiIndex.from_arrays(self.sates_all_nodes, names=self.node_labels)
        columns = pd.MultiIndex.from_arrays(self.sates_all_nodes, names=self.node_labels)
        
        return pd.DataFrame(tpm,columns=columns, index=index)
    
    def _validate_tpm(self,tpm):
        
        if self.base==2:
            if tpm.shape[0]!=np.power(2, self.size):
                raise NameError('TPM dimensions are incorrect')
            elif tpm.shape[1]==self.size:
                tpm=to_2dimensional(state_by_node2state_by_state(tpm))
            return self._tpm2df( tpm)
        elif tpm.shape[0]!=tpm.shape[1] or tpm.shape[0]!=np.power(self.base, self.size):
            raise NameError('TPM dimensions are incorrect')
        
        return self._tpm2df( tpm)
    def __str__(self):
        return 'Network\n{self.tpm.values}\n{self.cm}'.format(self=self)
    
    def __repr__(self):
        return 'Network\n{self.tpm.values}\n{self.cm}'.format(self=self)