#datasetname = pd.read_csv('C:\Rstuff\olr\inst\extdata\oildata.csv')
#resvarname = datasetname[['OilPrices']]
#expvarnames = datasetname[['SP500', 'RigCount', 'API', 'Field_Production', 'RefinerNetInput', 'OperableCapacity', 'Imports', 'StocksExcludingSPR']]
#olr(datasetname, resvarname, expvarnames, adjr2 = "True")


import pandas as pd
import numpy as np
import statsmodels.formula.api as sm

import itertools

from itertools import combinations

import functools

def reduce_concat(x, sep=""):
	return functools.reduce(lambda x, y: str(x) + sep + str(y), x)

def paste(*lists, sep=" ", collapse=None):
	result = map(lambda x: reduce_concat(x, sep=sep), zip(*lists))
	if collapse is not None:
		return reduce_concat(result, sep=collapse)
	return list(result)

summarylist = []

def olr(datasetname, resvarname, expvarnames, adjr2 = "TRUE"):

    if adjr2 == ("TRUE") or adjr2 == ("True") or adjr2 == ("true"):

        xmod = ["+".join(i) for i in range(1,len(list(expvarnames.columns.values))+1) for i in list(combinations(expvarnames,i))]

        ymod = [paste(resvarname, "~") for i in xmod]

        zmod = [i[0] for i in ymod]

        mod = paste(zmod,xmod)

        output = [sm.ols(formula = i, data=datasetname).fit().rsquared_adj for i in mod]

        maxoutput = max(output)
        
        summarylist = list(enumerate([sm.ols(formula = i, data=datasetname).fit().summary() for i in mod]))

        return(summarylist[output.index(maxoutput)])

    elif adjr2 == ("FALSE") or adjr2 == ("False") or adjr2 == ("false"):

        xmod = ["+".join(i) for i in range(1,len(list(expvarnames.columns.values))+1) for i in list(combinations(expvarnames,i))]

        ymod = [paste(resvarname, "~") for i in xmod]

        zmod = [i[0] for i in ymod]

        mod = paste(zmod,xmod)

        output = [sm.ols(formula = i, data=datasetname).fit().rsquared for i in mod]

        maxoutput = max(output)

        summarylist = list(enumerate([sm.ols(formula = i, data=datasetname).fit().summary() for i in mod]))

        return(summarylist[output.index(maxoutput)])

def olrmodels(datasetname, resvarname, expvarnames):

        xmod = ["+".join(i) for i in range(1,len(list(expvarnames.columns.values))+1) for i in list(combinations(expvarnames,i))]

        ymod = [paste(resvarname, "~") for i in xmod]

        zmod = [i[0] for i in ymod]

        mod = paste(zmod,xmod)

        output = [sm.ols(formula = i, data=datasetname).fit().summary() for i in mod]

        return(output)

def olrformulas(datasetname, resvarname, expvarnames):

        xmod = ["+".join(i) for i in range(1,len(list(expvarnames.columns.values))+1) for i in list(combinations(expvarnames,i))]

        ymod = [paste(resvarname, "~") for i in xmod]

        zmod = [i[0] for i in ymod]

        mod = paste(zmod,xmod)

        return(mod)

def olrformulasorder(datasetname, resvarname, expvarnames):

        xmod = ["+".join(i) for i in range(1,len(list(expvarnames.columns.values))+1) for i in list(combinations(expvarnames,i))]

        sortedxmod = sorted(xmod)

        ymod = [paste(resvarname, "~") for i in sortedxmod]

        zmod = [i[0] for i in ymod]

        mod = paste(zmod,sortedxmod)

        return(mod)

def adjr2list(datasetname, resvarname, expvarnames):

        xmod = ["+".join(i) for i in range(1,len(list(expvarnames.columns.values))+1) for i in list(combinations(expvarnames,i))]

        ymod = [paste(resvarname, "~") for i in xmod]

        zmod = [i[0] for i in ymod]

        mod = paste(zmod,xmod)

        output = [sm.ols(formula = i, data=datasetname).fit().rsquared_adj for i in mod]

        return(output)

def r2list(datasetname, resvarname, expvarnames):

        xmod = ["+".join(i) for i in range(1,len(list(expvarnames.columns.values))+1) for i in list(combinations(expvarnames,i))]

        ymod = [paste(resvarname, "~") for i in xmod]

        zmod = [i[0] for i in ymod]

        mod = paste(zmod,xmod)

        output = [sm.ols(formula = i, data=datasetname).fit().rsquared for i in mod]

        return(output)
