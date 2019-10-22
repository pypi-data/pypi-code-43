import collections
import numpy as np
import os
import pandas as pd
import operator
from scipy.spatial import distance
from scipy.spatial.distance import euclidean
import locuspeerexplorer.params

dirname, filename = os.path.split(os.path.abspath(__file__))


def get_geographic_peers(
    df_data, df_county_dist, df_msa_def, area, n_peers, year, geo_level="msa"
):
    """
    Find the n_peers based on the average distance
    between each county in the

    :param n_peers: number of peers to return
    :type n_peers: int
    :return: geographic peers
    :rtype: list
    """
    assert area in list(df_data["AREA"]), "Area code not present in the dataset"
    df_data = df_data.query("YEAR == @year")
    if geo_level == "msa":
        omb = df_msa_def[["FIPS", "CBSA_CODE"]]
        d = omb.set_index("FIPS").to_dict()
        d = d["CBSA_CODE"]
        county_distances = (df_county_dist)[(df_county_dist)["county1"].isin(list(d))]
        county_distances = county_distances[county_distances["county2"].isin(list(d))]
        new_distances = county_distances.replace({"county1": d})
        new_distances = new_distances.replace({"county2": d})
        msas = sorted(list(set(df_data["AREA"])))
        new_distances = new_distances[new_distances["county1"].isin(msas)]
        new_distances = new_distances[new_distances["county2"].isin(msas)]
        new_distances.columns = ["msa1", "mi_to_county", "msa2"]
        # we now have a df that replaced counties with msas
        # now we get rid of msa1 and msa2 that are the same
        new_distances = new_distances.query("msa1 != msa2")
        # now we average the distances from county level for msa level distances
        geo_distances = new_distances.groupby(["msa1", "msa2"]).mean()
        geo_distances = geo_distances.sort_values("mi_to_county")
        geo_distances.reset_index(inplace=True)
        geo_to_msa = geo_distances[geo_distances["msa1"] == area]
        peers = (list(geo_to_msa["msa2"]))[:n_peers]
    elif geo_level == "county":
        df_county = df_county[df_county["county1"] == area]
        df_county.sort_values("mi_to_county", inplace=True)
        peers = (list(df_county["county2"]))[:n_peers]
    return peers, []


def get_peers_from_input(df_data, area, year, n_peers, fms=[], outcomes=[]):
    """
    Find the n_peers based on the similarity in all specified FMS
        and outcomes among all s

        :param fms: FMs used to identify peers
        :type fms: list
        :param outcomes: Outcomes used to identify peers
        :type outcomes: list
        :param n_peers: Number of peers to return
        :type n_peers: int
        :return: User specified peers
        :rtype: list
    """
    assert area in list(df_data["AREA"]), "Area code not present in the dataset"
    df_data = df_data.query("YEAR == @year")
    cols = [x + "-PC_EMPL" for x in fms] + outcomes
    try:
        peers = _peers_euclidean_distance(df_data, cols, area, n_peers)
    except KeyError:
        print("Some inputs are not present in the dataset :")
        print([c for c in cols if c not in df_data.columns])
        cols = list(df_data.columns & cols)
        peers = _peers_euclidean_distance(df_data, cols, area, n_peers)
    return peers, cols


def get_top_n_fms_peers(df_data, area, year, n_peers, n_fms=10):
    """
    Get peers using the top n_fms FMs ranked by the presence of the FMs in
    the area

    :param n_fms: Number of FMs to use
    :type n_fms: int
    :param n_peers: Number of peers to return
    :type n_peers: int
    :return: Peers based on most present FMs in the area
    :rtype: list
    """
    assert area in list(df_data["AREA"]), "Area code not present in the dataset"
    df_data = df_data.query("YEAR == @year")
    pc_fms = [c for c in df_data.columns if "-PC_EMPL" in c]
    df_area = df_data[pc_fms][df_data["AREA"] == area].T.reset_index()
    df_area.columns = ["FMs", "PC_EMPL"]
    df_area.sort_values("PC_EMPL", inplace=True, ascending=False)
    ranked_fms = list(df_area["FMs"])[:n_fms]
    return _peers_euclidean_distance(df_data, ranked_fms, area, n_peers), ranked_fms


def get_distinguishing_features_peers(df_data, area, year, n_peers, n_feat=10):
    """
    Get peers using the FMs for which the area has a concentration of
    pc_estab significantly higher or significantly lower than average

    :param n_feat: Number of FMs to use
    :type n_feat: int
    :param n_peers: Number of peers to return
    :type n_peers: int
    :return: Peers based on the distinguishing features of the area
    :rtype: list
    """
    assert area in list(df_data["AREA"]), "Area code not present in the dataset"
    df_data = df_data.query("YEAR == @year")
    count_area = df_data.AREA.value_counts().sum()
    # Get FMs that are present in at least 50% of all areas
    # by summing PRES_ESTAB for all area, and taking fms for which
    # SUM_PRES >= count_area/2
    df_pres = df_data[[c for c in df_data.columns if "PRES_ESTAB" in c]].T
    df_sum_pres = df_pres.sum(axis=1).reset_index()
    df_sum_pres.columns = ["FMs", "SUM_PRES"]
    df_sum_pres = df_sum_pres.query("SUM_PRES >= @count_area/2")
    present_fms = list(df_sum_pres.FMs)
    cols = [c.split("-")[0] + "-LQ_EMPL_ESTAB_RANK" for c in present_fms]
    # Get 10 FMs for which area has a significantly higher or lower than
    # average number of estab
    df_area = df_data[cols][df_data["AREA"] == area].T.reset_index()
    df_area.columns = ["FMs", "RANK"]
    df_area["RANK"] = df_area.apply(lambda x: min(count_area - x.RANK, x.RANK), axis=1)
    df_area.sort_values("RANK", inplace=True)
    distinguishing_fms = [c.split("-")[0] + "-PC_EMPL" for c in list(df_area["FMs"])][
        :n_feat
    ]
    return (
        _peers_euclidean_distance(df_data, distinguishing_fms, area, n_peers),
        distinguishing_fms,
    )


def get_emp_threshold_peers(df_data, area, year, n_peers, coverage=5):
    """
    Helper function that sieves out FMs belonging to the user inputted area that cover
    50% or more of the total work.

    :param coverage: fraction of workforce coverage for the FMs,
                    coverage = 5 corresponds to 50%
    :type coverage: int
    :return: List of the minimum set of FMs that cover x% of the workforce
    :rtype: list
    """
    assert area in list(df_data["AREA"]), "Area code not present in the dataset"
    coverage = coverage / 10
    employment_str = "PC_EMPL"

    # Get employment columns
    employment_list = [c for c in df_data.columns if employment_str in c]

    # Filter out user area for specified year
    df_area_employment = df_data[(df_data["AREA"] == area) & (df_data["YEAR"] == year)][
        employment_list
    ]

    total_employment = df_area_employment.sum(axis=1).iloc[0]

    # Find minimum set of FMs required to cover x% of workforce
    df_area_employment = df_area_employment.sort_values(
        by=df_area_employment.index[0], axis=1, ascending=False
    ).T
    fms_included = df_area_employment.index[
        (df_area_employment.cumsum() <= total_employment * coverage).iloc[:, 0]
    ]

    return (
        _peers_euclidean_distance(df_data, fms_included.to_list(), area, n_peers),
        fms_included.to_list(),
    )


def get_stabilizing_peers(df_data, area, year, n_peers, method):
    method2call = {
        "top_fms": get_top_n_fms_peers,
        "distinguishing": get_distinguishing_features_peers,
        "coverage": get_emp_threshold_peers,
    }
    n = 1
    peers_curr, _ = method2call[method](df_data, area, year, n_peers, n)
    peers_next, cols = method2call[method](df_data, area, year, n_peers, n + 1)
    while len(set(peers_curr) & set(peers_next)) <= 0.90 * n_peers and n <= 100:
        n += 1
        peers_curr = peers_next
        peers_next, cols = method2call[method](df_data, area, year, n_peers, n + 1)
    return peers_curr, cols


def _peers_euclidean_distance(df_data, cols, area, n_peers):
    """
    Compute the euclidean distance to area for all rows (=all areas)
    on all columns in cols

    :param df: Data
    :type df: dataframe
    :param cols: Columns to use to compute the distance
    :type cols: list
    :param area: area to compute the distance to
    :type area: int
    :param n_peers: Number of peers to return
    :type n_peers: int
    :return: List of peers
    :rtype: list
    """

    df = (df_data.copy()).dropna(subset=cols, how="any")[(["AREA"] + cols)]
    df.set_index("AREA", inplace=True)

    def standardize(c):
        return (c - c.mean()) / c.std()

    df = df.apply(standardize, axis=0)
    df_area = df.loc[area]
    df = df.drop(area)

    # Euclidean distance
    df_dist = (((df - df_area).pow(2)).sum(axis=1)).pow(0.5)
    # df_dist = df.corrwith(df_area, axis=1)
    df_dist = df_dist.reset_index()
    df_dist.columns = ["AREA", "DIST"]
    df_dist.sort_values("DIST", inplace=True)
    peers = list(df_dist.head(n_peers)["AREA"])
    return peers
