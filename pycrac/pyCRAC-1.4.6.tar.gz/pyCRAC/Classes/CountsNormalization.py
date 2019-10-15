#!/usr/bin/python
 
__author__      = "Sander Granneman"
__copyright__   = "Copyright 2017"
__version__     = "0.0.1"
__credits__     = ["Sander Granneman"]
__maintainer__  = "Sander Granneman"
__email__       = "sgrannem@staffmail.ed.ac.uk"
__status__      = "beta"

import numpy as np
import pandas as pd

class CountTableNormalization():
	def __init__(self):
		self.data = None
		self.datafile = None
		self.genelengths = []
		
	def loadDataFile(self,datafile):
		self.data = pd.read_csv(datafile,index_col=0,header=0,comment="#",sep="\t")
		self.datafile = datafile

	def zscoreNormalization(self):
		return (self.data - self.data.mean(axis=0))/self.data.std(ddof=0)
	
	def __calcualteDEseqScalingfactor(self,counts):
		"""
		Calculate DESeq scaling factor per sample.
		"""
		# masked array to discard inf, -inf, and nan
		ma = np.ma.masked_invalid(counts)
		return np.exp(np.ma.median(ma))

	def DESeqNormalization(self):
		"""
		Normalize by DESeq scaling factor, which is computed as the median of
		the ratio, for each row (gene), of its read count over its geometric
		mean across all samples. Return new counts dataframe.
		Details:
		--------
		http://genomebiology.com/2010/11/10/R106
		Parameters:
		-----------
		- exp_obj: experiment object. Normalized by DESeq scaling factor.
		"""
		df = self.data.copy()
		# log of counts
		lg = df.apply(np.log)
		# per sample: exponential(median(log(counts) - geometric mean))
		sf = lg.sub(lg.mean(axis=1), axis=0).apply(self.__calcualteDEseqScalingfactor, axis=0)
		# apply scaling
		df = df.div(sf, axis=1)
		return df

	def __sf_tmm(self,obs, ref,
				log_ratio_trim=0.3,
				sum_trim=0.05,
				weighting=True,
				a_cutoff=-1e10):
		"""
		Called by `norm_tmm`.
		"""
		if all(obs == ref):
			return 1
	
		obs_sum = obs.sum()
		ref_sum = ref.sum()

		# log ration of expression accounting for library size
		lr = np.log2((obs / obs_sum) / (ref / ref_sum))
		# absolute expression
		ae = (np.log2(obs / obs_sum) + np.log2(ref / ref_sum)) / 2
		# estimated asymptotic variance
		v = (obs_sum - obs) / obs_sum / obs + (ref_sum - ref) / ref_sum / ref
		# create mask
		m = np.isfinite(lr) & np.isfinite(ae) & (ae > a_cutoff)
		# drop the masked values
		lr = lr[m]
		ae = ae[m]
		v = v[m]
		assert len(lr) == len(ae) == len(v)
	
		n = len(lr)
		lo_l = np.floor(n * log_ratio_trim) + 1
		hi_l = n + 1 - lo_l
		lo_s = np.floor(n * sum_trim) + 1
		hi_s = n + 1 - lo_s
		k = ((lr.rank(method="first") >= lo_l) & (lr.rank(method="first") <= hi_l)) \
				& ((ae.rank(method="first") >= lo_s) & (ae.rank(method="first") <= hi_s))

		if weighting:
			return 2**(sum(lr[k] / v[k]) / sum(1 / v[k]))
		else:
			return 2**(lr[k].mean())

	def TMMNormalization(self,ref_col=None,log_ratio_trim=0.3,sum_trim=0.05,weighting=True,a_cutoff=-1e10):
		"""
		Trimmed Mean of M-values (TMM) is the weighted mean of log ratios between
		this test and the reference, after exclusion of the most expressed genes
		and the genes with the largest log ratios.
	
		Parameters:
		-----------
		- exp_obj: experiment object.
		- ref_col: reference column from which to scale others.
		- log_ratio_trim: amount of trim to use on log-ratios.
		- sum_trim: amount of trim to use on combined absolute values.
		- weighting: whether to compute weights.
		- a_cutoff: cutoff of absolute expression values.
		"""
		df = self.data.copy()
		# remove zeros
		nz = df.where(df > 0)
		nz = nz.dropna(how="all").fillna(0)
		# reference column
		if ref_col is None:
			# quantile factors
			sf_q = self.__sf_q(nz)
			ref_col = (abs(sf_q - np.mean(sf_q))).idxmin()
		# try:
		kwargs = {"ref": nz[nz.columns[ref_col]],
				  "log_ratio_trim": log_ratio_trim,
				  "sum_trim": sum_trim,
				  "weighting": weighting,
				  "a_cutoff": a_cutoff}
		# except KeyError:
			# revert back to auto?
		sf_tmm = nz.apply(self.__sf_tmm, **kwargs)
		# apply scaling
		df = df.div(sf_tmm, axis=1)
		return df

	def __sf_q(self,df, q=0.75):
		"""
		Parameters:
		-----------
		- df: zeroed rows removed
		- q: quartile
		"""
		lib_size = df.sum()
		y = df.T.div(lib_size, axis=0).T
		# fill nans with 0
		y = y.dropna(how="all").fillna(0)
		y = y.quantile(q)
		# factors multiple to one
		sf = y.div(np.exp(np.mean(np.log(y))))
		return sf

	def quantileNormalization(self,q=0.75):
		"""
		Ported from edgeR and still needs to be validated. Also, maybe compare
		edgeR method to limma implementation.
	
		Quantile normalization.
	
		Parameters:
		-----------
		- exp_obj: experiment object.
		- q: quantile.
		"""
		df = self.data.copy()
		# remove zeros
		nz = df.where(df > 0)
		nz = nz.dropna(how="all").fillna(0)
		sf_q = self.__sf_q(nz, q)
		# apply scaling
		df = df.div(sf_q, axis=1)
		return df
		
	def FPKMNormalization(self,norm=1000000):
		""" Calculates the FPKM values for each column """
		sumofcollums = self.data.sum(axis=0)
		normdata = self.data.div((sumofcollums/norm),axis=1)
		return normdata.div(self.genelengths,axis=0)
	
	def TPMNormalization(self,norm=1000000):
		""" Calculates Transcripts per million for the raw count data """
		normdata = self.data.div(self.genelengths,axis=0)
		return normdata.div(normdata.sum(axis=0)/norm)