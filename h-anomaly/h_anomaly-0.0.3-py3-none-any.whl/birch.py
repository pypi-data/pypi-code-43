import pandas as pd
import numpy as np
import seaborn as sns
import pickle

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

import bcluster

warnings.filterwarnings("ignore")

class birch(object):

    def __init__(self,threshold=0.7,branching_factor=40,n_clusters=None,outlier_threshold=0.7):
        self.threshold = threshold
        self.branching_factor = branching_factor
        self.n_clusters = n_clusters
        self.outlier_threshold = outlier_threshold
        self.Birch_clusterer = Birch(threshold=self.threshold, branching_factor=self.branching_factor,
                                     n_clusters=self.n_clusters,compute_sample_indices=True)
        self.test_set = 0
        self.test_set_X = {}
        self.test_set_y = {}
    # Fitting the model with train_X
    def fit(self,data,y):
        self.data = data
        print(self.data.shape)
        self.y = y
        #self.data.drop(self.data.columns[len(self.data.columns)-1], axis=1, inplace=True)
        self.Birch_clusterer.fit(self.data)
        
    def set_test(self,data,y):
        self.test_set += 1
        self.test_set_X[self.test_set] = data
        self.test_set_y[self.test_set] = y

    #Defines and builds the Cluster Feature Tree
    def get_cluster_tree(self):
        self.htree, n_clusters = birch_hierarchy_wrapper(self.Birch_clusterer)
        clusters = {}
        max_depth = 0
        for i in range(n_clusters):
            #print('cluster:', i)
            node = bcluster.bcluster()
            sub_cluster = self.htree.flatten()[i]
            node.set_cluster_id(sub_cluster['cluster_id'])
            depth = sub_cluster.current_depth
            node.set_depth(depth)
            if depth > max_depth:
                max_depth = depth
            if i not in clusters.keys():
                clusters[i] = {}
            if sub_cluster.current_depth == 0:
                node.set_parent()
            else:
                node.set_parent(clusters[sub_cluster.parent['cluster_id']])
            cluster_size = sub_cluster['cluster_size']
            node.set_size(cluster_size)
            data_points = sub_cluster['document_id_accumulated']
            node.set_data_points(data_points)
            centroid = self.data.iloc[sub_cluster['document_id_accumulated'], :].mean(axis=0).values
            node.set_centroid(centroid)
            d1,d1_v = self.calculate_d1(centroid,data_points)
            d2 = self.calculate_d2(centroid,data_points,d1_v)
            node.add_d1(d1)
            node.add_d2(d2)
            node.calculate_threshold(self.outlier_threshold)
            clusters[i] = node
        return clusters,max_depth
    
    #Calculate the d1 distance(point farthest away from centroid)
    def calculate_d1(self,centroid,data_points):
        d1 = 0
        u = centroid
        d1_v = None
        for point in data_points:
            v = point
            distance = euclidean(u,v)
            if distance>d1:
                d1 = distance
                d1_v = v
        return d1,d1_v
    
    #Calculate the d2 distance(point farthest away from d1 and its distance from centroid)
    def calculate_d2(self,centroid,data_points,d1_v):
        d2_d1 = 0
        u = d1_v
        d2_v = None
        for point in data_points:
            v = point
            distance = euclidean(u,v)
            if distance>d2_d1:
                d2_d1 = distance
                d2_v = v
        d2 = euclidean(centroid,v)
        return d2
    
    # Display's the tree
    def show_clutser_tree(self):
        self.htree.display_tree()
        
    # Add classification model at each node and leaf
    def model_adder(self,cluster_tree):
        for cluster_id in cluster_tree:
            clf = DecisionTreeClassifier(criterion='entropy')
            sample_points = cluster_tree[cluster_id].data_points
            train_X_sub = self.data.iloc[sample_points,:]
            train_y_sub = self.y.iloc[sample_points]
            clf.fit(train_X_sub,train_y_sub)
            cluster_tree[cluster_id].set_classifier(clf)
        return cluster_tree
    
    def update_model(self,cluster_tree,cluster_id):
        clf = DecisionTreeClassifier(criterion='entropy')
        sample_points = cluster_tree[cluster_id].data_points
        last_retrained = cluster_tree[cluster_id].last_retrained
        train_X_sub = self.data.iloc[sample_points,:]
        train_y_sub = self.y.iloc[sample_points]
        retraining_datasets = cluster_tree[cluster_id].test_points.keys()
        for test_set in retraining_datasets:
            sample_test_points = cluster_tree[cluster_id].test_points[test_set]
            test_X_sub = self.test_set_X[test_set].iloc[sample_test_points,:]
            test_y_sub = self.test_set_y[test_set].iloc[sample_test_points]
            train_X_sub = pd.concat([train_X_sub,test_X_sub])
            train_y_sub = pd.concat([train_y_sub,test_y_sub])
        X = train_X_sub
        y = train_y_sub
        clf.fit(X,y)
        cluster_tree[cluster_id].retrained(self.test_set)
        cluster_tree[cluster_id].set_classifier(clf)
    
    def outlier_model_adder(self,cluster_tree):
        for cluster_id in cluster_tree:
            clf = OneClassSVM(kernel = 'poly',degree = 5,gamma = 'scale',nu=0.4)
            sample_points = cluster_tree[cluster_id].data_points
            train_X_sub = self.data.iloc[sample_points,:]
            clf.fit(train_X_sub)
            cluster_tree[cluster_id].set_outlier_model(clf)
        return cluster_tree
        
    # # Prediction Function with height based prediction with outlier detection
    # def predict(self,test_X,depth,do_predict=True):
    #     predicted = []
    #     for test_instance in test_X.iterrows():
    #         test_sample = test_instance[1].values
    #         min_distance = float('inf')
    #         selected_cluster = None
    #         for cluster_id in cluster_tree:
    #             if cluster_tree[cluster_id].depth != depth:
    #                 continue
    #             u = cluster_tree[cluster_id].centroid
    #             v = np.asarray(test_sample,dtype='float64')
    #             distance = euclidean(u,v)
    #             if distance < min_distance:
    #                 min_distance = distance
    #                 selected_cluster = cluster_id
    #         cluster_tree[selected_cluster].add_test_points(test_instance[0])
    #         # Outlier identifier
    #         if cluster_tree[selected_cluster].check_outlier(min_distance):
    #             cluster_tree[selected_cluster].add_outlier_points(test_instance[0])
    #         if do_predict:
    #             _predicted_label = cluster_tree[selected_cluster].classifier.predict([test_sample])
    #             cluster_tree[selected_cluster].add_predicted(_predicted_label)
    #             predicted.append(_predicted_label)
    #     return predicted
    
    def distance(self,x,y):
        dist = (list(x[:,1]) - y)**2
        dist = np.sum(dist, axis=1)
        dist = np.sqrt(dist)
        ind = np.unravel_index(np.argmin(dist, axis=None), dist.shape)
        min_distance = dist[np.argmin(dist, axis=None)]
        return list(x[ind])[0],min_distance
    
    # New Predict
    def predict_new(self,test_X,depth,cluster_tree,do_predict=True):
        predicted = []
        cluster_centroids = []
        for cluster_id in cluster_tree:
            cluster_tree[cluster_id].reset_outlier_bucket()
            if cluster_tree[cluster_id].depth != depth:
                continue
            cluster_centroids.append([cluster_id,cluster_tree[cluster_id].centroid])
        cluster_centroids = np.array(cluster_centroids)
        for test_instance in test_X.iterrows():
            test_sample = np.array(test_instance[1].values)
            selected_cluster,min_distance = self.distance(cluster_centroids,test_sample)
            cluster_tree[selected_cluster].add_test_points(test_instance[0],self.test_set)
            # Outlier identifier
            #if cluster_tree[selected_cluster].check_outlier(min_distance):
            #    cluster_tree[selected_cluster].add_outlier_points(test_instance[0])
            if cluster_tree[selected_cluster].check_OCS_outlier(test_sample):
                cluster_tree[selected_cluster].add_outlier_points(test_instance[0])
            if do_predict:
                _predicted_label = cluster_tree[selected_cluster].classifier.predict([test_sample])
                cluster_tree[selected_cluster].add_predicted(_predicted_label[0],self.test_set)
                predicted.append(_predicted_label[0])
        return predicted
    
    # Model certification creator
    def certify_model(self,cluster_tree,test_y):
        for cluster_id in cluster_tree:
            if len(cluster_tree[cluster_id].test_points.keys()) == 0:
                continue
            if self.test_set not in cluster_tree[cluster_id].test_points.keys():
                continue
            cluster_tree[cluster_id].set_test_labels(test_y[cluster_tree[cluster_id].test_points[self.test_set]].values,self.test_set)
            precision = metrics.precision_score(cluster_tree[cluster_id].test_labels[self.test_set], 
                                                cluster_tree[cluster_id].predicted[self.test_set],average='weighted')
            recall = metrics.recall_score(cluster_tree[cluster_id].test_labels[self.test_set], 
                                          cluster_tree[cluster_id].predicted[self.test_set],average='weighted')
            f1_Score = metrics.f1_score(cluster_tree[cluster_id].test_labels[self.test_set], 
                                        cluster_tree[cluster_id].predicted[self.test_set],average='weighted')
            score = {'precision': precision,'recall': recall,'f1_Score': f1_Score}
            cluster_tree[cluster_id].set_score(score)
            
            
    def check_model(self,cluster_tree,threshold = 0.7):
        score = {}
        for cluster_id in cluster_tree:
            if len(cluster_tree[cluster_id].test_points) == 0:
                continue
            score[cluster_id] =  cluster_tree[cluster_id].get_score()
            if score[cluster_id]['f1_Score'] < threshold:
                print('retreining',score[cluster_id]['f1_Score'])
                self.update_model(cluster_tree,cluster_id)
                
    def rebuild_models(self,cluster):
        train_X_sub = self.data
        train_y_sub = self.y
        for test_set in range(1,self.test_set+1):
            test_X_sub = self.test_set_X[test_set]
            test_y_sub = self.test_set_y[test_set]
            train_X_sub = pd.concat([train_X_sub,test_X_sub])
            train_y_sub = pd.concat([train_y_sub,test_y_sub])
        X = train_X_sub.reset_index(drop=True)
        y = train_y_sub.reset_index(drop=True)
        self.fit(X,y)
        self.test_set = 0
        self.test_set_X = {}
        self.test_set_y = {}
        cluster_tree,max_depth = cluster.get_cluster_tree()
        cluster_tree = cluster.model_adder(cluster_tree)
        cluster_tree = cluster.outlier_model_adder(cluster_tree)
        return cluster_tree,max_depth
                