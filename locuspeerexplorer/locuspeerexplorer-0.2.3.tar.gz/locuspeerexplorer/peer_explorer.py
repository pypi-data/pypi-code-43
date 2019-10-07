import collections
from fastdtw import fastdtw
import numpy as np
import pandas as pd
import operator
from scipy.spatial import distance
from scipy.spatial.distance import euclidean
from . import params


class PeerExplorer:

    # Valid distance metrics to compute
    DISTANCE = ['euclidean', 'correlation', 'cosine']

    # List of all metrcs
    METRIC_NAMES = ['PC_EMPL', 'PC_ESTAB', 'LQ_EMPL_ESTAB',
                    'LQ_EMPL_ESTAB_RANK', 'WM_ESTAB', 'PRES_ESTAB']

    # Metric used to compute top industries for each MSA
    TOP_INDUSTRIES_METRIC = 'PC_ESTAB'
    # Metric used to find FM strengths and weaknesses
    STRENGTH_METRIC = "LQ_EMPL_ESTAB_RANK"
    # Metric used to find valid FM for strengths and weaknesses based on binary presence
    BINARY_PRESENCE_METRIC = 'PRES_ESTAB'

    def __init__(self, msa, year):

        self.msa = msa
        self.year = year

    def get_geographic_peers(self, n_peers):
        """
        Find the n_peers based on the average distance between county_distances
        """
        omb = omb[['FIPS', 'CBSA_CODE']]
        d = omb.set_index('FIPS').to_dict()
        d = d['CBSA_CODE']
        county_distances = county_distances[county_distances['county1'].isin(
            list(d))]
        county_distances = county_distances[county_distances['county2'].isin(
            list(d))]
        new_distances = county_distances.replace({"county1": d})
        new_distances = new_distances.replace({'county2': d})
        msas = sorted(list(set(data['MSA'])))
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
        peers = list(geo_distance_df[self.geo_distance['msa1'] == self.msa].head(
            n_peers)['msa2'])
        return peers

    def get_industry_peers(self, fms, n_peers):
        pass

    def get_outcomes_peers(self, outcomes, n_peers):
        pass

    def get_top_n_fms_peers(self, n_fms, n_peers):
        pass

    def get_distinguished_feat_peers(self, n_feat, n_peers):
        pass
