# Copyright (C) 2000-2018 Hiroshi Watabe watabe@cyric.tohoku.ac.jp
# Define PYBld Class python implemantation of BLD originally developed by Richard E Carson
# $Id: __init__.py,v 3c9bd9bf60c7 2019/02/11 09:14:39 watabe $
from numpy import *
from . import datafile
from . import pybldc
from . import grace_np #grace graph
import pickle
import string
import sys
from . import bldanaimg
import os
import time
import types
try:#for GnuPlot
	import Gnuplot
except ImportError:
	pass
try:
        import matplotlib.pyplot as plt
except ImportError:
        pass

class PYBLD:
	""" BLD with Python
	Variables
	gp_cmd = 'matplot' or 'grace' or 'gnuplot' for plotting data
	view_cmd = 'matplot' or 'gpetview' to view data
	show = 1 if you want to see detail of fitting
	fit_z = results of fitting
	comment = comment for output function
	legend = list of legend for graph
	title = title of graph
	xlabel = label for X axis for graph
	ylabel = label for X axis for graph
	"""
	def __init__(self):
		import __main__
		self.def_var = dir(__main__)
		self.tm_inp = 0 #input function time
		self.cnt_inp = 0 #input function time
		self.corrmat = array([0])
		self.fitresmat = array([0])
		self.fit_z = array([0]) #results of fitting
		self.comment = "" # comment for output function
		self.gp_cmd = 'matplot' #you can give eather 'grace' or 'gnuplot'
		self.view_cmd = 'matplot' #you can give eather 'gpetview' or 'matplot'
		self.version = "3.1"
		self.legend = "" #legend for Graph
		self.title = "" #title for Graph
		self.xlabel = "" #xaxis label for Graph
		self.ylabel = "" #yaxis label for Graph
		self.sddata = "" #sd data for Graph
		self.show = 1
	def mulmat(self,a,b):
		"Multiply Matrix"
		res = dot(a,b);
		return(res)
	def invmat(self,a):
		"inverse matrix"
		res = linalg.inv(a)
		return(res)
	def conv_exp(self,time,param,bld_tm,bld_cnt):
		"""conv_exp(x,p,a,b)  returns  the  convolution  of  the  piecewise
		linear  curve  described  by  the  variables  a  and  b with a sum of
		exponentials defined by the parameter list p, evaluated at  times  x.
		The  variable  'a' is the list of times of the sampled curve (assumed
		to be in ascending order) and 'b' contains the function value at  the
		times  in  'a'.   The  curve  being integrated is assumed to have the
		value 0 for a<=0 (so the result of INTEGRATE is 0 for x<=0).   For  x
		values  beyond  the  largest  value  of  a, the curve is extrapolated
		linearly based on the final two points.  The exponential function has;
		the following form depending on the number of values in p:
		1 value    p(1)
		2 values   p(1)exp(-p(2)x)
		3 values   p(1)exp(-p(2)x)+p(3)
		4 values   p(1)exp(-p(2)x)+p(3)exp(-p(4)x),    etc"""

		res = pybldc.conv_exp(time,param,bld_tm,bld_cnt)
		return(res)
	def pconv_exp(self,time,param,bld_tm,bld_cnt):
		"""pconv_exp(x,p,a,b)  returns  the  product convolution  of  the  piecewise
		linear  curve  described  by  the  variables  a  and  b with a sum of
		exponentials defined by the parameter list p, evaluated at  times  x.
		The  variable  'a' is the list of times of the sampled curve (assumed
		to be in ascending order) and 'b' contains the function value at  the
		times  in  'a'.   The  curve  being integrated is assumed to have the
		value 0 for a<=0 (so the result of INTEGRATE is 0 for x<=0).   For  x
		values  beyond  the  largest  value  of  a, the curve is extrapolated
		linearly based on the final two points.  The exponential function has;
		the following form depending on the number of values in p:
		1 value    p(1)
		2 values   p(1)exp(-p(2)x)
		3 values   p(1)exp(-p(2)x)+p(3)
		4 values   p(1)exp(-p(2)x)+p(3)exp(-p(4)x),    etc"""

		res = pybldc.pconv_exp(time,param,bld_tm,bld_cnt)
		return(res)
	def interpolate(self,newtime,time,cnt):
		"""interpolate(x,a,b) interpolates  the  piecewise  linear   curve
		described  by  a  and  b to the list of times x. This function assumes
		that the values in the variable a are greater than or equal to 0  and
		are  in  ascending order.  The curve being interpolated is assumed to
		have the value 0 for a<=0 (so the result of INTEGRATE is 0 for x<=0).
		For x values beyond the largest value of a, the curve is extrapolated(
		linearly based on the final two points."""
		newtime = self.checkarg(newtime)
		res = pybldc.interpolate(time,cnt,newtime)
		return(res)
	def spline(self,newtime,time,cnt):
		"""spline(X,R,S) The SPLine fit routine allows the  user  to  generate  a  smooth curve at many time points, simply by specifying the Y values at a few of these points.  First the user must specify the time points at which the curve should be computed (X),  and  the  original curve in  R and S.
		Typing SPL will cause the routine to compute the spline fit.  The spline fit routine places the spline in X, and  the final fitted values in Y.  The original data (R and S) and the spline curve (X and Y) are selected upon completion, ready for plotting."""
		newtime = self.checkarg(newtime)
		res = pybldc.spline(time,cnt,newtime)
		return(res)
		
	def integrate(self,newtime,time,cnt):
		"""integrate(x,a,b) Integrates the piecewise linear curve described  by
		the  variables  a  and  b  from  0  to the list of times x.  This
		function assumes that the values in the variable a are  greater  than
		or equal to 0 and are in ascending order.  The curve being integrated
		is assumed to have the value 0 for a<=0 (so the result  of  INTEGRATE
		is  0  for  x<=0).   For  x values beyond the largest value of a, the
		curve is extrapolated linearly based on the  final  two  points.   To)
		evaluate the integral from x1 to x2, use integrate(x2,a,b) - integrate(x1,a,b)"""
		if self.checkarray(newtime)==0:
			if len(array(newtime).shape)==0:
				ar_newtime = array([newtime])
			else:
				ar_newtime = array(newtime)
		else:
			ar_newtime = newtime
		if self.checkarray(time)==0:
			ar_time = array(time)
		else:
			ar_time = time
		if self.checkarray(cnt)==0:
			ar_cnt = array(cnt)
		else:
			ar_cnt = cnt
		res = pybldc.integrate(ar_time,ar_cnt,ar_newtime)
		return(res)
	def gaus(self,mean,sd):
		"""gaus(x,y) returns a list of gaussian random numbers with mean x
		and  standard deviation y.  One value is returned for each element in
		the list x.  
		To get 100 random  numbers  with  mean  0  and  standard
		deviation  1,  Use  gaus(zeros(100,'f'),1).  These numbers are pseudo
		random and are generated from a seed variable."""

		seed3 = int(random.random()*1000)
		#check arg
		sd = self.checkarg(sd)
		mean = self.checkarg(mean)
		#in the case of multi dimension
		s = mean.shape
		if len(s)>1:
			sum = 1
			for i in range(len(s)):
				sum = sum*s[i]
			mean = reshape(mean,(sum,))
		ret = pybldc.gaus(mean,sd,seed3)
		if len(s)>1:
			ret = reshape(ret,s)
		return(ret)
	def ran(self,x,y):
		"""ran(x,y) returns a list of uniform random numbers between x and y (x and y must be same length).
		These numbers are pseudo_- random and are generated from 
		a seed variable."""

		seed2 = int(1000*(time.time() - int(time.time())))
		#check arg
		x = self.checkarg(x)
		y = self.checkarg(y)
		return(pybldc.ran(x,y,seed2))
	
	def mullin(self,dep_y,ind_x,wt=array([0.0]),cst=0):
		"""mullin(dependent,independents,[wt],cst=0 or 1) perform linear regression of one dependent variable against any number
                   of independent variables.  To use this routine you must first select the
                   variables of interest. 
		   The first variable must be the dependent one,followed by the independent
                    variables.  The order of the resulting parameters will correspond to the order
                    of selection of the independent variables.
		   The linear fitting routine will do a weighted regression when you create
                    a variable named 'wt' with the same length as the independent variable. 
                   This variable will be used to weight the sum of squares computed by the 
                   regression routine. You will be notified that a weighted regression is being done.
                If the user give cst=1, the routine includes constant.
		   This funciton returns estimated p values and their se. Also corrmat,fitresmat,fit_z contains results of fitting.

		   fitresmat[0]:standard error of the estimate
		   fitresmat[1]:sum of squares
		   fitresmat[2]:degree of freedom1
		   fitresmat[3]:degree of freedom2
		   fitresmat[4]:F value
		   fitresmat[5]:R square
		   fitresmat[6]:Correlation coefficient
		   """
		if self.show==0:
			pybldc.cvar.show_flag = 0
		self.corrmat = array([0]) #initialize corrmat and resmat
		self.fitresmat = array([0])
		if len(ind_x.shape)==1:
			ind_x = reshape(ind_x,(1,ind_x.shape[0]))
		if cst == 1: #there is constant
			c1,c2 = ind_x.shape
			newx = zeros([c1+1,c2],'f');
			newx[0:c1,:] = ind_x;
			newx[-1,:] = 1.0;
			ind_x = newx;
		if len(wt)==len(dep_y):
			weight = 1
		else:
			weight = 0
		#ind_x = transpose(ind_x)
		res = pybldc.mullin(dep_y,ind_x,wt,weight,cst)
		n_var = int(res[0])
		res_p = res[1:(n_var + 1)]
		res_se = res[(n_var + 1):(n_var*2 + 1)]
		self.fitresmat = res[(n_var*2 + 1):(n_var*2 + 8)]
		self.corrmat = reshape(res[(n_var*2 + 8):(n_var*2 + 8 + n_var*n_var)],(n_var,n_var))
		self.fit_z = res[(len(res)-len(dep_y)):len(res)]
		pybldc.cvar.show_flag = 1
		return res_p,res_se

	#polinominal fitting
	def polfit(self,deg_pol,x,y,wt=array([0.0])):
		"""polfit(degree,x,y,[wt])
		The polynomial fitting routine will perform a polynomial fit. A polynomial function is of the form ;
		y=a+bx+cx**2.......
		The simplest polynomial fit is a linear fit;
		y_=a_+bx    
		First you must specify the order of the polynomial to be used, i.e. one=linear, two=quadratic, three=cubic, etc.
		The routine will perform all fits starting with linear, quadratic, up to the requested order.  A statistical summary will be provided.
		The polynomial fitting routine will do a weighted regression when you create a variable named 'wt' with the same number of elements as the independent (x) variable.  This variable will be used to weight the sum of squares computed by the regression routine.  You will be notified that a weighted regression is being done. 
		This funciton returns estimated p values and their se. Also corrmat,fitresmat,fit_z contains results of fitting.

		fitresmat[0]:standard error of the estimate
		fitresmat[1]:sum of squares
		fitresmat[2]:degree of freedom1
		fitresmat[3]:degree of freedom2
		fitresmat[4]:F value
		fitresmat[5]:R square
		fitresmat[6]:Correlation coefficient

		"""
		if self.show==0:
			pybldc.cvar.show_flag = 0
		self.corrmat = array([0]) #initialize corrmat and resmat
		self.fitresmat = array([0])
		if len(wt)==len(x):
			weight = 1
		else:
			weight = 0
		res = pybldc.polfit(deg_pol,y,x,wt,weight)
		n_var = int(res[0])
		res_p = res[1:(n_var + 1)]
		res_se = res[(n_var + 1):(n_var*2 + 1)]
		self.fitresmat = res[(n_var*2 + 1):(n_var*2 + 8)]
		self.corrmat = reshape(res[(n_var*2 + 8):(n_var*2 + 8 + n_var*n_var)],(n_var,n_var))
		self.fit_z = res[(len(res)-len(y)):len(res)]
		pybldc.cvar.show_flag = 1
		return res_p,res_se
	#general fitting
	def fit(self,fitfunc,x,obs,p,wt=array([0.0]),fixm=array([0.0])):
		"""Fitting to user-given funciton. fit(func,x,obs,p)
		where 'func' is define function, 'x' is x-axis of function such as time, 'obs' is observed data, and 'p' is array of initial parameters to be fitted.
		you must define func as func(x,p) and return fitted values.
		Optionally you can give weight of data as variable 'wt'.
		Optionally you can fix certain parameters by variable 'fixm'
		fixm has format of array with elements of one or zero. If you want to fix second parameter in four parameters, you can give fixm = array([0,1,0,0])
		this funciton returns estimated p values and their se. Also corrmat,fitresmat,fit_z contains results of fitting.

		fitresmat[0]:standard error of the estimate
		fitresmat[1]:sum of squares
		fitresmat[2]:degree of freedom1
		fitresmat[3]:degree of freedom2
		fitresmat[4]:F value
		fitresmat[5]:R square
		fitresmat[6]:Correlation coefficient
		"""
		pybldc.cvar.fit_func = 2 #specify general fitting
		if self.show==0:
			pybldc.cvar.show_flag = 0
		self.corrmat = array([0]) #initialize corrmat and resmat
		self.fitresmat = array([0])
		if len(wt)!=len(obs):#no weight
			wt = zeros(obs.shape,'d')
			pybldc.cvar.fit_weight = 0
		else:
			pybldc.cvar.fit_weight = 1

		if len(fixm)!=len(p):# no fix
			fixm = zeros(p.shape,'d')
			pybldc.cvar.fit_const = 0
		else:
			if len(p)==1 and fixm[0]==0:#one parameter case
				fixm = zeros(p.shape,'d')
				pybldc.cvar.fit_const = 0
			else:
				pybldc.cvar.fit_const = 1
		res = pybldc.fit(fitfunc,x,obs,p,wt,fixm)
		fit_puse = self.dimen(p) - sum(fixm)
		res_p = res[0:(self.dimen(p))]
		res_se = res[(self.dimen(p)):(2*(self.dimen(p)))]
		self.corrmat = res[(2*(self.dimen(p))):(2*(self.dimen(p)) + int(fit_puse*fit_puse))]
		self.corrmat.shape = (int(fit_puse),int(fit_puse))
		self.fitresmat = res[(2*(self.dimen(p)) + int(fit_puse*fit_puse)):]
		self.fit_z = fitfunc(x,res_p)
		pybldc.cvar.show_flag = 1
		pybldc.cvar.fit_weight = 0
		pybldc.cvar.fit_const = 0
		return(res_p,res_se)
	#fitting with derivatives
	def fitd(self,fitfunc,x,obs,p,wt=array([0.0]),fixm=array([0.0])):
		"""Fitting to user-given funciton with derivatives. fitd(func,x,obs,p)
		where 'func' is define function, 'x' is x-axis of function such as time, 'obs' is observed data, and 'p' is array of initial parameters to be fitted.
		you must define func as func(x,p). This function returns fitted values and derivatives of each parameter.
		Optionally you can give weight of data as variable 'wt'.
		Optionally you can fix certain parameters by variable 'fixm'
		fixm has format of array with elements of one or zero. If you want to fix second parameter in four parameters, you can give fixm = array([0,1,0,0])
		this funciton returns estimated p values and their se. Also corrmat,fitresmat,fit_z contains results of fitting.
		"""
		pybldc.cvar.fit_func = 1 #specify general fitting with derivatives
		if self.show==0:
			pybldc.cvar.show_flag = 0
		self.corrmat = array([0]) #initialize corrmat and resmat
		self.fitresmat = array([0])
		if len(wt)!=len(obs):#no weight
			wt = zeros(obs.shape,'d')
			pybldc.cvar.fit_weight = 0
		else:
			pybldc.cvar.fit_weight = 1
			
		if len(fixm)!=len(p):# no fix
			fixm = zeros(p.shape,'d')
			pybldc.cvar.fit_const = 0
		else:
			if len(p)==1 and fixm[0]==0:#one parameter case
				fixm = zeros(p.shape,'d')
				pybldc.cvar.fit_const = 0
			else:
				pybldc.cvar.fit_const = 1
		res = pybldc.fit(fitfunc,x,obs,p,wt,fixm)
		fit_puse = self.dimen(p) - sum(fixm)
		res_p = res[0:(self.dimen(p))]
		res_se = res[(self.dimen(p)):(2*(self.dimen(p)))]
		self.corrmat = res[(2*(self.dimen(p))):(2*(self.dimen(p)) + int(fit_puse*fit_puse))]
		self.corrmat.shape = (int(fit_puse),int(fit_puse))
		self.fitresmat = res[(2*(self.dimen(p)) + int(fit_puse*fit_puse)):]
		self.fit_z = fitfunc(x,res_p)[0:len(x)] #exclude derivatives
		pybldc.cvar.show_flag = 1
		pybldc.cvar.fit_weight = 0
		pybldc.cvar.fit_const = 0
		pybldc.cvar.fit_func = 2 #specify general fitting
		return(res_p,res_se)
	def combine(self,a,b): #combine two arrays into one array
		"""combine(a,b) combines two arrays into one array"""
		return(array(tuple(a)+tuple(b)))
		
	def histogram(self,a,b0,bw,nbins):
		"""histogram(a,b0,bw,nbins) the histogram of the list a where the
		first bin starts at b0, the width of each bin is bw, and 
		there are a total of nbin bins."""
		bins = arange(b0,b0 + nbins*bw,bw,'f')
		n = searchsorted(sort(a.astype('f')),bins)
		n = concatenate([n,[len(a)]])
		return n[1:]-n[:-1]
	#filtering
	def filter(self,x,f):
		res = pybldc.filter(x,f);
		return(res)
	#normalize
	def normalize(self,x):
		"scale a vector/matrix so that its sum is 1"
		shape = x.shape
		if(len(shape)==1):
			ret = x/sum(x)
		else:
			ret = x/sum(sum(x))
		return ret
	#gaussian filter
	def gaussian_1d(self,x,f):
		ret1 = exp(-log(2.0)*4.0*(x**2)/(f**2))
		ret = self.normalize(ret1)
		return ret
	def gaussian_2d(self,x,f):
		"calculate value of 2d gaussian at distances x from the center with fwhm of f"
		ret1 = exp(-log(2.0)*4.0*(x**2 + self.tran(x)**2)/(f**2))
		ret = self.normalize(ret1)
		return ret
	def gauss_filter1d(self,fwhm):
		"define gaussian kernel with fwhm in pixels (keep until 1% of gaussian)"
		xrange = arange(-int(1.3*fwhm),(int(1.3*fwhm)+1))
		ret = self.gaussian_1d(xrange,fwhm)
		return ret
	def gauss_filter2d(self,fwhm):
		"define gaussian kernel with fwhm in pixels (keep until 1% of gaussian)"
		xrange = arange(-int(1.3*fwhm),(int(1.3*fwhm)+1))
		xrange = reshape(xrange,(xrange.shape[0],1)) #in order to trans
		ret = self.gaussian_2d(xrange,fwhm)
		return(ret)
	def gauss_smooth1d(self,x,fwhm):
		"perform 1d gaussian smooth of line x with fwhm"
		ret = self.filter(x,self.gauss_filter1d(fwhm))
		return ret;
	def gauss_smooth2d(self,x,fwhm):
		"perform 2d gaussian smooth of image x with fwhm"
		ret = self.filter(x,self.gauss_filter2d(fwhm))
		return ret;
#read data of two columns
	def input(self,*arg):
		"Read data file if no argument are given, from standard input"
		"if you want to read only two column from multi-column file, give second argument for number of column"
		if len(arg)==0:
			fname = sys.stdin
		else:
			fname = arg[0]
		dat = datafile.datafile(fname);
		try:
			coln = dat.data.shape[1]
		except AttributeError:#error
			return([])
		if len(arg)==2: #specify how many columns to read
			coln = arg[1]
		ret = []
		for i in range(coln):
			ret.append(dat.data[:,i])
		return(ret)
	def output(self,outfile,*arg):
		"Output text file from data. If first argument is null, print out to standard output"
		if len(outfile)==0:
			fp = sys.stdout
		else:
			fp = open(outfile,'w')
		if len(self.comment)!=0: #comment
			fp.write("#" + self.comment + '\n')
		if len(arg[0].shape)==2:#for multidimension array
			ndim = arg[0].shape[1]
		else:
			ndim = arg[0].shape[0]
		ny = len(arg)
		for i in range(ndim):
			aline = ""
			for j in range(ny):
				if len(arg[j].shape)==2:#for multidimension array
					for k in range(arg[j].shape[0]):
						aline = aline + " " + str(arg[j][k][i])
				else:
					aline = aline + " " + str(arg[j][i])
			aline = aline + '\n'
			fp.write(aline)
		fp.close()
		return
	def plot(self,_tm,*_arg):
		ny = len(_arg)
		if self.gp_cmd=='matplot':
			gp = self.matplot(_tm,_arg,ny)
		else:
		        if self.gp_cmd=='grace':
			        gp = self.graceplot(_tm,_arg,ny)
		        else:
			        gp = self.gnuplot(_tm,_arg,ny)
		return gp
		
	# Graph plot using Grace
	def matplot(self,tm,arg,ny):
		"Plot x,y points using matplot"
		gp = plt.figure()
		axs = gp.add_subplot(111)
		if len(self.title)!=0:
			gp.suptitle("%s" % self.title)
		if len(self.xlabel)!=0:
			axs.set_xlabel("%s" % self.xlabel)
		if len(self.ylabel)!=0:
			axs.set_ylabel("%s" % self.ylabel)
		
		ndim = tm.shape[0]
		pdat = zeros((ndim,),'d')
		idata = 0
		for i in range(ny):
			if len(arg[i].shape)==2:#multi-column data
				no_col = arg[i].shape[0]
			else:
				no_col = 1
			for ic in range(no_col):
				if no_col==1:
					col_data = arg[i]
				else:
					col_data = arg[i][ic]
				try:
					pdat[:] = col_data.astype('d')
				except ValueError: #another set of data
					tm = col_data
					ndim = len(tm)
					pdat = zeros((ndim,),'d')
					continue

				try:
					legend = self.legend[idata]
				except IndexError:
                                        legend = ''
				axs.plot(tm,pdat,label=legend)
				if len(legend)>0:
					axs.legend(loc='best')
				if len(self.sddata)!=0:
					try:
						nsd = self.sddata.shape[1] #how many columns for sd
					except:#only one
						sd = self.sddata
					else:
						if no_col==1:
							sd = self.sddata[:,i]
						else:
							sd = self.sddata[:,ic]
					axs.errorbar(tm,pdat,yerr=sd)

				idata = idata + 1
		#gp.ginput(timeout=0)
		try:
		        if sys.ps1: interpreter = True
		except AttributeError:
		        interpreter = False
		        if sys.flags.interactive: interpreter = True
		if interpreter:
		        plt.show(block=False)
		else:
		        plt.show(block=True)
		return(gp)
        
	# Graph plot using Grace
	def graceplot(self,tm,arg,ny):
		"Plot x,y points using Grace"
		gp = grace_np.GraceProcess()
		#initialize
		gp('page size 600 600')
		gp('view xmin 0.15')
		gp('view xmax 0.9')
		gp('view ymin 0.15')
		gp('view ymax 0.9')
		gp('legend 0.5, 0.8')
		if len(self.title)!=0:
			gp('title "%s"' % self.title)
		if len(self.xlabel)!=0:
			gp('xaxis label "%s"' % self.xlabel)
		if len(self.ylabel)!=0:
			gp('yaxis label "%s"' % self.ylabel)
		if len(self.sddata)!=0:
			gp('type xydy')
		
		ndim = tm.shape[0]
		pdat = zeros((ndim,),'d')
		idata = 0
		for i in range(ny):
			if len(arg[i].shape)==2:#multi-column data
				no_col = arg[i].shape[0]
			else:
				no_col = 1
			for ic in range(no_col):
				if no_col==1:
					col_data = arg[i]
				else:
					col_data = arg[i][ic]
				try:
					pdat[:] = col_data.astype('d')
				except ValueError: #another set of data
					tm = col_data
					ndim = len(tm)
					pdat = zeros((ndim,),'d')
					continue

				try:
					legend = self.legend[idata]
				except IndexError:
					pass
				else:
					str = 'g0.s%d legend "%s"' % (idata,legend)
					gp(str)
				if len(self.sddata)!=0:
					gp('s%d type xydy' % (idata))
				for j in range(ndim):
					str = "g0.s%d point %f,%f" % (idata,tm[j],pdat[j])
					gp(str)
					if len(self.sddata)!=0:
						try:
							nsd = self.sddata.shape[1] #how many columns for sd
						except:#only one
							sd = self.sddata
						else:
							if no_col==1:
								sd = self.sddata[:,i]
							else:
								sd = self.sddata[:,ic]
						str = "g0.s%d.y1[%d] = %f" % (idata,j,sd[j])
						gp(str)

				idata = idata + 1
		gp('autoscale')
		gp('redraw')
		return(gp)
	def gnuplot(sel,tm,arg,ny):
		"Plot x,y points using gnuplot"
		gp = Gnuplot.Gnuplot()
		gp('set data style lines')
		ndim = tm.shape[0]
		pdat = zeros((ndim,ny+1),'d')
		pdat[:,0] = tm[:]
		str = "gp.plot("
		for i in range(ny-1):
			pdat[:,i+1] = arg[i].astype('d')
			str = str + "Gnuplot.Data(pdat,cols=(0,%d))," % (i+1)
		pdat[:,ny] = arg[ny-1].astype('d')
		str = str + "Gnuplot.Data(pdat,cols=(0,%d)))" % (ny)
		exec(str)
		return gp
#
	#check whether array or not
	def checkarg(self,inp):
		try:
			res = inp.astype('f')
		except AttributeError:
			res = array([inp]).astype('f')
		return(res);
	#check whether array
	def checkarray(self,inp):
		try:
			tmp = inp.shape
		except AttributeError:
			return 0
		return 1
	#save BLD object
	def save(self,file):
		import __main__
		fp = open(file,'wb');
		obj = self.var()
		lenobj = len(obj)
		#first save how many objects you have
		fp.write(bytes('%d\n' % lenobj,'utf8'))
		for i in obj:
                        if type(__main__.__dict__[i]) == types.FunctionType:
                                continue
                        if type(__main__.__dict__[i]) == PYBLD:#pybld instance
                                continue

#                        if isinstance(__main__.__dict__[i],bldanaimg.ANAIMG)!=1:#bld image will be saved
#                                continue
                        try:
                                s = pickle.dumps(__main__.__dict__[i])
                        except pickle.PicklingError:
                                pass
                        except TypeError:
                                pass
                        else:
                                fp.write(bytes('%s\n' % i,'utf8'))
                                pickle.dump(__main__.__dict__[i],fp,protocol=2,fix_imports=True) #-1 to choose maximum protocol
                                #print(repr(i))
#			pickle.dump(obj[i],fp,1)
		fp.close()
	#recall BLD object
	def recall(self,file):
                import __main__
                fp = open(file,'rb');
                lenobj = fp.readline()
                lenobj = int(lenobj)
                name = []
                obj = []
                for i in range(lenobj):
                        s = fp.readline()
                        s = str(s[0:-1],'utf8')
                        name.append(s)
                        try:
                                __main__.__dict__[s] = pickle.load(fp,fix_imports=True)
                        except SystemError:
                                pass
                        except TypeError:
                                pass
                        except pickle.UnpicklingError:
                                pass
                        except ImportError:
                                pass
                        except AttributeError:
                                pass
                        except EOFError:
                                break
                fp.close()
                return
	#BLD var list variables
	def var(self):
		import __main__
		list = dir(__main__)
		varlist = []
		for i in list:
			match_flag = 0
			for j in self.def_var:
				if i == j:
					match_flag = 1
					break;
			if match_flag == 0:
				varlist.append(i)
		return varlist
	#get numbers of row
	def nrow(self,a):
		shape = a.shape
		if len(a) == 1:
			return(shape[0])
		else:
			return(shape[0])
	def ncol(self,a):
		shape = a.shape
		if len(a) == 1:
			return(1)
		else:
			return(shape[1])
	def tran(self,a):
		" Transpose of matrix "
		return(transpose(a))
	def mean(self,a):
		"return mean value of matrix"
		#in the case of multi dimension
		s = a.shape
		if len(s)>1:
			ssum = 1
			for i in range(len(s)):
				ssum = ssum*s[i]
			a = reshape(a,(ssum,))
		ret = sum(a)/self.nrow(a)
		return ret
	def variance(self,x):
		"return variance value of matrix"
		s = x.shape
		if len(s)>1:
			ssum = 1
			for i in range(len(s)):
				ssum = ssum*s[i]
			x = reshape(x,(ssum,))
		ret = sum(((x-self.mean(x))**2))/max([1,self.nrow(x)-1])
		return ret
	def sd(self,x):
		"return sd value of matrix"
		return(self.variance(x)**0.5)
	def vector(self,a,x):
		""" VECTOR(a;x) returns a list of length 'a' filled with values  for x.   If  there  are less then 'a' values, the value will be recycled,\n
		for example;
		     x=1,2,3,4
                     vector(2;x) returns 1,2
                     vector(6;x) returns 1,2,3,4,1,2
		     VECTOR(a) returns a vector filled with zeroes."""
		res = resize(x,(a,))
		return res.astype('f')
	#dimen function
	def dimen(self,a):
		""" return dimension of array"""
		b = a.shape
		return b[0]
	#fit exponential
	def expfit(self,x,obs,p,wt=array([0.0]),fixm=array([0.0])):
		"""Exponential Fitting. The exponential fit routine fits the X,Y data to the function:
		y(x) = p1  exp(p2  x) + p3 exp(p4 x) + ...
		First you  must specify the number of parameters, two for one exponential, three for one exponential plus a constant,four for two exponentials, etc.
		Then PyBLD requests initial estimates for the parameters.
		Note that for exponential decay, p2 and p4 ,etc. should be negative.
		The exponential function is non-linear in the parameters, 
		so the fitting procedure is an iterative one.
		This means that the program will find the best fitting parameters step by step,starting from the initial estimates that you supply.
		The closer these parameters are to the true values, the quicker the convergence. The algorithm is Marquardt_-Levenberg with step halving."""


		pybldc.cvar.fit_func = 0 #specify exponential fitting
		if self.show==0:
			pybldc.cvar.show_flag = 0
		self.corrmat = array([0]) #initialize corrmat and resmat
		self.fitresmat = array([0])
		if len(wt)!=len(obs):#no weight
			wt = zeros(obs.shape,'d')
			pybldc.cvar.fit_weight = 0
		else:
			pybldc.cvar.fit_weight = 1

		if len(fixm)!=len(p):# no fix
			fixm = zeros(p.shape,'d')
			pybldc.cvar.fit_const = 0
		else:
			if len(p)==1 and fixm[0]==0:#one parameter case
				fixm = zeros(p.shape,'d')
				pybldc.cvar.fit_const = 0
			else:
				pybldc.cvar.fit_const = 1
		res = pybldc.fit(0,x,obs,p,wt,fixm)
		fit_puse = self.dimen(p) - sum(fixm)
		res_p = res[0:(self.dimen(p))]
		res_se = res[(self.dimen(p)):(2*(self.dimen(p)))]
		self.corrmat = res[(2*(self.dimen(p))):(2*(self.dimen(p)) + int(fit_puse*fit_puse))]
		self.corrmat.shape = (int(fit_puse),int(fit_puse))
		self.fitresmat = res[(2*(self.dimen(p)) + int(fit_puse*fit_puse)):]
		self.fit_z = self.expf(x,res_p)
		pybldc.cvar.fit_func = 2 #specify general fitting
		pybldc.cvar.show_flag = 1
		pybldc.cvar.fit_weight = 0
		pybldc.cvar.fit_const = 0
		return(res_p,res_se)
	#  EXPo(X;A;beta) - sum of exponentials A(1)*exp(beta(1)*x) + ...
	def expo(self,x,a,beta):
		x2 = self.vec2mat(x)
		return(sum(self.tran(a*exp(beta*self.tran(x2))),axis=0))
	def expf(self,x,p):
		""" expf(x,p) - sum of exponentials  p[0]*exp(p[1]*x) + p[2]exp(... """
		return self.expo(x,p[0:2*(int(self.nrow(p)/2)):2],p[1:2*(int(self.nrow(p)/2)):2]) + self.odd(self.nrow(p))*p[self.nrow(p) - 1]
	# modular arithmetic  (x mod y) - remainder from x divided by y
	def mod(self,x,y):
		return x - y*int(x/y)
	def even(self,x):
		"""even(x) is the value x even (1=yes, 0=no)"""
		return equal(self.mod(x,2),0)
	def odd(self,x):
		"""odd(x) is the value x odd (1=yes, 0=no)"""
		return equal(self.mod(x,2),1)
	#vector to matrix
	def vec2mat(self,x):
		x2 = self.list2vec(x)
		sx = x2.shape
		if len(sx) != 1:
			return x2
		else:
			x2.shape = (1,sx[0])
			return x2
	#list to vector
	def list2vec(self,x):
		try:
			sx = x.shape
		except AttributeError:
			x = array(x,'f') #defaults is float
			return x
		return array(x)
	#exit pybld
	def exit(self):
		sys.exit()
	def img(self,xdim=0,ydim=0,zdim=0,tdim=1,px=0.0,py=0.0,pz=0.0,type=bldanaimg.TYPE_IMG_B):
		return bldanaimg.ANAIMG(xdim=xdim,ydim=ydim,zdim=zdim,tdim=tdim,px=px,py=py,pz=pz,type=type,view_cmd=self.view_cmd)
