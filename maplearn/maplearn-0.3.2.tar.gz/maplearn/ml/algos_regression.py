# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 19:51:31 2018

@author: thomas_a
"""
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
from sklearn import linear_model, neural_network
from sklearn.svm import SVR
from sklearn.kernel_ridge import KernelRidge
from sklearn.ensemble import RandomForestRegressor

ALGOS = dict(
            lm=LinearRegression(),
            ransac=linear_model.RANSACRegressor(linear_model.LinearRegression()),
            ridge=linear_model.Ridge(fit_intercept=True, normalize=True),
            svr=SVR(max_iter=500000),
            kr=KernelRidge(),
            mlp=neural_network.MLPRegressor(max_iter=500, early_stopping=True),
            tree=DecisionTreeRegressor(),
            rforest=RandomForestRegressor())