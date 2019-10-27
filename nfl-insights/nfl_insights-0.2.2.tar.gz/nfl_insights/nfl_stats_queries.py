import os
import pandas as pd
from datetime import datetime as dt
from pathlib import Path
import logging

import gspread

from contendo_utils import *
from nfl_insights import *

# noinspection PyUnresolvedReferences
class NFLStatsQueries():
    #
    # read in the configurations
    def __init__(self, project=None):
        #
        # get the initial configurations
        self.ccm = ContendoConfigurationManager()
        self.sourcesConfigDict = self.ccm.get_configuration_dict(NFL_DOMAIN_NAME, NFL_DOMAIN_CONFIG_GID, 'Configname')
        self.statsDF = self.ccm.get_configuration_df(NFL_DOMAIN_NAME, 530297342)
        self.statsDict = ProUtils.pandas_df_to_dict(self.statsDF, 'StatName')
        self.compStatsDF = self.ccm.get_configuration_df(NFL_DOMAIN_NAME, 1414140695)
        self.compStatsDict = ProUtils.pandas_df_to_dict(self.compStatsDF, 'StatName')
        self.dimentionsDF = self.ccm.get_configuration_df(NFL_DOMAIN_NAME, 71679784)
        self.dimentionsDict = ProUtils.pandas_df_to_dict(self.dimentionsDF, 'ConditionCode')
        self.dimentionsMatrixDict = self.ccm.get_configuration_dict(NFL_DOMAIN_NAME, 779003421, 'GroupCode')
        self.ptmapDict = self.ccm.get_configuration_dict(NFL_DOMAIN_NAME, 582380093, 'Object')
        #
        # initialize data
        #self.bqu = BigqueryUtils(project)
        self.nfldata = NFLGetData(project)
        #
        # cache variables
        self.pbpDF = None
        self.cachedDFs = dict()
        self.cachedSeasonDFs = dict()

    def _get_pbp_data(self, seasons=None):
        if self.pbpDF is None:
            self.pbpDF = self.nfldata.get_pbp_data()
            self.pbpDF['all']=1
            self.pbpDF['count']=1
            self.pbpDF['counter']=1
            #self.pbpDF = self.pbpDF[(self.pbpDF.season=='2019-regular')]
            #self.pbpDF.set_index("playType", inplace=True)
            self.pbpDF.set_index("season", inplace=True, append=True)
            #self.pbpDF.set_index("playType", inplace=True)
            self.pbpDF['yardsRushed'] = pd.to_numeric(self.pbpDF['yardsRushed'])

        _seasons = str(seasons)
        if _seasons not in self.cachedSeasonDFs:
            if _seasons:
                self.cachedSeasonDFs[_seasons] = self.pbpDF.query('season.isin({})'.format(_seasons))
            else:
                self.cachedSeasonDFs[_seasons] = self.pbpDF

        return self.cachedSeasonDFs[_seasons]


    def _get_dimentions_condition(self, dimensions):
        retCond = 'True'
        for dim in dimensions:
            dimDef = self.dimentionsDict[dim]
            condition = dimDef['Condition']
            if condition and condition!='True':
                retCond += ' & ({})'.format(condition)

        return retCond

    def _get_stat_condition(self, statDef):
        condition = statDef['Condition']
        _function = statDef['Function']
        if condition:
            if condition=='True':
                pass
            elif _function == 'count':
                return '{}'.format(condition)
            else:
                return '({})'.format(condition, statDef['AggField'])

        return 'True'

    @contendo_classfunction_logger
    def _save_trace_df(self, traceDF, initialColumns, spreadId=None, sheetName=None):
        if not spreadId:
            spreadId = '1Q5O3ejSyEDZrlFXX04bOIWOqMxfiHJYimunZKtpFswU'
        if not sheetName:
            sheetName = 'trace'

        finalColumns=['season', 'gameid', 'gamename', 'homeScore', 'awayScore','quarter', 'playType', 'currentDown']

        for col in initialColumns:
            if col in traceDF.columns:
                finalColumns.append(col)

        for col in traceDF.columns:
            if col not in finalColumns:
                finalColumns.append(col)

        if 'CONTENDO_AT_HOME' in os.environ:
            from gspread_pandas import Spread, Client
            import google.auth
            credentials, project = google.auth.default()
            gc = gspread.Client(credentials)
            spread = Spread(spreadId, client=gc)
            spread.df_to_sheet(traceDF[finalColumns], index=False, sheet=sheetName, start='A1', replace=True)
            logger.info('trace can be found in this url: %s', spread.url)
        else:
            fileName = '{}.csv'.format(sheetName)
            traceDF[finalColumns].to_csv(fileName)
            logger.info ('Trace to file %s', fileName)
            try:
                import google.colab
                IN_COLAB = True
                from google.colab import files
                logger.debug ('Downloading %s', fileName)
                files.download(fileName)
            except Exception as e:
                logger.warning('Error getting trace file %s', fileName)
                IN_COLAB = False

    @contendo_classfunction_logger
    def pbp_get_stat(self, statName, object, dimensions=['all'], seasons=['2019-regular'], aggfunc=None, playType=None, filter='True', trace=False, playerId = None, teamId=None):
        assert statName in self.statsDict, "Illegal statName: '{}', must be one of {}".format(statName, self.statsDict.keys())
        assert object in self.ptmapDict, "Illegal object: '{}', must be one of {}".format(object, self.ptmapDict.keys())
        assert type(dimensions) == list, "Illrgal dimensions argument {}, must be a list".format(dimensions)
        for _dim in dimensions:
            assert _dim in self.dimentionsDict, "Illegal statName: '{}', must be one of {}".format(_dim, self.dimentionsDict.keys())
        dimensions.sort()

        #
        # build the query conditions
        statDef = self.statsDict[statName]
        queryInst = {
            'statcond': self._get_stat_condition(statDef),
            'dimensionsCond': self._get_dimentions_condition(dimensions),
            'filtercond': filter,
            'isInplayCond': "(df.playType=='penalty') | (df.isNoPlay!=True)"
        }
        aggField = statDef['AggField']
        #
        # get the DF for the relevant seasons
        df = self._get_pbp_data(seasons)

        logger.debug('before aggfield processing %s', aggField)
        #df[aggField] = pd.to_numeric(df[aggField])
        #queryeval = 'df[({statcond}) & ({gamecond}) & ({playcond}) & ({filtercond}) & ({isInplayCond})]'.format(**queryInst)
        queryeval = 'df[({statcond}) & ({dimensionsCond}) & ({filtercond}) & ({isInplayCond})]'.format(**queryInst)
        _query = '({statcond}) & ({dimensionsCond}) & ({filtercond}) & ({isInplayCond})'.format(**queryInst).replace('df.', '').replace('(True) &', '').replace('True &', '')
        if queryeval in self.cachedDFs:
            filteredDF = self.cachedDFs[queryeval]
            logger.debug('From cache: Filtered DF shape: %s, Main DF shape: %s', filteredDF.shape, df.shape)
        else:
            try:
                logger.debug('before filtering: %s, %s', queryeval, _query)
                filteredDF = df.query(_query) # eval(queryeval)
                self.cachedDFs[queryeval] = filteredDF
                logger.debug('Filtered DF shape: %s, Main DF shape: %s', filteredDF.shape, df.shape)
            except Exception as e:
                logger.exception("Error evaluating filtering statemet: %s", queryeval)
                raise e

        #
        # return empty if no answers
        if filteredDF.shape[0]==0:
            logger.debug ('ZERO results for filter %s, total plays %s', queryeval, df.shape[0])
            return pd.DataFrame()

        objectDef = self.ptmapDict[object]
        statObject = objectDef['StatObject']
        if statObject=='team':
            groupby = "['{object}_id', '{object}_name']"
        else:
            groupby = "['{object}_id', '{object}_firstName', '{object}_lastName', '{object}_position', '{team}_id', '{team}_name']"
        groupby = groupby.format(object=object, team=objectDef['TeamType'])

        groupingeval = "filteredDF.groupby({groupby}, as_index=False).agg({}'{aggField}': '{aggFunc}', 'count': 'count', 'gameid': pd.Series.nunique {}).sort_values(by='{aggField}', ascending=False)"

        if not aggfunc:
            aggfunc = statDef['Function']
        logger.debug('before grouping')
        groupingeval = groupingeval.format('{', '}',groupby=groupby, aggField=aggField, aggFunc=aggfunc)

        try:
            finalDF = eval(groupingeval)
        except Exception as e:
            logger.exception("Error evaluating aggregation statemet: %s", groupingeval)
            raise e

        if trace:
            self._save_trace_df(filteredDF, finalDF.columns, sheetName='trace-{}-{}-{}'.format(statName, object, dimensions))

        if statObject=='team':
            finalDF.columns=['teamId', 'teamName', 'statValue', 'count', 'nGames']
            #finalDF.set_index('teamId', inplace=True)
        else:
            finalDF.columns=['playerId', 'firstName', 'lastName', 'position', 'teamId', 'teamName', 'statValue', 'count', 'nGames']
            #finalDF.set_index('playerId', inplace=True)

        #
        # add the rank - denserank.
        finalDF['rank'] = finalDF['statValue'].rank(method='dense', ascending=False)
        cols = finalDF.columns.copy()
        if teamId:
            finalDF = finalDF[finalDF.teamId==teamId]
            if finalDF.shape[0] == 0:
                record=dict()
                for col in finalDF.columns:
                    record[col] = None
                record['teamId'] = teamId
                record['statValue'] = 0
                record['count'] = 0
                record['rank'] = -1
                finalDF = pd.DataFrame([record])
        if playerId:
            finalDF = finalDF[finalDF.playerId==playerId]
            if finalDF.shape[0] == 0:
                playerDict = self.nfldata.get_player_by_id(playerId)
                record = dict()
                for col in finalDF.columns:
                    record[col] = None
                record['playerId'] = playerId
                record['firstName'] = playerDict.get('firstName', '')
                record['lastName'] = playerDict.get('lastName', '')
                record['teamId'] = playerDict.get('teamId', 0)
                record['statValue'] = 0
                record['count'] = 0
                record['rank'] = -1
                finalDF = pd.DataFrame([record])
        finalDF=finalDF[cols]
        finalDF['statName'] = statName
        finalDF['statObject'] = object
        finalDF['dimensions'] = str(dimensions)
        finalDF['seasons'] = str(seasons)
        return finalDF

    @contendo_classfunction_logger
    def pbp_get_composed_stat(self, compstat, object, dimensions=['all'], seasons=['2019-regular'], filter='True'):
        assert compstat in self.compStatsDict, "Illegal statName: '{}', must be one of {}".format(statName, self.compStatsDict.keys())
        compstatDef = self.compStatsDict[compstat]
        numerator = compstatDef['NumeratorStatName']
        numeratorDef = self.statsDict[numerator]
        denominator = compstatDef['DenominatorStatName']
        denominatorDef = self.statsDict[denominator]
        #
        # define the index-key(s) for team/player
        objectDef = self.ptmapDict[object]
        if objectDef['StatObject'] == 'team':
            _keys = 'teamId'
        else:
            _keys = ['playerId', 'teamId']
        #
        # get the numerator data
        numeratorDF = self.pbp_get_stat(numerator, object, dimensions, seasons, filter=filter).set_index(_keys)
        if numeratorDF.shape[0]==0:
            return numeratorDF
        #
        # get the denominator data
        denominatorDF = self.pbp_get_stat(denominator, object, dimensions, seasons, filter=filter).set_index(_keys)
        if denominatorDF.shape[0]==0:
            return denominatorDF

        df = numeratorDF.join(
            denominatorDF,
            rsuffix='_dn',
            on=_keys,
            how='left',

        )
        df['statValue'] = df['statValue']/df['statValue_dn']*compstatDef['StatRatio']
        df.sort_values(by='statValue', ascending=False, inplace=True)
        df['rank'] = df['statValue'].rank(method='dense', ascending=False)
        #
        # updating the parameter-based columns
        df['statName'] = compstat
        df['statObject'] = object
        df['dimensions'] = str(dimensions)
        df['seasons'] = str(seasons)
        df.reset_index(level=_keys, inplace=True)
        #
        # disposing of irrelevant (duplicate) denominator columns.
        retCols = list()
        for col in df.columns:
            if col.find('_dn')==-1 or col==denominatorDef['AggField']+'_dn':
                retCols.append(col)
        return df[retCols]

@contendo_function_logger
def test_all_stats(generator):
    counter=dict()
    results=[]
    for statName, statDef in generator.statsDict.items():
        if statDef['Condition']=='' or statDef['Doit'] != 'y':
            continue
        for condCode, condDef in generator.dimentionsDict.items():
            for object, objectDef in generator.ptmapDict.items():
                #
                # only do if defined as 1
                if statDef[object] != 'y':
                    continue

                #if condDef['Condition']=='' or playCondDef['Condition']=='':
                    #logger.debug ('skipping %s, %s, %s', statDef, condDef, playCondDef)
                    #continue
                if condDef['playType'] != 'all' and condDef['playType'].find(statDef['playType'])==-1:
                    continue

                df = generator.pbp_get_stat(statName=statName, object=object, dimensions=[condCode])
                isResults = (df.shape[0]>0)
                counter[isResults] = counter.get(isResults, 0)+1
                logger.info ('%s, %s, %s, %s, %s, %s', counter[isResults], isResults, df.shape, statName, object, condCode)
                if isResults:
                    results.append(
                        {
                            'StatName': statName,
                            'Object': object,
                            'StatObject': objectDef['StatObject'],
                            'dimensions': condCode,
                            'nResults': df.shape[0],
                        }
                    )

    print(counter)
    keys = results[0].keys()
    resultsDF = pd.DataFrame(results, columns=keys)
    from gspread_pandas import Spread, Client
    spread = Spread(generator.ccm.get_domain_docid('Football.NFL'))
    spread.df_to_sheet(resultsDF, index=False, sheet='PBP Stats results', start='A1', replace=True)

# Main Test function
@contendo_function_logger
def test():
    startTime=dt.now()
    pd.set_option('display.max_columns', 20)
    pd.set_option('display.width', 200)
    #os.environ['CONTENDO_AT_HOME'] = 'y'
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "{}/sportsight-tests.json".format(os.environ["HOME"])
    os.environ['CONTENDO_DEV']='y'
    os.chdir('{}/tmp/'.format(os.environ["HOME"]))
    generator = NFLStatsQueries()
    #print(generator._generate_pbp_query())
    logger.info('Start updating pbp data, delta = %s', dt.now() - startTime)
    #generator.nfldata._update_pbp_data()
    logger.info('Start querying data, delta = %s', dt.now() - startTime)
    df = generator.pbp_get_stat(statName='yardsPassed', object='defenseTeam', dimensions=['all', 'all'], seasons=['2019-regular'])
    df = df.set_index('teamId')
    logger.info('Columns={}, Shape={}\n\n{}\n\n'.format(df.columns, df.shape, df))
    #df = generator.pbp_get_stat('rushes', 'rushingPlayer', ['conversion3', '4thQ'], seasons=['2019-regular'], trace=False, playerId=12606)
    df = generator.pbp_get_stat('rushes', 'rushingPlayer', ['conversion3', '4thQ'], seasons=['2019-regular'], trace=False, playerId=12606)
    logger.info('Columns={}, Shape={}\n{}'.format(df.columns, df.shape, df))
    df = generator.pbp_get_composed_stat('yardsPerCarry', 'rushingPlayer', seasons=['2019-regular'])
    logger.info('Columns={}, Shape={}\n{}'.format(df.columns, df.shape, df))
    logger.info('Done, delta=%s', dt.now() - startTime)

if __name__ == '__main__':
    contendo_logging_setup(default_level=logging.DEBUG)
    test()
