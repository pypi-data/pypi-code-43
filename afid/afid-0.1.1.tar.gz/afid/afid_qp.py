#!/usr/bin/env python


import pandas as pd
import numpy as np
import scipy, sklearn
import os, sys, string, fileinput, glob, re, math, itertools, functools, copy, logging
import sklearn.decomposition, sklearn.preprocessing, sklearn.linear_model, sklearn.covariance
import cvxopt


loglevel = logging.WARNING


class AfidQP:
    """Provides a sklearn type fit+transform API for affine mapping of input data such that 
        the output data separates better under a L2 measure.

       This version is based on a Quadratic Programming Framework.
    """

    
    def __init__(self, mode, min_desired_corr=0.9, w_max_to_avg=20, params={}):
        """
        The typical use-pattern is:
          aqp = AfidQP(...) # parameters
          aqp.fit(...) # original data and side-information
          y = aqp.transform() # the transformed data

        mode: one of 'shear' or 'affine'. 
         'shear' does scaling+centering transformations only.
         'affine' first does a mapping to PCA space (you can specify n_components) 
            It then does a shearing transform in that space and then maps everything back to the
             regular space, the final space being an affine transformation 

        min_desired_corr: the minimum desired correlation between squared L2 distances in the original
           space and the transformed space. 
          For biological data with thousands of observations, try pretty high values. 
          The default is 0.9, but you might want to go all the way to 0.9995 as well. 
        
        w_max_to_avg: a parameter (>1) that increases the severity of remapping. 
          It sets the upper-bound on the ratio of w's largest element to w's avg element.
          Making it large will allow for more severe transformations. 
          In transcriptomic data, values of 30-100 should allow for it to be pretty high.
          To really constrain this, set it in the [1-5] range

        params: a dict of key-value pairs for code configuration. 
          You can ignore this on the first pass. The default values are pretty reasonable. 
          Here are the important ones:
           num_top_pca_components: (Default=None) number of PCA components to use when mode=="affine". 
              Default means use all.
           do_pca_whiten: (Default=False) when mode=="affine", should be PCA loadings be made 0-mean,1-variance?
           dist_npairs: (Default=2000000). How many pt-pairs to use for computing pairwise distances
               value=None means compute exhaustively over all n*(n-1)/2 pt-pairs. Not recommended for n>5000. 
               Otherwise, the given number of pt-pairs is sampled randomly. The sampling is done in a way in which
               each point will be represented roughly equally. 

        """        
        assert mode in ['shear', 'affine']
        assert w_max_to_avg > 0
        
        self._mode = mode
        self._w_max_to_avg = w_max_to_avg
        self._min_desired_corr = min_desired_corr
        self._std_scaler = None
        self._pca = None
        self._params = copy.deepcopy(params)

    
    
    def fit(self, d, sideinfo_val_list, sideinfo_type_list, sideinfo_wt_list = None):
        """
        d should be a numpy-type 2-D array. The rows are observations and the cols are variables. scanpy's .X works just fine.  

        sideinfo_val_list should be a list of the groupings (each numpy-type 1-d array) that you want to align the data towards.
          columns in scanpy's .obs variables work well (just remember to use .values)  

        sideinfo_type_list is a list of the same length as sideinfo_val_list. Each element should be one of 'categorical' or 'numeric'

        sideinfo_wt_list is an optional argument of user-specified wts for each grouping. If 'None', the wts are 1. 
          IMPORTANT: you can try to get a mapping that *disagrees* with the side_info instead of *agreeing*. 
            To do so, pass in a negative number (e.g., -1)  here.

        example usage:
           afp = AfidQP(..)
           # scobj is a scanpy/anndata obj
           afp.fit( scobj.X, [scobj.obs.col1.values, scobj.obs.col2.values], ["categorical", "numeric"], None) 
           or 
           # df is a pd.DataFrame, srs is a pd.Series, -1 means try to disagree
           afp.fit( df.values, [srs.values], ['numeric'], [-1]) 
        """
        assert len(sideinfo_val_list)>0 and len(sideinfo_type_list)
        if sideinfo_wt_list is not None: assert len(sideinfo_val_list) == len(sideinfo_wt_list)
        
        if self._mode=="shear":
            self._fit_shear(d, sideinfo_val_list, sideinfo_type_list, sideinfo_wt_list)
        else: #affine
            self._fit_affine(d, sideinfo_val_list, sideinfo_type_list, sideinfo_wt_list)

            
            
    def transform(self, d):
        """d should be a numpy 2-D array. 
            It can be a different dataset from the one used in fit(...) and no side-info is needed.
        """        
        if self._mode=="shear":
            assert d.shape[1] == len(self._wts)
            dx = self._std_scaler.transform(d)
            return np.multiply(dx, np.sqrt(np.maximum(np.array(self._wts),0)))
        else: #affine
            assert d.shape[1] == self._pca.components_.shape[1]
            dx = self._pca.transform(d)
            return np.multiply(dx, np.sqrt(np.maximum(np.array(self._wts),0)))
    

        
    def fit_transform(self, d, sideinfo_val_list, sideinfo_type_list, sideinfo_wt_list = None):
        """
        Does what you would expect. Look at doc for 'fit' and 'transform' for details
        """
        self.fit(d, sideinfo_val_list, sideinfo_type_list, sideinfo_wt_list)
        return self.transform(d)

    
    ######## "private" methods below. Not that Python cares... ########
    
    def _getDistances(self, D, G, nPointPairs):
        """
        Compute the various distances between point pairs in D
        D is a NxK numpy type 2-d array, with N points, each of K dimensions
        G is list, with each entry a 3-tuple: (g_val, g_type, gamma_g)
           each 3-tuple corresponds to one dimension of side-information
             g_val is Nx1 numpy type 1-d vector of values for the N points, in the same order as D
             g_type is "numeric" or "categorical"
             gamma_g is the relative wt you want to give this column. You can leave 
               it as None for all 3-tuples, but not for just some. If you leave them
               all as None, the system will set wts to 1  
        nPointPairs is the number of point pairs you want to evaluate over. If it is None,
             the system will generate over all possible pairs
        """
        ##############################
        # symbology
        # uv_dist = nPointPairs x K matrix of squared distances between point pairs, along K dimensions
        # uv_dist_mean = 1 x K vector: avg of uv_dist along each dimension 
        # uv_dist_centered = nPointPairs x K matrix with uv_dist_mean subtracted from each row
        # d0 = nPointPairs x 1 vector: squared distances in the current L2 space. row-wise sum of uv_dist
        # z_d0 = z-scored version of  d0
        # dg = nPointPairs x 1 vector: squared distances (or class-match scores) for grouping g
        # z_dg = z-scored version of dg
        ##############################
        
        logging.info ("Flag 232.12 ", len(G), G[0][0].shape, G[0][1], G[0][2])
        gamma_gs_are_None = True
        for i,g in enumerate(G):
            g_val, g_type, gamma_g = g
            
            assert g_type in ['categorical','numeric']
            
            if i==0 and gamma_g is not None:
                gamma_gs_are_None = False
            if gamma_g is None: assert gamma_gs_are_None
            if gamma_g is not None: assert (not gamma_gs_are_None)
            

        N, K = D.shape[0], D.shape[1]

        if nPointPairs is not None:
            j_u = np.random.randint(0, N, int(3*nPointPairs))
            j_v = np.random.randint(0, N, int(3*nPointPairs))
            valid = j_u < j_v  #get rid of potential duplicates (x1,x2) and (x2,x1) as well as (x1,x1)
            i_u = (j_u[valid])[:nPointPairs]
            i_v = (j_v[valid])[:nPointPairs]
        else:
            x = pd.DataFrame.from_records(list(itertools.combinations(range(N),2)), columns=["u","v"])
            x = x[x.u < x.v]
            i_u = x.u.values
            i_v = x.v.values
            
        # NxK matrix of square distances along dimensions
        uv_dist = (D[i_u,:].astype(np.float64) - D[i_v,:].astype(np.float64))**2 #(D[i_u,:].toarray() - D[i_v,:].toarray())**2

        # scale things so QP gets ~1-3 digit numbers, very large or very small numbers cause numerical issues         
        uv_dist = uv_dist/ (np.sqrt(uv_dist.shape[0])*uv_dist.ravel().mean())  
        
        # center uv_dist along each dimension
        uv_dist_mean = uv_dist.mean(axis=0) #Kx1 vector, this is the mean of (u_i - v_i)^2, not sqrt((u_i - v_i)^2) 
        uv_dist_centered = uv_dist - uv_dist_mean
        
        # square distances in the current metric space
        d0 = uv_dist.sum(axis=1) # Nx1
        z_d0  = (d0 - d0.mean())/d0.std()

        l_z_dg = []
        for g_val, g_type, gamma_g in G:
            logging.info ("Flag 201.80 ", g_val.shape, g_type, gamma_g)
            if g_type == "categorical":
                dg = 1.0*( g_val[i_u] != g_val[i_v]) #1.0*( g_val[i_u].toarray() != g_val[i_v].toarray())
            else:
                dg = (g_val[i_u].astype(np.float64) - g_val[i_v].astype(np.float64))**2   #(g_val[i_u].toarray() - g_val[i_v].toarray())**2            

            z_dg = (dg - dg.mean())/dg.std()
            if gamma_g is not None:
                z_dg *= gamma_g
                
            l_z_dg.append(z_dg)

        logging.info ("Flag 201.99 ", uv_dist_centered.shape, z_d0.shape, len(l_z_dg), l_z_dg[0].shape)
        logging.info ("Flag 201.991 ", uv_dist_centered.mean(axis=0))
        logging.info ("Flag 201.992 ", uv_dist_centered.std(axis=0))
        logging.info ("Flag 201.993 ", z_d0[:10], z_d0.mean(), z_d0.std())
        logging.info ("Flag 201.994 ", l_z_dg[0][:10], l_z_dg[0].mean(), l_z_dg[0].std())
        return (uv_dist_centered, z_d0, l_z_dg)


    
    
    def _prepareQPterms(self, uv_dist_centered, z_d0, l_z_dg):
        nPointPairs = uv_dist_centered.shape[0]
        
        l_g = []
        for i,z_dg in enumerate(l_z_dg):
            l_g.append( np.sum(uv_dist_centered * z_dg[:,None], axis=0) )
            
        q1 = l_g[0]
        for v in l_g[1:]:
            q1 += v
        
        P1 = np.matmul( uv_dist_centered.T,  uv_dist_centered)

        g1 = np.sum(uv_dist_centered * z_d0[:,None], axis=0)
        h1 = np.sum(g1)

        return (P1, q1, g1, h1, nPointPairs)

    

    def _computeSolutionFeatures(self, w, P1, q1, g1, nPointPairs):
        K = len(w)
        #print ("Flag 569.20 ", w.shape, P1.shape, q1.shape, g1.shape, np.reshape(w,(1,K)).shape)
        
        newmetric_sd = np.sqrt( np.matmul(np.matmul(np.reshape(w,(1,K)), P1), np.reshape(w,(K,1)))[0] / nPointPairs)
        oldnew_corr = (np.dot(w,g1)/nPointPairs)/newmetric_sd

        groupcorr_score = (np.dot(w,q1)/nPointPairs)/newmetric_sd
        return {"w": w, "distcorr": oldnew_corr[0], "objval": groupcorr_score[0]}
        

    
    def _doQPSolve(self, P1, q1, g1, h1, nPointPairs, lambda1, alpha, beta):
        #https://cvxopt.org/examples/tutorial/qp.html and https://courses.csail.mit.edu/6.867/wiki/images/a/a7/Qp-cvxopt.pdf
        #  the cvx example switches P & q to Q & p
        
        from cvxopt import matrix, solvers
        solvers.options["show_progress"] = False


        K = len(g1)

        I_K = np.diagflat(np.ones(K).astype(np.float64))
        #P = 2* (lambda1*matrix(I_K) + beta*matrix(P1))
        P = matrix(2* ((I_K*lambda1) + (P1*beta)))
        
        q = -matrix(q1 + 2*lambda1*np.ones(K))
        
        G0 = np.zeros((K+1,K)).astype(np.float64)
        for i in range(K):
            G0[i,i] = 1.0
        G0[-1,:] = g1
        #print ("Flag 543.66 ", G0.shape, I_K.shape, g1.shape)
                
        G = -matrix(G0) #first K rows say -w_i <= 0. The K+1'th row says -corr(newdist,olddist) <= -const
        h = matrix(np.zeros(K+1))
        h[-1] = -alpha*h1
        
        
        logging.debug("Flag 543.70 ", P1.shape, q1.shape, g1.shape, h1, nPointPairs, lambda1 , alpha, beta, P.size, q.size, G0.shape, G.size, h.size) #K, P.size, q.size, G.size, h.size)
        sol=solvers.qp(P, q, G, h)
        solvers.options["show_progress"] = True

        w = np.array(sol['x']).ravel()
        s = self._computeSolutionFeatures(w, P1, q1, g1, nPointPairs)
        return s


    def _summarizeSoln(self, soln, free_params):
        retl = []
        retl.append(("w_max_to_avg", (max(soln["w"])/np.nanmean(soln["w"]))))
        retl.append(("w_num_zero_dims", sum(soln["w"] < 1e-5)))
        retl.append(("distcorr", soln["distcorr"]))
        retl.append(("objval", soln["objval"]))
        retl.append(("lambda", free_params["lambda"]))
        retl.append(("alpha", free_params["alpha"]))
        retl.append(("beta", free_params["beta"]))
        
        return retl
                    

    
    def _doQPiterations(self, P1, q1, g1, h1, nPointPairs, max_w_wt, min_desired_oldnew_corr):
        solutionList = []

        if afid_loglevel >= logging.WARNING: print('Starting (each dot is 10%): ', end='', flush=True)

        alpha = 1.0  #start from one (i.e. no limit on numerator and make it bigger)
        while alpha > 1e-5:
            soln, param_settings = self._iterateQPLevel1(P1, q1, g1, h1, nPointPairs, max_w_wt, min_desired_oldnew_corr, alpha)
            
            if soln is not None and soln["distcorr"] >= min_desired_oldnew_corr:
                solutionList.append((-soln["objval"], soln, param_settings))

            alpha -= 0.1
            if afid_loglevel >= logging.WARNING: print('.', end='', flush=True)
        try:
            solutionList.sort() #find the highest score

            logging.info("Flag 103.60 alpha")
            for x in solutionList:
                logging.info("Flag 103.601 ", self._summarizeSoln(x[1], x[2]))
                
            if afid_loglevel >= logging.WARNING: print('\n', end='', flush=True)
            return (solutionList[0][1], solutionList[0][2])
        except:
            if afid_loglevel >= logging.WARNING: print('\n', end='', flush=True)
            return (None, {})

        

        
    def _iterateQPLevel1(self, P1, q1, g1, h1, nPointPairs, max_w_wt, min_desired_oldnew_corr, alpha):
        solutionList = []

        beta = 1e6  #start from a large value and go towards zero (a large value means the denominator will need to be small)
        while beta > 1e-6:
            try:
                soln, param_settings = self._iterateQPLevel2(P1, q1, g1, h1, nPointPairs, max_w_wt, alpha, beta)
            except Exception as e:
                logging.warning ("Flag 110.50 crashed in _iterateQPLevel2", P1.size, q1.size, g1.size, max_w_wt, alpha, beta)
                print (e)
                beta *= 0.5
                continue
            
            if soln["distcorr"] >= min_desired_oldnew_corr:
                solutionList.append((-soln["objval"], soln, param_settings))

            beta *= 0.5
        
        try:
            solutionList.sort() #find the highest score
            
            logging.info("Flag 110.60 beta")
            for x in solutionList:
                logging.info("Flag 110.601 ", self._summarizeSoln(x[1],x[2]))

            return (solutionList[0][1], solutionList[0][2])
        except:
            return (None, {})



    def _iterateQPLevel2(self, P1, q1, g1, h1, nPointPairs, max_w_wt, alpha, beta):
        lo=1e-10 #1e-6
        solLo = self._doQPSolve(P1, q1, g1, h1, nPointPairs, 1/lo, alpha, beta)
        scalerangeLo = (max(solLo["w"])/np.nanmean(solLo["w"]))
        
        hi=1e9 #1e6
        solHi = self._doQPSolve(P1, q1, g1, h1, nPointPairs, 1/hi, alpha, beta)
        scalerangeHi = (max(solHi["w"])/np.nanmean(solHi["w"]))

        if scalerangeHi < max_w_wt:
            solZero = self._doQPSolve(P1, q1, g1, h1, nPointPairs, 0, alpha, beta)
            scalerangeZero = (max(solZero["w"])/np.nanmean(solZero["w"]))
            if scalerangeZero < max_w_wt:
                return solZero, {"lambda": 0, "alpha": alpha, "beta": beta} 
            else:
                return solHi, {"lambda": 1/hi, "alpha": alpha, "beta": beta}
            
        if scalerangeLo > max_w_wt: return solLo, {"lambda": 1/lo, "alpha": alpha, "beta": beta}
        
        niter=0
        while (niter < 60 and (hi/lo -1)>0.001):
            mid = np.exp((np.log(lo)+np.log(hi))/2)
            solMid = self._doQPSolve(P1, q1, g1, h1, nPointPairs, 1/mid, alpha, beta)
            scalerangeMid = (max(solMid["w"])/np.nanmean(solMid["w"]))
            
            if (scalerangeLo <= max_w_wt <= scalerangeMid):
                hi = mid
                scalerangeHi = scalerangeMid
                solHi = solMid
            else:
                lo = mid
                scalerangeLo = scalerangeMid
                solLo = solMid

            niter += 1
            logging.debug ("Flag 42.113 ", niter, lo, mid, hi, max(solLo["w"]), min(solLo["w"]), max(solHi["w"]), min(solHi["w"]), scalerangeMid)
        return solLo, {"lambda": 1/lo, "alpha": alpha, "beta": beta}        

    

    def _fit_helper(self, dx, sideinfo_val_list, sideinfo_type_list, sideinfo_wt_list):
        nPointPairs = self._params.get("dist_npairs", 2000000)
        sample_rate = self._params.get("dist_df_frac", 1.0)

        w_max_to_avg= self._w_max_to_avg
        min_desired_corr = self._min_desired_corr

        N = dx.shape[0]

        logging.info ("Flag 102.30 ", dx.shape, sideinfo_val_list, sideinfo_type_list, sideinfo_wt_list)
        
        G = []
        for i in range(len(sideinfo_val_list)):
            G.append((sideinfo_val_list[i].copy(), sideinfo_type_list[i], None if sideinfo_wt_list is None else sideinfo_wt_list[i]))

        if sample_rate < 0.9999999: 
            idx = np.random.choice(N, size=int(sample_rate*N), replace=False)
            dx = dx[idx,:]
            for i, gx in enumerate(G):
                G[i] = (gx[0][idx], gx[1], gx[2])

                
        uv_dist_centered, z_d0, l_z_dg = self._getDistances(dx, G, nPointPairs)
        P1, q1, g1, h1, nPointPairs1 = self._prepareQPterms(uv_dist_centered, z_d0, l_z_dg)
        
        soln, free_params = self._doQPiterations(P1, q1, g1, h1, nPointPairs1, scaleRange, min_desired_corr)
        
        if soln is None:
            raise Exception("Couldn't find valid solution to QP")
        
        if afid_loglevel >= logging.WARNING: print ("Final solution: ", self._summarizeSoln(soln, free_params))
        return soln["w"].ravel(), self._summarizeSoln(soln, free_params)
    
        
    def _fit_shear(self, d, sideinfo_val_list, sideinfo_type_list, sideinfo_wt_list):

        self._std_scaler = sklearn.preprocessing.StandardScaler() 
        dx1 = d.copy()
        dx = self._std_scaler.fit_transform(dx1)

        s, sl = self._fit_helper(dx, sideinfo_val_list, sideinfo_type_list, sideinfo_wt_list)
        
        self._wts = np.maximum(s,0)
        self._soln_info = dict(sl)

        
    def _fit_affine(self, d, sideinfo_val_list, sideinfo_type_list, sideinfo_wt_list):
        do_pca_whiten = self._params.get("do_pca_whiten",0)>0
        ncomp = self._params.get("num_top_pca_components",None) #default is all
        
        self._pca = sklearn.decomposition.PCA(n_components=ncomp, whiten=do_pca_whiten)
        dx1 = d.copy()
        dx = self._pca.fit_transform(dx1)
        
        s, sl = self._fit_helper(dx, sideinfo_val_list, sideinfo_type_list, sideinfo_wt_list)

        self._wts = np.maximum(s,0)
        self._soln_info = dict(sl)



