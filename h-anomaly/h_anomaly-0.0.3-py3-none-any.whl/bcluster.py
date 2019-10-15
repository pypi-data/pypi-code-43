import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
#from graphviz import Digraph
import scipy.spatial.distance
from scipy.cluster.hierarchy import dendrogram
#Clustering birch
from freediscovery.cluster import birch_hierarchy_wrapper
from freediscovery.cluster import Birch,BirchSubcluster
#Sklearn
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.model_selection import train_test_split
from sklearn import metrics
#Learners
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import OneClassSVM
#Distance measure
from scipy.spatial.distance import euclidean
from sklearn.preprocessing import MinMaxScaler

import warnings

import matplotlib.pyplot as plt

import pickle
warnings.filterwarnings("ignore")

class bcluster(object):
    
    def __init__(self):
        self.parent = None
        self.parent_id = None
        self.depth = None
        self.size = None
        self.cluster_id = None
        self.data_points = []
        self.test_points = {}
        self.test_labels = {}
        self.predicted = {}
        self.centroid = None
        self.classifier = None
        self.outlier_model = None
        self.cluster_obj = None
        self.outlier_points = []
        self.score = []
        self.d1 = None
        self.d2 = None
        self.threshold = None
        self.last_retrained = 1
        self.last_certified = 0
    
    def set_parent(self,parent_node=None):
        if parent_node == None:
            self.parent = None
            self.parent_id = None
        else:
            self.parent = parent_node
            self.parent_id = parent_node.cluster_id
    
    def set_depth(self,depth):
        self.depth = depth
        
    def retrained(self,test_set):
        self.last_retrained = test_set
    
    def certify(self,test_set):
        self.last_certified = test_set
    
    def set_size(self,size):
        self.size = size
        
    def set_cluster_id(self,cluster_id):
        self.cluster_id = cluster_id
        
    def set_data_points(self,data_points):
        self.data_points = data_points
    
    def set_test_labels(self,test_labels,test_set):
        if test_set not in self.test_labels.keys():
            self.test_labels[test_set] = []
        self.test_labels[test_set] = test_labels
        
    def add_test_points(self,test_point,test_set):
        if test_set not in self.test_points.keys():
            self.test_points[test_set] = []
        self.test_points[test_set].append(test_point)
        
    def add_predicted(self,predicted,test_set):
        if test_set not in self.predicted.keys():
            self.predicted[test_set] = []
        self.predicted[test_set].append(predicted)
    
    def set_centroid(self,centroid):
        self.centroid = centroid
        
    def set_classifier(self,classifier):
        self.classifier = classifier
        
    def set_outlier_model(self,outlier_model):
        self.outlier_model = outlier_model
        
    def set_cluster_obj(self,cluster_obj):
        self.cluster_obj = cluster_obj
        
    def add_outlier_points(self,outlier_points):
        self.outlier_points.append(outlier_points)
    
    def reset_outlier_bucket(self):
        self.outlier_points = []
        
    def set_score(self,score):
        self.score = score
    
    def get_score(self):
        return self.score
        
    def add_d1(self,d1):
        self.d1 = d1
        
    def add_d2(self,d2):
        self.d2 = d2
        
    def calculate_threshold(self,outlier_threshold):
        self.threshold = max(self.d1,self.d2)*outlier_threshold
        
    def check_outlier(self,distance):
        if self.threshold < distance:
            result = True
        else:
            result = False
        return result
    
    def check_OCS_outlier(self,test_data):
        if self.outlier_model.predict([test_data]) == -1:
            result = True
        else:
            result = False
        return result