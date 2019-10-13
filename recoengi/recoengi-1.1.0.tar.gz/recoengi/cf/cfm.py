from scipy import sparse
from sklearn.preprocessing import normalize
import numpy as np
import logging
from .cosimtop import cosimtop

class CFM:

    '''
    Preferences Matrix Class
    '''
    

    def __init__(self, M):

        '''
        Initialization. 
        :param M: Preferences matrix, each row represents a user, each column represents the product.  
        '''
        
        # Computations are performed in sparse matrices in order to hold more data. 
        self.M = sparse.csr_matrix(M)
        logging.debug("M matrix has shape " + str(self.M.shape[0]) + "x" + str(self.M.shape[1]) + ".")


    def computeSimilarityMatrix(self, bln_bin = False, bln_norm = True, flt_ths = 0.0, ntop = None, flt_lb = -1):

        '''
        Compute the cosine similarity matrix.
        :param bln_bin: Binarize each matrix entry? If True, each entry will be binarized according to the flt_ths. 
        :param bln_norm: Should the output matrix entries be constrained in the interval [-1, +1]? 
        :param flt_ths: Threshold used by the binarization. 
        :param ntop: How many most similar users to keep for each user? If None, every similarity coefficient will be kept. Set this parameter to take advantage of the sparse matrix memory optimization. 
        :param flt_lb: Lower bound value for the output similarity matrix entries. 
        '''

        if ntop is None:
            ntop = self.M.shape[0]

        self.bln_bin = bln_bin
        self.bln_norm = bln_norm
        self.flt_ths = flt_ths
        self.ntop = ntop

        self.B = self.M.copy()
        self.B.data = (self.B.data > flt_ths) + 0.0
        logging.debug("B matrix has shape " + str(self.B.shape[0]) + "x" + str(self.B.shape[1]) + ".")
        logging.debug("B matrix has sparsity " + str(sum(self.B.data)/(self.B.shape[0] * self.B.shape[1])*100) + "%.")

        if bln_bin:
            self.S = self.B.copy()
        else:
            self.S = self.M.copy()

        if bln_norm:
            self.S = normalize(self.S, norm='l2', axis=1)

        logging.debug("Computing the similarity matrix S ...")
        self.S = cosimtop(self.S, self.S.transpose(), ntop = ntop, lower_bound=flt_lb)
        logging.debug("S matrix has shape " + str(self.S.shape[0]) + "x" + str(self.S.shape[1]) + ".")
    

    def computeScores(self):

        '''
        Compute the scores for each couple (user, product). 
        '''

        logging.debug("Computing the matrix SNORMALIZED ...")
        self.SNORMALIZED = self.S.copy()
        self.SNORMALIZED = self.SNORMALIZED - sparse.diags(self.SNORMALIZED.diagonal(), format="csr")
        self.SNORMALIZED = normalize(self.SNORMALIZED, norm='l1', axis=1)
        logging.debug("Computing the matrix SCORES ...")
        self.SCORES = self.SNORMALIZED * self.B
        logging.debug("SCORES matrix has shape " + str(self.SCORES.shape[0]) + "x" + str(self.SCORES.shape[1]) + ".")


    def computeAmounts(self):

        '''
        Compute the averaged amount for each couple (user, product).
        '''

        logging.debug("Computing the matrix AMOUNTS ...")
        self.AMOUNTS = self.SNORMALIZED * self.M
        logging.debug("AMOUNTS matrix has shape " + str(self.AMOUNTS.shape[0]) + "x" + str(self.AMOUNTS.shape[1]) + ".")
    

    def computePerformances(self):

        '''
        Compute model performances. 
        '''

        # TODO: add out of the sample testing. 

        logging.debug("Computing the performances ...")

        self.avg_global_scores_diff = abs(self.SCORES - self.B).mean()
        self.avg_pos_scores_diff = abs(self.SCORES[self.B > 0.01] - 1).mean()
        logging.debug("Average global scores difference: " + str(self.avg_global_scores_diff) + ".")
        logging.debug("Average positive scores difference: " + str(self.avg_pos_scores_diff) + ".")

        if self.avg_pos_scores_diff >= 0.5:
            logging.warning("The scores model could not perform better than a random model! Further tests needed!")

        self.avg_global_amounts_diff = abs(self.AMOUNTS - self.M).mean()
        tmp_positive_amounts = self.AMOUNTS[self.B > 0.01]
        tmp_real_positive_amounts = self.M[self.B > 0.01]
        tmp_random_model_pred = tmp_positive_amounts.mean()
        self.avg_pos_amounts_diff_perc = (abs(tmp_positive_amounts - tmp_real_positive_amounts) / tmp_real_positive_amounts).mean() * 100
        self.avg_pos_ampunts_diff_perc_random = (abs(tmp_random_model_pred - tmp_real_positive_amounts) / tmp_real_positive_amounts).mean() * 100
        logging.debug("Average global amounts difference: " + str(self.avg_global_amounts_diff) + ".")
        logging.debug("Average positive amounts difference percentage: " + str(self.avg_pos_amounts_diff_perc) + "%.")
        logging.debug("Average positive amounts difference percentage of a random model: " + str(self.avg_pos_ampunts_diff_perc_random) + "%.")

        if self.avg_pos_amounts_diff_perc >= self.avg_pos_ampunts_diff_perc_random:
            logging.warning("The amounts model could not perform better than a random model! Further tests needed!")

    
    def computeEverything(self, bln_bin = False, bln_norm = True, flt_ths = 0.0, ntop = None, flt_lb = -1):

        '''
        Method for lazy people like me. :)
        :param bln_bin: Binarize each matrix entry? If True, each entry will be binarized according to the flt_ths. 
        :param bln_norm: Should the output matrix entries be constrained in the interval [-1, +1]? 
        :param flt_ths: Threshold used by the binarization. 
        :param ntop: How many most similar users to keep for each user? If None, every similarity coefficient will be kept. Set this parameter to take advantage of the sparse matrix memory optimization. 
        :param flt_lb: Lower bound value for the output similarity matrix entries. 
        '''

        self.computeSimilarityMatrix(bln_bin = bln_bin, bln_norm = bln_norm, flt_ths = flt_ths, ntop = ntop, flt_lb = flt_lb)
        self.computeScores()
        self.computeAmounts()
        self.computePerformances()