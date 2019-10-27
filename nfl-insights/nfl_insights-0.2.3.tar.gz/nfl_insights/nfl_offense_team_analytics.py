import pandas as pd
import numpy as np
import os
import logging

from nfl_insights import NFLStatsQueries
from contendo_utils import *


# noinspection PyUnresolvedReferences
class OffenseTeamData:

    @contendo_classfunction_logger
    def __init__(self, seasons):
        assert type(seasons)==list, 'seasons parameter must be a list, "{}" is illegal'.format(seasons)
        self.generator = NFLStatsQueries('sportsight-tests')
        _df = self.generator.statsDF
        self.statList = list(_df[_df.StatGroup=='Offense']['StatName'])
        # get team names and IDs
        self.teams = self.generator.nfldata.get_teams_df(season=seasons[0])

        #build a table for each stats with all dimensions
        self.metrics = dict()
        self._build_all_metrics(seasons)

    def _add_result_df_to_team_metrics(self, statName, df, dim):
        result = self.metrics[statName]
        if df.shape[0] != 0:
            #df.set_index('teamId', inplace=True)
            result[statName + "_" + dim] = df["statValue"]
            result[statName + "_" + dim + "_pct"] = result[statName + "_" + dim] / (result[statName + "_all_all"] + 1e-6)
        else:
            result[statName + "_" + dim] = np.zeros(32)
            result[statName + "_" + dim + "_pct"] = np.zeros(32)

    @contendo_classfunction_logger
    def _build_all_metrics(self, seasons):

        _dimensionsMatrixDict = self.generator.dimentionsMatrixDict
        _dimensionsDF = self.generator.dimentionsDF
        _dimensionGroups = _dimensionsDF.groupby(['GroupCode'])
        _dimGroupList = _dimensionsMatrixDict.keys()
        _statsDict = self.generator.statsDict

        _dimensionGroupsDict = dict()
        for dimGroup in _dimGroupList:
            _dimDF = _dimensionGroups.get_group(dimGroup)
            _dimensionGroupsDict[dimGroup] = list(_dimDF['ConditionCode'])

        #logger.debug('Dimensions groups: %s', _dimensionGroupsDict)
        counter = 0
        lineCounter=0
        for statName in self.statList:
            if _statsDict[statName]['Doit'] !='y':
                continue
            self.metrics[statName] = self.teams.copy()
            for dimGroup1 in _dimGroupList:
                logger.info('%4d. calculating stat: %s, dim-group1: %s, data: %s', counter, statName, dimGroup1, lineCounter)
                for dimGroup2 in _dimGroupList:
                    if _dimensionsMatrixDict[dimGroup2][dimGroup1]==1:
                        for dim1 in _dimensionGroupsDict[dimGroup1]:
                            for dim2 in _dimensionGroupsDict[dimGroup2]:
                                counter+=1
                                _dimComb2 = [dim1, dim2]
                                #print('{}\t{}\t{}'.format( counter,dim1, dim2))
                                df = self.generator.pbp_get_stat(
                                    statName=statName,
                                    object='offenseTeam',
                                    dimensions=_dimComb2,
                                    seasons=seasons,
                                )
                                lineCounter+=df.shape[0]
                                self._add_result_df_to_team_metrics(statName, df, dim='{}_{}'.format(dim1, dim2))
            self.metrics[statName].fillna(0)
        logger.debug('Num queries: %d, Num results: %d', counter, lineCounter)
        return lineCounter

@contendo_function_logger
def test():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "{}/sportsight-tests.json".format(os.environ["HOME"])
    os.chdir('{}/tmp/'.format(os.environ["HOME"]))
    pd.set_option('display.max_columns', 1500)
    pd.set_option('display.width', 20000)
    ostats = OffenseTeamData(seasons=['2019-regular'])
    for statName, metricsDF in ostats.metrics.items():
        metricsDF.to_csv('stats_{}.csv'.format(statName), index=False)

if __name__ == '__main__':
    contendo_logging_setup(default_level=logging.INFO)
    test()
