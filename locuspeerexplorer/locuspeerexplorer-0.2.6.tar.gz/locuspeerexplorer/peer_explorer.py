import collections
import numpy as np
import pandas as pd
import operator
from scipy.spatial import distance
from scipy.spatial.distance import euclidean
import locuspeerexplorer.params


class PeerExplorer:

    # List of all metrcs
    METRIC_NAMES = ['PC_EMPL', 'PC_ESTAB', 'LQ_EMPL_ESTAB',
                    'LQ_EMPL_ESTAB_RANK', 'WM_ESTAB', 'PRES_ESTAB']

    def __init__(self, msa, year, metrics_outcomes, omb, county_distances):

        self.msa = msa
        self.year = year
        self.data = metrics_outcomes
        self.data = self.data[self.data['YEAR'] == self.year]
        self.omb = omb
        self.county_distances = county_distances

        self.distance_peers = None
        self.distinguishing_features = None
        self.ranked_fms = None

    def get_geographic_peers(self, n_peers):
        """
        Find the n_peers based on the average distance
        between each county in the MSA

        :param n_peers: number of peers to return
        :type n_peers: int
        :return: geographic peers
        :rtype: list
        """
        if self.distance_peers is None:
            omb = (self.omb)[['FIPS', 'CBSA_CODE']]
            d = omb.set_index('FIPS').to_dict()
            d = d['CBSA_CODE']
            county_distances = (self.county_distances)[(self.county_distances)['county1'].isin(
                list(d))]
            county_distances = county_distances[county_distances['county2'].isin(
                list(d))]
            new_distances = county_distances.replace({"county1": d})
            new_distances = new_distances.replace({'county2': d})
            msas = sorted(list(set(self.data['MSA'])))
            new_distances = new_distances[new_distances['county1'].isin(msas)]
            new_distances = new_distances[new_distances['county2'].isin(msas)]
            new_distances.columns = ['msa1', 'mi_to_county', 'msa2']
            # we now have a df that replaced counties with msas
            # now we get rid of msa1 and msa2 that are the same
            new_distances = new_distances.query("msa1 != msa2")
            # now we average the distances from county level for msa level distances
            geo_distances = new_distances.groupby(['msa1', 'msa2']).mean()
            geo_distances = geo_distances.sort_values("mi_to_county")
            geo_distances.reset_index(inplace=True)
            geo_to_msa = geo_distances[geo_distances['msa1'] == self.msa]
            self.distance_peers = list(geo_to_msa['msa2'])
        return (self.distance_peers)[:n_peers]

    def get_peers_from_input(self, n_peers, fms=[], outcomes=[]):
        """
        Find the n_peers based on the similarity in all specified FMS
        and outcomes among all MSAs

        :param fms: FMs used to identify peers
        :type fms: list
        :param outcomes: Outcomes used to identify peers
        :type outcomes: list
        :param n_peers: Number of peers to return
        :type n_peers: int
        :return: User specified peers
        :rtype: list
        """
        cols = [x+'-PC_EMPL' for x in fms] + outcomes
        return self._peers_euclidean_distance(self.data,
                                              cols, self.msa, n_peers)

    def get_top_n_fms_peers(self, n_fms, n_peers):
        """
        Get peers using the top n_fms FMs ranked by the presence of the FMs in
        the MSA

        :param n_fms: Number of FMs to use
        :type n_fms: int
        :param n_peers: Number of peers to return
        :type n_peers: int
        :return: Peers based on most present FMs in the MSA
        :rtype: list
        """
        if self.ranked_fms is None:
            df = self.data.copy()
            pc_fms = [c for c in df.columns if '-PC_EMPL' in c]
            df_msa = df[pc_fms][df['MSA'] == self.msa].T.reset_index()
            df_msa.columns = ['FMs', 'PC_EMPL']
            df_msa.sort_values('PC_EMPL', inplace=True)
            self.ranked_fms = list(df_msa['FMs'])
        return self._peers_euclidean_distance(self.data,
                                              self.ranked_fms[:n_fms],
                                              self.msa, n_peers)

    def get_distinguishing_features_peers(self, n_feat, n_peers):
        """Get peers using the FMs for which the MSA has a concentration of
        pc_estab significantly higher or significantly lower than average

        :param n_feat: Number of FMs to use
        :type n_feat: int
        :param n_peers: Number of peers to return
        :type n_peers: int
        :return: Peers based on the distinguishing features of the MSA
        :rtype: list
        """
        if self.distinguishing_features is None:
            df = self.data.copy()
            count_msa = df.MSA.value_counts().sum()

            # Get FMs that are present in at least 50% of all MSAs
            # by summing PRES_ESTAB for all MSA, and taking fms for which
            # SUM_PRES >= count_msa/2
            df_pres = df[[c for c in df.columns if 'PRES_ESTAB' in c]].T
            df_sum_pres = df_pres.sum(axis=1).reset_index()
            df_sum_pres.columns = ['FMs', 'SUM_PRES']
            df_sum_pres = df_sum_pres.query("SUM_PRES >= @count_msa/2")
            present_fms = list(df_sum_pres.FMs)
            cols = [c.split('-')[0]+'-LQ_EMPL_ESTAB_RANK' for c in present_fms]

            # Get 10 FMs for which MSA has a significantly higher or lower than
            # average number of estab
            df_msa = df[cols][df['MSA'] == self.msa].T.reset_index()
            df_msa.columns = ['FMs', 'RANK']
            df_msa['RANK'] = df_msa.apply(lambda x: min(count_msa-x.RANK, x.RANK),
                                          axis=1)
            df_msa.sort_values('RANK', inplace=True)
            distinguishing_fms = [
                c.split('-')[0]+'-PC_EMPL' for c in list(df_msa['FMs'])]
            self.distinguishing_features = distinguishing_fms
        return self._peers_euclidean_distance(self.data,
                                              self.distinguishing_features[:n_feat],
                                              self.msa, n_peers)

    def _peers_euclidean_distance(self, df, cols, msa, n_peers):
        """
        Compute the euclidean distance to msa for all rows (=all MSAs)
        on all columns in cols
        
        :param df: Data
        :type df: dataframe
        :param cols: Columns to use to compute the distance
        :type cols: list
        :param msa: MSA to compute the distance to
        :type msa: int
        :param n_peers: Number of peers to return
        :type n_peers: int
        :return: List of peers
        :rtype: list
        """
        cols.append('MSA')
        df = (df.copy())[cols]
        df = df.set_index('MSA')
        df = df.pow(2)
        df_msa = df.loc[self.msa]
        df_dist = ((df-df_msa).sum(axis=1)).pow(0.5)
        df_dist = df_dist.reset_index()
        df_dist.columns = ['MSA', 'DIST']
        df_dist.sort_values('DIST', inplace=True)
        peers = list(df_dist.head(n_peers)['MSA'])
        return peers
