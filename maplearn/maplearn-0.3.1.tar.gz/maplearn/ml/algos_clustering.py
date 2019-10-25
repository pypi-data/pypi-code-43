# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 19:45:09 2018

@author: thomas_a
"""
from sklearn import cluster

ALGOS = dict(
            mkmeans=cluster.MiniBatchKMeans(),
            kmeans=cluster.KMeans(),
            ms=cluster.MeanShift(bin_seeding=True),
            ward=cluster.AgglomerativeClustering(linkage='ward'),
            spectral=cluster.SpectralClustering(affinity='rbf', eigen_tol=0.25,
                                                eigen_solver='arpack',
                                                assign_labels="kmeans"),
            dbscan=cluster.DBSCAN(),
            propa=cluster.AffinityPropagation(damping=0.8, preference=None), )