import collections
from fastdtw import fastdtw
import numpy as np
import pandas as pd
import operator
from scipy.spatial import distance
from scipy.spatial.distance import euclidean
from . import params


class PeerExplorer:
    """
    Given an MSA and a year, this class groups different kinds (general, industrial, outcome) of peer MSAs.
    The class also requires the dataframes of 3 files: metrics_outcomes.csv, omb_msa_1990_2018.csv, sf12010countydistance500miles.csv

    Use this class as follows:
    lpe = PeerExplorer(<your MSA>, [<2015 or 2016>], [opt:<FMs of interest>],[opt:<outcomes of interest>])
    lpe.compute_distance(data, omb, county_distances)  # the 3 aforementioned dataframes
    if general:
        lpe.find_general_peers(<num peers>) #searches over all peers
    elif industrial:
        lpe.find_industry_peers(<num peers>) #searches for peers only using the previously specified <FMs of interest>
    elif outcomes:
        lpe.find_outcome_peers(<num peers>) #searches for peers only using the previously specified <outcomes of interest>
    """
    # Valid distance metrics to compute

    DISTANCE = ['euclidean', 'braycurtis', 'canberra', 'chebyshev',
                'cityblock', 'correlation', 'cosine', 'minkowski']

    # List of all metrcs
    METRIC_NAMES = ['PC_EMPL', 'PC_ESTAB', 'LQ_EMPL_ESTAB',
                    'LQ_EMPL_ESTAB_RANK', 'WM_ESTAB', 'PRES_ESTAB']
    # Metric used to compute top industries for each MSA
    TOP_INDUSTRIES_METRIC = 'PC_ESTAB'
    # Metric used to find FM strengths and weaknesses
    STRENGTH_METRIC = "LQ_EMPL_ESTAB_RANK"
    # Metric used to find valid FM for strengths and weaknesses based on binary presence
    BINARY_PRESENCE_METRIC = 'PRES_ESTAB'
    # Number of top MSAs to find
    N_TOP_MSA = 10

    def __init__(self, msa, years, fms=[], outcomes=[], year_gap=[], general_peer_metric='fm', dist_func='euclidean'):
        """
        params:
            msa (int): MSA to query
            years (list): list of years of interest
            fms (list): list of fms of interest
            outcomes (list): list of outcomes of interest
            year_gap (list): list of years to find ancestral peers
            dist_func (string): method to calculate the distance (default='euclidean')
        """
        # Save data to class
        self.raw_data = None
        self.data = None
        self.omb = None
        self.county_distances = None
        self.msa = msa
        self.years = years
        self.fms = [f'{c}-LQ_EMPL_ESTAB' for c in fms] + [f'{c}-PC_ESTAB' for c in
                                                          fms]  # [f'{c}-LQ_EMPL_ESTAB_RANK' for c in fms] + [f'{c}-PC_ESTAB' for c in fms]
        self.outcomes = outcomes
        self.dist_func = self._get_distance_function(dist_func)
        self._year_gap = sorted(year_gap)
        # Save results to class
        self._industry_distance_dict = None
        self._outcome_distance_dict = None
        self._ancestral_industry_dict = None
        self._ancestral_outcome_dict = None
        self._geo_distance_df = None
        self._top_industries_dict = None
        self._state_peers = None
        self._strengths = None
        self._weaknesses = None
        self._state_strengths = None
        self._state_weaknesses = None
        self._msa_strengths = None
        self._msa_weaknesses = None
        self._fms_to_negate = []
        self._general_dict = None
        self._general_peer_metric = general_peer_metric
        self._average_distance = {}

    def compute_distance(self, dataframe, omb, county_distances=None):
        """
        This function is always called to make peer groups.
        compute all the distances the users required, specified by the inputs
        params:
            dataframe - {dataframe} data that contains FMs and outcomes data
            omb - {dataframe} county level data (name and code)
            county_distances - {dataframe} physical distance data between counties
        returns:
            none, but will fill the attribute of multiple dictionaries specified by the user's requirement
        """
        # save raw data
        self.raw_data = dataframe
        # standardize all the columns in the metrics_outcomes dataframe
        data = self._standardize(dataframe)

        # save data to class
        self.data = data
        self.omb = omb
        if county_distances is not None:
            self.county_distances = county_distances

        allowed_codes = set(omb.loc[omb.YEAR.isin(self.years)].CBSA_CODE)
        assert self.msa in allowed_codes, "CBSA code does not exist for year range entered"
        # user inputs a list of FMs, and only wants to look at the distances point in time
        if self.fms and len(self.years) == 1:
            # call point in time compute distance function
            self._industry_distance_dict = self._compute_distance(
                data, self.fms, (self.years[0], self.years[0]))

        # user inputs a list of outcomes, and only wants to look at the distances point in time
        if self.outcomes and len(self.years) == 1:
            # call point in time compute distance function
            self._outcome_distance_dict = self._compute_distance(
                data, self.outcomes, (self.years[0], self.years[0]))

        # user inputs a list of FMs, and only wants to look at the distances
        # in time series, basically computing the similarity between the shapes
        # of two time series data
        if self.fms and len(self.years) > 1 and not self._year_gap:
            # make sure _year_gap is [] so that you are not looking at ancestral peers
            self._industry_distance_dict = self._compute_ts_distance(
                data, self.fms, self._year_gap)

        # user inputs a list of outcomes, and only wants to look at the distances
        # in time series
        if self.outcomes and len(self.years) > 1 and not self._year_gap:
            # make sure _year_gap is [] so that you are not looking at ancestral peers
            self._outcome_distance_dict = self._compute_ts_distance(
                data, self.outcomes, self._year_gap)

        # user wants to look at the distances between point-in-time peers in FMs
        if self.fms and len(self.years) == 1 and self._year_gap:
            # make sure that _year_gap is NOT [] so that you can look at ancestral peers
            self._ancestral_industry_dict = self._compute_distance(
                data, self.fms, self._year_gap)

        # user wants to look at the distances between point-in-time peers in outcomes
        if self.outcomes and len(self.years) == 1 and self._year_gap:
            # make sure that _year_gap is NOT [] so that you can look at ancestral peers
            self._ancestral_outcome_dict = self._compute_distance(
                data, self.outcomes, self._year_gap)

        # user wants to look at distances between time series peers in FMs
        if self.fms and len(self.years) > 1 and self._year_gap:
            # ancestral peers
            self._ancestral_industry_dict = self._compute_ts_distance(
                data, self.fms, self._year_gap)

        # user wants to look at distances between time series peers in outcomes
        if self.outcomes and len(self.years) > 1 and self._year_gap:
            # ancestral peers
            self._ancestral_outcome_dict = self._compute_ts_distance(
                data, self.outcomes, self._year_gap)

        # geographical distances
        if county_distances is not None:
            self._geo_distance_df = self._compute_geo_distance_df(
                data, omb, county_distances)
        self._state_peers = self._compute_state_peers(data, omb)

        # strengths, weaknesses, general peers
        self._fms_to_negate = self._find_fms_to_negate(dataframe)
        self._strengths, self._weaknesses = \
            self._find_strengths_weaknesses(
                dataframe, functional=(self._general_peer_metric == 'fm'))

        state_data = dataframe[dataframe['MSA'].isin(self._state_peers)]
        # state strengths and state weaknesses
        self._state_strengths, self._state_weaknesses = \
            self._find_strengths_weaknesses(
                state_data, functional=(self._general_peer_metric == 'fm'))

        # msa strengths and msa weaknesses
        self._msa_strengths, self._msa_weaknesses = self._find_strengths_weaknesses_within_msa(
            dataframe)

        # genearl peers
        self._general_dict = self._compute_general_distances(data)

        if not self._top_industries_dict:
            self.compute_top_industries(dataframe, n_fms=10, compare_growth_year=None,
                                        metric=self.TOP_INDUSTRIES_METRIC)
        return

    def _find_strengths_weaknesses(self, data=None, frac=0.1, functional=True):
        """
        (Private function)
        Finds and returns the FMs and outcomes that this particular MSA is ranked in top and bottom n in.
        params:
            msa (int): MSA to query and find strengths/weaknesses
            data (DataFrame): see metrics_outcomes.csv
            frac (float): Performance threshold across all MSAs within an FM to be considered as strength or weakness
            functional (bool): whether or not you want strengths/weaknesses based only on functional data
        :returns:
            tuple of two lists: best and worst.
            Each list is itself made up of two tuples, the metric of interest, and
            the rank of the msa within that metric
        """
        # use default dict if none provided
        if data is None:
            data = self.data.copy()

        # get number of MSAs to consider
        # top 10% of MSAs
        n = int(frac * data[data['YEAR'] == max(self.years)].shape[0])
        if n == 0:
            n = 1
        msa, year = self.msa, self.years[-1]
        best, worst = [], []

        # fm column names
        fm_outcomes = [i for i in data.columns.values if
                       self.STRENGTH_METRIC in i]  # this is the FM metric we will use to compare
        # outcome column names
        # we don't want other FM metrics
        non_fm_outcomes = [j for j in data.columns.values if '-' not in j]
        # if functional, use only fm columns
        if functional:
            cols_of_interest = fm_outcomes + ['MSA', 'MSA_NAME', 'YEAR']
        # else use both fm and outocme columns
        else:
            cols_of_interest = fm_outcomes + non_fm_outcomes

        datamod = data.loc[data.YEAR == year]
        metrics_of_interest = [metric for metric in cols_of_interest if metric not in [
            'MSA', 'MSA_NAME', 'YEAR']]

        # See if each FM and/or outcome is strength or weakness for MSA
        for metric in metrics_of_interest:
            temp = datamod.sort_values(by=[metric, 'MSA'], ascending=False)

            if msa in set(temp.head(n).MSA.values):

                rank = temp.head(n).MSA.values.tolist().index(msa) + 1
                if temp[metric].iloc[rank - 1] == 0:  # offset 0 index
                    continue  # all values are 0

                best.append((metric.split("-")[0], rank))
            if msa in set(temp.tail(n).MSA.values) and metric.split("-")[0] not in self._fms_to_negate:
                rank = temp.MSA.values.tolist().index(msa) + 1
                worst.append((metric.split("-")[0], rank))

        # Sort strengths and weaknesses
        best = sorted(best, key=lambda x: int(x[1]))
        worst = sorted(worst, key=lambda x: int(x[1]), reverse=True)

        return best, worst

    def _find_strengths_weaknesses_within_msa(self, data):
        """
        helper function for compute_distance. Finds an MSA's strengths
        :params:
            data (DataFrame): dataframe containing FM information
        returns:
            Tuple of lists: ([best FMs],[worst FMs])
        """
        # Select data for given MSA and YEAR
        msa_df = data[data['MSA'] == self.msa]
        msa_df = msa_df[msa_df['YEAR'] == self.years[-1]]
        # Select columns with appropriate metric
        fms = [i for i in data.columns.values if self.TOP_INDUSTRIES_METRIC in i]
        msa_df = msa_df[fms].T
        msa_df.columns = ['pc_estab']
        msa_df = msa_df.rename_axis('FM')
        # Sort FM by presence
        msa_df = msa_df.sort_values(
            by=['pc_estab', 'FM'], ascending=False).index.values

        # Build strengths
        strengths = []
        for index in range(len(msa_df)):
            strengths.append((msa_df[index].split("-")[0], index + 1))
            if len(strengths) == 10:
                break

        # Build weaknesses
        weaknesses = []
        for i in range(len(msa_df)):
            index = len(msa_df) - 1 - i
            fm = msa_df[index].split('-')[0]
            if fm in self._fms_to_negate:
                continue
            weaknesses.append((fm, index + 1))
            if len(weaknesses) == 10:
                break
        return strengths, weaknesses

    def find_peer_strengths_weaknesses(self, peers, frac=0.5, functional=True):
        """
        Finds the strengths and weaknesses of self.msa versus *only the peer group*

        params:
            peers (list): peers of interest
            frac (float): percentage of peers you want to compare against
            function (bool): whether or not you want strengths/weaknesses based only on functional data
        returns:
            Tuple containing list of strengths and list of weaknesses.
        """
        data = self.data.copy()

        data = data.loc[data['MSA'].isin(peers + [self.msa])]
        # Find strengths and weaknesses for peer group
        return self._find_strengths_weaknesses(data, frac, functional)

    def _get_distance_function(self, method):
        """
        Get the string version of a function call, specific to the scipy.distance api.
        Internal use for the class
        params:
            method - {string} the name of the distance metric
        returns:
            function call {string}
        """
        if method in PeerExplorer.DISTANCE:
            return f'distance.{method}'
        raise ValueError('Invalid distance metric.')

    def _standardize(self, data):
        """
        standardize all the numerical columns in the dataframe
        params:
            data - {dataframe} dataframe that contains FM and outcome data
        returns:
            new - {dataframe} standardized dataframe
        """
        new = data.copy()

        # all numerical columns
        cols = np.array(data.columns)
        cols = [c for c in cols if data[c].dtypes
                != 'O' and c not in ['YEAR', 'MSA']]

        # standardization
        new[cols] = (new[cols] - new[cols].mean()) / new[cols].std()

        return new

    def _find_fms_to_negate(self, data, threshold=0.6):
        """
        helper function for compute_distance. Provides a threshold to determine if a given set of FMs are 'similar
        enough' using the threshold variable, as we do not want to consider FMs where a majority of MSAs have 0
        presence.
        :params:
            data (DataFrame): dataframe to select FMs from
            threshold (float): specifies the allowed level of similarity. E.g. if 0.6 then
            FMs that have 'PRES_ESTAB' < 0.6 are chosen to be negated
        returns:
            list of FMs
        """
        # columns for binary presence metric
        fms = [i for i in data.columns.values if self.BINARY_PRESENCE_METRIC in i]
        # compute mean presence
        avg_pres = data[fms].mean().to_dict()
        # remove fms with presence across all MSAs less than threshold
        fms_to_negate = list(
            {k: v for (k, v) in avg_pres.items() if v < threshold})
        for index in range(len(fms_to_negate)):
            fms_to_negate[index] = fms_to_negate[index].split("-")[0]
        # return list of fm names
        return fms_to_negate

    def compute_top_industries(self, data, n_fms, compare_growth_year=None, metric=TOP_INDUSTRIES_METRIC):
        """
        Function to compute the top FMs for each MSA, the distances between the top FMs list for the current MSA and
            the top FMs list for every other MSA.
        Arguments:
            data {DataFrame} - DataFrame containing FM presence metric data for each MSA.
            n_fms {int} - Number of top FMs to consider.
            compare_growth_year {int} - Year from which to compare industry growth, if None only compare current year
                (default = None).
            metric {str} - FM Presence metric to use to compute top industries in each MSA.
        Returns:
            Saves to class a dictionary containing mapping of MSA codes to top industries distances, and mapping of MSA
            codes to list of top industries.
        """
        # Check valid metric
        if metric not in PeerExplorer.METRIC_NAMES:
            raise ValueError("Invalid Metric")

        # Get list of MSAs
        msas = data[data['YEAR'] == self.years[-1]][['MSA']]
        index = np.where(msas['MSA'] == self.msa)[0][0]

        # Compute top FMs for each MSA
        top_industries = self._compute_top_industries_list(
            data, n_fms, compare_growth_year, metric)
        # Get list of top FMs for current MSA
        top_industries_curr = top_industries[index]

        # Build dictionary of peer MSA to Top FMs Distance
        top_industries_peers = {}
        # Repeat for each peer MSA
        for i, peer in enumerate(top_industries):
            # Skip current MSA
            if i == index:
                continue
            # Compute distance between Top FMs
            top_industries_peers[msas.iloc[i]['MSA']] = self._compute_top_industries_distances(
                top_industries_curr, peer)

        # Compile MSA Names to results
        self._top_industries_dict = {'distance': top_industries_peers,
                                     'industries': {m: ind for m, ind in zip(msas['MSA'].values, top_industries)}}
        return

    def _get_top(self, attribute, ascending=True):
        """
        Get up to the top 10 strengths and weaknesses by rank
        params:
            attribute - feature to extract MSA with most and least presence
        returns:
            Ordered list of MSAs
        """
        # Sort data by FM presence
        temp = pd.DataFrame(attribute).sort_values(1, ascending=ascending)
        threshold = list(temp.head(self.N_TOP_MSA)[1])[-1]
        # Get lowest values
        if ascending:
            return list(temp[temp[1] <= threshold][0])
        # Get highest values
        else:
            return list(temp[temp[1] >= threshold][0])

    def _compute_general_distances(self, data):
        """
        Creates a dictionary of distances for creating general peers using strengths and weaknesses
        params:
            data - DataFrame containing FM values
        returns:
            dictionary of distances to other MSAs
        """
        _strengths_weaknesses = []

        # if no national strength/weakness, go to state level.
        # STILL NEED TO IMPLEMENT IF NO STATE STRENGTH/WEAKNESS (but haven't seen any cases yet)
        strength = self._strengths if self._strengths else \
            self._state_strengths if self._state_strengths else self._msa_strengths
        weakness = self._weaknesses if self._weaknesses else \
            self._state_weaknesses if self._state_weaknesses else self._msa_weaknesses

        _strengths_weaknesses = self._get_top(
            strength) + self._get_top(weakness, ascending=False)

        _strengths_weaknesses = list(_strengths_weaknesses)
        _strengths_weaknesses = [f'{c}-LQ_EMPL_ESTAB' for c in _strengths_weaknesses] + \
                                [f'{c}-PC_ESTAB' for c in _strengths_weaknesses] + _strengths_weaknesses
        # used to be LQ_EMPL_ESTAB_RANK
        if not _strengths_weaknesses:
            return {}
        _general_dict = self._compute_distance(data, _strengths_weaknesses,
                                               (self.years[-1], self.years[-1]))
        return _general_dict

    def find_general_peers(self, n_peers):
        """
        Determines the top n general peers based on population, strengths, and weaknesses
        :params:
            n_peers (int): number of peers to return
        returns:
            MSA codes for general peers
        """
        if self._general_dict:
            # find peers that are most similar
            return [m for m in sorted(self._general_dict.keys(), key=lambda x: sum(self._general_dict[x].values()))][
                   :n_peers]

    def _compute_distance(self, data, cols, year_lag):
        """
        calculate the distance between two msas
        :params:
            data (DataFrame): see metrics_outcomes.csv
            cols (list): columns of interest in the DataFrame
            year_lag (list): year of interest for each msa
        :returns:
            distance between two msas
        """
        # select columns
        cols = [c for c in cols if c in data.columns]
        newdata = data[['YEAR', 'MSA'] + cols].drop_duplicates()

        msa_list = set(newdata['MSA'].tolist())
        _distance_dict = {}

        # for each MSA
        for m in msa_list:
            if m == self.msa:
                continue
            # select data for both MSAs
            f1 = newdata[(newdata['MSA'] == m) & (
                newdata['YEAR'] == year_lag[0])][cols]
            f2 = newdata[(newdata['MSA'] == self.msa) & (
                newdata['YEAR'] == year_lag[1])][cols]
            # Remove columns with NaN
            delete_col = []
            delete_col += f1.columns[f1.isna().any()].tolist()
            delete_col += f2.columns[f2.isna().any()].tolist()
            delete_col = set(delete_col)
            cols = [c for c in cols if c not in delete_col]

            # get desired columns
            f1 = list(newdata[(newdata['MSA'] == m) & (
                newdata['YEAR'] == year_lag[0])][cols].values[0])
            f2 = list(newdata[(newdata['MSA'] == self.msa) & (
                newdata['YEAR'] == year_lag[1])][cols].values[0])

            if len(f1) == 0 or len(f2) == 0:
                continue
            # Distance between two MSAs for each column
            _distance_dict[m] = {k: v for k, v in
                                 zip(cols, [eval(self.dist_func)(f1[i], f2[i]) for i in range(len(f1))])}
        return _distance_dict

    def _compute_ts_distance(self, data, cols, year_lag):
        """
        use dynamic time warping to calculate the distance/similarity between different time series. compares the
        multi-dimensional time series of different FMs, outcomes. when specified with year_lag, can compare time series
        with time gap (for finding ancestral peers) This function is for internal class use only
        :params:
            data : {dataframe} FM metrics and outcomes data
            cols : {list[string]} the selected columns of the dataframe, could be either
                    FM names or outcome names
            year_lag : {list[int]} specify the year for the ancestral peers as well as
                    the current year for the target MSA. i.e. year_lag=[2013, 2016]
                    means that you compare distance for the time series for all MSAs
                    before 2013, and the time series for your target MSA before 2016
        returns:
            _distance_dict - {dictionary} a dictionary that contains the distances for
                    all MSAs
        """
        # by default, when year_lag is not specified, you want to
        # compare time series with consistent years
        self.years = sorted(self.years)
        # index for the last year of ancestral peers
        # index for the last year of the garget MSA
        idx_an, idx_rn = len(self.years) - 1, len(self.years) - 1

        # if year_lag is specified
        if year_lag:
            idx_an, idx_rn = self.years.index(
                year_lag[0]), self.years.index(year_lag[1])

        # new dataframe that contains specific years according to year_lag
        # dataframe for ancestral peers
        dts_an = data.loc[data['YEAR'].isin(
            self.years[:idx_an + 1])][['MSA', 'YEAR'] + cols]
        # dataframe for the current MSA
        dts_rn = data.loc[data['YEAR'].isin(
            self.years[:idx_rn + 1])][['MSA', 'YEAR'] + cols]

        tg_rn, tg_an = dts_rn.groupby('MSA'), dts_an.groupby('MSA')

        # helper function to group the dataframes by MSA and sort the rows
        # of each MSA by year, and then return a numpy matrix
        def _get_ts_values(tg, msa):
            return tg.get_group(msa) \
                .sort_values('YEAR')[cols] \

            # a matrix for target MSA that contains multi-dimensional

        # time series data
        ts_target = _get_ts_values(tg_rn, self.msa)

        msas = dts_an['MSA'].unique()  # search for all unique MSAs
        _distance_dict = {}
        for msa in msas:
            if msa == self.msa:
                continue
            # matrix for the MSA you want to compare with the
            # target MSA
            ts_msa = _get_ts_values(tg_an, msa)

            delete_col = []
            delete_col += ts_target.columns[ts_target.isna().any()].tolist()
            delete_col += ts_msa.columns[ts_msa.isna().any()].tolist()
            delete_col = set(delete_col)
            cols = [c for c in cols if c not in delete_col]

            ts_target = _get_ts_values(tg_rn, self.msa).values
            ts_msa = _get_ts_values(tg_an, msa).values

            if not len(ts_msa):
                continue
            # DTW computation for multi-dimensional time series
            # use euclidean distance. result is distance, the
            # larger the distance, the less similar of the two
            # time series
            distance, _ = fastdtw(ts_target, ts_msa, dist=euclidean)
            _distance_dict[msa] = distance

        return _distance_dict

    def _compute_geo_distance_df(self, data, omb, county_distances):
        """
        Computes the distances between MSAs from county level distance data

        :params:
            data (df): dataframe of outcomes and FMs across years
            omb (df): dataframe of FIPS and MSA codes and names
            county_distances (df): dataframe of pairwise county distances

        returns:
            distances (df): dataframe of average distances between pairs of MSAs
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
        _distances = new_distances.groupby(['msa1', 'msa2']).mean()
        _distances = _distances.sort_values("mi_to_county")
        _distances.reset_index(inplace=True)
        return _distances

    def _compute_state_peers(self, data, omb):
        """
        Groups MSAs by state through the first two digits of FIPS codes

        :params:
            data (df): dataframe of outcomes and FMs across years
            omb (df): dataframe of FIPS and MSA names and codes

        returns:
            states_codes_copy (df): dataframe of all MSAs with their first two FIPS codes digits (state)
        """
        # group MSAs by state
        msas = sorted(list(set(data['MSA'])))
        states_codes = omb[omb['CBSA_CODE'].isin(msas)]
        states_codes_copy = states_codes.copy()
        states_codes_copy['FIPS'] = states_codes_copy['FIPS'].astype(
            str).str[0:2]
        states_codes_copy = states_codes_copy[[
            'CBSA_CODE', 'FIPS']].drop_duplicates()
        state = list(
            states_codes_copy[states_codes_copy['CBSA_CODE'] == self.msa]['FIPS'])
        return list(set(states_codes_copy[states_codes_copy['FIPS'].isin(state)]['CBSA_CODE']))

    def _compute_top_industries_list(self, data, n_fms, compare_growth_year=None, metric=TOP_INDUSTRIES_METRIC):
        """
        Function to compute the top industries for each MSA, by ranking FM presence metric.
        :params:
            data {DataFrame} : DataFrame containing FM presence metric data for each MSA.
            n_fms: {int} : Number of top FMs to consider.
            compare_growth_year {int} : Year from which to compare industry growth, if None only compare current year
                (default = None).
            metric {str} : FM Presence metric to use to compute top industries in each MSA.
        returns:
            List of top FMs from most present to least present for each row in input DataFrame.
        """
        # Get columns for FM presence metric
        metric_columns = [col for col in data.columns if len(col.split("-")) > 1
                          and col.split("-")[1] == metric]
        # Get FM name from columns
        metric_names = [m.split('-')[0] for m in metric_columns]

        # Select columns for metric
        data = data[['MSA', 'YEAR'] + metric_columns]

        # If previous year input, compute change in industry presence
        if compare_growth_year:
            # Check valid input compare_growth_year
            if compare_growth_year >= self.years[-1]:
                raise ValueError('Invalid historical year to compute top industry growth: {}.'.format(
                    compare_growth_year))
            if compare_growth_year not in data['YEAR'].unique():
                raise ValueError(
                    'Historical data for year not found: {}.'.format(compare_growth_year))
            # Compute percent change from previous year to current year
            curr = data[data['YEAR'] == self.years[-1]].set_index('MSA')
            prev = data[data['YEAR'] == compare_growth_year].set_index('MSA')
            data = curr[metric_columns].subtract(
                prev[metric_columns]).divide(prev[metric_columns])
        # Else use industry presence values
        else:
            # Filter on year
            data = data[data['YEAR'] == self.years[-1]]

        # Sort each row
        fm_presence = data[metric_columns].values.argsort(axis=1)
        # Get list of top n FMs
        top_indices = fm_presence[:, ::-1][:, :n_fms]
        # Convert to FM names
        top_industries = [np.array(metric_names)[row] for row in top_indices]

        return top_industries

    def _compute_top_industries_distances(self, curr, peer):
        """
        Function to compute the distances between top FMs for each MSA. Computed by summing the positional differences
            between FMs in top FMs lists.
        :params:
            curr {List}: List of top FMs for current MSA.
            peer {List}: List of top FMs for peer MSA to compute distance.
        returns:
            Distance between two lists of top FMs.
        """
        curr, peer = np.array(curr), np.array(peer)
        # Track total distance
        dist = 0
        n = len(curr)
        # Iterate through all top FMs for current MSA
        for i, ind in enumerate(curr):
            # If FM not found in peer MSA's top FMs list, add distance proportionate to position in current MSA's list
            if ind not in peer:
                dist += n - i
            # If FM is found in peer MSA's top FMs list, add distance of difference in ranking
            else:
                dist += abs(i - np.where(peer == ind)[0][0])

        return dist

    def find_industry_peers(self, n_peers):
        """
        find peers based on distance between msas in terms of fm distribution
        :params:
            n_peers: number of peers wanted
        :returns:
            desired number of msa peers
        """
        if self._industry_distance_dict:
            return [m for m in sorted(self._industry_distance_dict.keys(),
                                      key=lambda x: sum(self._industry_distance_dict[x].values()))][:n_peers]
        return []

    def find_outcome_peers(self, n_peers):
        """
        find peers based on distance between msas in terms of outcome
        :params:
            n_peers: number of peers wanted
        :returns:
            desired number of msa peers
        """
        if self._outcome_distance_dict:
            return [m for m in sorted(self._outcome_distance_dict.keys(),
                                      key=lambda x: sum(self._outcome_distance_dict[x].values()))][:n_peers]
        return []

    def find_industry_ancestral_peers(self, n_peers):
        """
        find ancestral peers based on distance between msas in terms of fm distribution
        :params:
            n_peers: number of peers wanted
        :returns:
            desired number of msa peers
        """
        if self._ancestral_industry_dict:
            return [m for m in sorted(self._ancestral_industry_dict.keys(),
                                      key=lambda x: sum(self._ancestral_industry_dict[x].values()))][:n_peers]
        return []

    def find_outcome_ancestral_peers(self, n_peers):
        """
        find peers based on distance between msas in terms of outcome
        :params:
            n_peers: number of peers wanted
        :returns:
            desired number of msa peers
        """
        if self._ancestral_outcome_dict:
            return [m for m in sorted(self._ancestral_outcome_dict.keys(),
                                      key=lambda x: sum(self._ancestral_outcome_dict[x].values()))][:n_peers]
        return []

    def find_geographic_peers(self, n_peers):
        """
        find peers based on physical distance
        :params:
            n_peers: number of peers wanted
        :returns:
            desired number of msa peers
        """
        if not self._geo_distance_df.empty:
            return list(self._geo_distance_df[self._geo_distance_df['msa1'] == self.msa].head(n_peers)['msa2'])

    def find_top_industries_peers(self, n_peers):
        """
        find peers based on previously specified FMs in the __init__ part of the function
        :params:
            n_peers: number of peers wanted
        :returns:
            desired number of msa peers
        """
        if self._top_industries_dict:
            return [m[0] for m in sorted(self._top_industries_dict['distance'].items(),
                                         key=operator.itemgetter(1))[:n_peers]]
        return []

    def find_what_makes_peers(self, peer, peer_type='general'):
        """
        find what metrics make the msa peer of the target msa by choosing top 5 metrics with shortest distance and then
        checking whether the distance is below the average metric distance of all msa pairs or not.
        :params:
            peers: peer found using different algorithms
            peer_type: types of the peer (general, industry, outcome, industry_ancestral and outcome_ancestral)
        :returns:
            metric that make the msa peer of the target msa
        """
        _res = []
        # use appropriate dictionary depending on peer type
        if peer_type == 'general':
            dic = self._general_dict
        elif peer_type == 'industry':
            dic = self._industry_distance_dict
        elif peer_type == 'outcome':
            dic = self._outcome_distance_dict
        elif peer_type == 'industry_ancestral':
            dic = self._ancestral_industry_dict
        else:
            dic = self._ancestral_outcome_dict
        _sum_distance = collections.defaultdict(int)
        _count_distance = collections.defaultdict(int)

        # Find FMs with least distance
        for m in dic:
            for col in dic[m]:
                _sum_distance[col] += dic[m][col]
                _count_distance[col] += 1
        for col in _sum_distance:
            self._average_distance[col] = _sum_distance[col] / \
                _count_distance[col]
        for key in sorted(dic[peer].items(), key=operator.itemgetter(1))[:10]:
            if dic[peer][key[0]] < self._average_distance[key[0]]:
                _res.append(key)
        return _res

    def find_most_similar_fm(self, peer, n=5, data=None):
        """
        Used for find_geographical_peers. Yields n most similar fms of given peer.
        :params:
            peer (int): peer MSA
            n (int): number of FMs to yield
        returns:
            set of most similar fms to given peer
        """
        if data is None:
            data = self.data.copy()
        cols = [i for i in data.columns.values if self.TOP_INDUSTRIES_METRIC in i]
        dic = self._compute_distance(
            data, cols, [self.years[0], self.years[0]])
        # Find FMs that contribute least to distance
        return list(set([k[0].split('-')[0] for k in sorted(dic[peer].items(), key=operator.itemgetter(1))[:n]]))

    def find_peers_specialty(self, peers, metric='PC_ESTAB', n=5):
        """
        Selects FMs where the peer group is most different to the national average, and returns the data in the form of
        a DataFrame.
        :params:
            peers (list): the peer FMs to compare to national average
            metric (str): presence metric to use
            n (int): number of FM metrics to return
        returns: dataframe of peer vs national averages across the most different FMs
        """
        fms = [i for i in self.raw_data.columns.values if metric in i]
        desired_cols = ['MSA', 'MSA_NAME', 'YEAR'] + fms
        proc_df = self.raw_data.loc[self.raw_data.YEAR
                                    == self.years[-1]][desired_cols]
        peer_df = proc_df.loc[proc_df.MSA.isin(peers + [self.msa])]
        # Compute peer and national means
        peer_mean, national_mean = peer_df[fms].mean(), proc_df[fms].mean()
        # Find absolute differences
        diff = abs(peer_mean - national_mean)
        # Return largest differences
        most_diff_fms = list(diff.nlargest(n).index)
        ret = pd.DataFrame(
            {"Peer": peer_mean[most_diff_fms], "National": national_mean[most_diff_fms]}).T
        return ret

    def explain_peers(self, peers=None, peer_type='general', n_peers=5):
        """
        Takes in the type of peer and number of peers and returns dataframe of FMs (of your msa, peer, and national
        average) explaining the peer grouping
        """
        # Grab appropriate peer group
        if peers is None:
            if peer_type == 'general':
                peers = self.find_general_peers(n_peers)
            elif peer_type == 'industry':
                peers = self.find_industry_peers(n_peers)
            elif peer_type == 'geographic':
                peers = self.find_geographic_peers(n_peers)
            elif peer_type == 'outcome':
                peers = self.find_outcome_peers(n_peers)
            else:
                raise ValueError('Please enter a valid peer type')

        # Find most defining FMs for MSA and each peer in peer group
        peer_fm_dict = collections.defaultdict(set)
        if peer_type == 'geographic':
            for peer in peers:
                geo_peers = list(self.find_most_similar_fm(peer))
                for fm in geo_peers:
                    peer_fm_dict[peer].add(fm)
        else:
            for peer in peers:
                for fm_tup in self.find_what_makes_peers(peer, peer_type):
                    peer_fm_dict[peer].add(fm_tup[0])

        ret = self._build_peer_similarity_dict(peer_fm_dict)
        return ret

    def _build_peer_similarity_dict(self, peer_dict):
        """
        Helper function for explain_peers.
        Takes in Peer
        """
        ret_dict = {}  # peer: df
        df = self.raw_data.loc[self.raw_data.YEAR == self.years[-1]]
        # For each peer, compute differences in mean of FM presence
        for peer_msa in peer_dict.keys():
            shared_cols = list(i for i in peer_dict[peer_msa])
            own_FM = df.loc[df.MSA == self.msa][shared_cols].values[0]
            other_FM = df.loc[df.MSA == peer_msa][shared_cols].values[0]
            mean_FM = df[shared_cols].mean(axis=0).values
            peer_df = pd.DataFrame(
                {self.msa: own_FM, peer_msa: other_FM, 'Mean': mean_FM}, index=shared_cols)
            ret_dict[peer_msa] = peer_df.to_dict()
        return ret_dict

    @property
    def industry_distance_dict(self):
        return self._industry_distance_dict

    @property
    def outcome_distance_dict(self):
        return self._outcome_distance_dict

    @property
    def ancestral_industry_dict(self):
        return self._ancestral_industry_dict

    @property
    def ancestral_outcome_dict(self):
        return self._ancestral_outcome_dict

    @property
    def geo_distance_df(self):
        return self._geo_distance_df

    @property
    def state_peers(self):
        return self._state_peers

    @property
    def general_dict(self):
        return self._general_dict

    @property
    def strengths(self):
        return self._strengths

    @property
    def weaknesses(self):
        return self._weaknesses

    @property
    def state_strengths(self):
        return self._state_strengths

    @property
    def state_weaknesses(self):
        return self._state_weaknesses

    @property
    def msa_strengths(self):
        return self._msa_strengths

    @property
    def msa_weaknesses(self):
        return self._msa_weaknesses

    @property
    def top_industries_dict(self):
        return self._top_industries_dict

    @property
    def average_distance_dict(self):
        return self._average_distance
