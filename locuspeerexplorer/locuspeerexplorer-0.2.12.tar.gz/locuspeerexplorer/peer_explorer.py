import numpy as np
import pandas as pd
import locuspeerexplorer.params
from scipy import stats


def get_distinguishing_outcomes(
    df_data, area, peers, year, comparison, metric, threshold=99
):

    """
    Function to derive outcomes at the national/peer level that are different from
    the outcomes at the peer/area level

    :type area: int
    :param peers: Peers of the reference area
    :type peers: list
    :param year: Year to be used for comparison
    :type year: int
    :param comparison: Int to indicate whether to use just the area or
                       area + peers for comparison to the national data
                       Key - 0: National/Peers, 1: National/area, 2: Peers/area
    :type comparison: int
    :param significance: Significance level used for t-tests
    :type significance: float
    :return: Dictionary of outcomes that are signficantly different from the
             peer group/area outcomes
    :rtype: dict
    """

    # Get outcomes to be compared
    outcomes = [c for c in df_data.columns if metric in c]

    # Get area data
    df_area = df_data.loc[(df_data["AREA"] == area) & (df_data["YEAR"] == year)]
    df_peers = df_data.loc[df_data["AREA"].isin(peers) & (df_data["YEAR"] == year)]
    df_national = df_data.loc[
        ~df_data["AREA"].isin([peers, area]) & (df_data["YEAR"] == year)
    ]

    distinguishing_outcomes = dict()

    # Loop percentile comparisons through all outcomes
    for outcome in outcomes:

        # Get national outcome data
        outcome_national = df_national[outcome].tolist()

        # Percentile comparison for peer groups/areas
        if comparison == 0:
            outcome_peers = df_peers[outcome].tolist()
            percentile = stats.percentileofscore(
                outcome_national, np.mean(outcome_peers)
            )
        elif comparison == 1:
            outcome_area = df_area[outcome].tolist()
            percentile = stats.percentileofscore(outcome_national, outcome_area)
        else:
            outcome_peers = df_peers[outcome].tolist()
            outcome_area = df_area[outcome].tolist()
            percentile = stats.percentileofscore(outcome_peers, outcome_area)

        # Keep outcomes that are higher than the specified threshold
        if percentile > threshold:
            distinguishing_outcomes[outcome] = percentile

    return distinguishing_outcomes
