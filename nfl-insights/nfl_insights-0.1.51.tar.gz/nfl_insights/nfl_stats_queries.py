import os
import pandas as pd
from datetime import datetime as dt
from pathlib import Path

import gspread

#from contendo_utils import ProUtils
#from contendo_utils import BigqueryUtils
#from contendo_utils import ContendoConfigurationManager
from contendo_utils import *
import logging

NFL_DOMAIN_NAME = 'Football.NFL'
NFL_DOMAIN_CONFIG_GID = 274419028
NFL_DATA_DATASET = 'NFL_Data'
NFL_PBP_TABLEID = 'all_game_pbp_enriched1'

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
        # initialize BQ
        self.bqu = BigqueryUtils(project)
        #
        # data file name
        self.resourceDir = 'resource'
        self.pbpDataFileName = '{}/pbp_data.csv'.format(self.resourceDir)
        self.playersDataFileName = '{}/players_data.csv'.format(self.resourceDir)
        self.pbpDF = None
        self.gamesDF = None
        self.playersDF = None
        self.cachedDFs = dict()
        self.cachedSeasonDFs = dict()

    @contendo_classfunction_logger
    def _generate_pbp_query(self):
        exceptionList = [
            'interceptedAtPosition',
            'recoveringTeam', #abbreviation
            'fumblingTeam',
            'scrambles',
        ]
        pbp_schema = self.bqu.get_table_schema(NFL_DATA_DATASET, NFL_PBP_TABLEID)
        fieldsList = []
        def aggregate_fieldslist(schema, parent=None):
            def calc_fieldname(name, parent):
                if parent:
                    return '{parent}.{name}'.format(parent=parent, **field)
                else:
                    return name

            for field in schema:
                name = field['name']
                if name in exceptionList or name[0]=='_':
                    continue

                fieldname = calc_fieldname(name, parent)
                if field['type'] == 'RECORD':
                    if field['mode'] == 'REPEATED':
                        logger.debug(name)
                        continue
                    else:
                        aggregate_fieldslist(field['fields'], fieldname)
                else:
                    fieldsList.append('{} as {}'.format(fieldname, fieldname.replace('.','_'), field['type']))

        aggregate_fieldslist(pbp_schema)
        fieldsStr = str(fieldsList).replace('[', '').replace(']', '').replace(',', ',\n').replace("'", '')
        query = 'SELECT {fields} FROM `sportsight-tests.NFL_Data.{tableId}`'.format(fields=fieldsStr, tableId=NFL_PBP_TABLEID)
        if 'CONTENDO_DEV' in os.environ:
            ProUtils.write_string_to_file('{}/queries/pbp_flat_query.sql'.format(str(Path(__file__).parent)), query)
        return query

    def update_pbp_data(self):
        pbpQuery = self._generate_pbp_query()
        _pbpDF = self.bqu.execute_query_to_df(pbpQuery)
        if not os.path.exists(self.resourceDir):
            os.mkdir(self.resourceDir)
        _pbpDF.to_csv(self.pbpDataFileName)

    def _get_pbp_data(self, seasons=None):
        #
        # Read the pbp data from file.
        if not os.path.exists(self.pbpDataFileName):
            self.update_pbp_data()

        if self.pbpDF is None:
            self.pbpDF = pd.read_csv(self.pbpDataFileName)
            self.pbpDF['all']=1
            self.pbpDF['count']=1
            self.pbpDF['counter']=1
            #self.pbpDF = self.pbpDF[(self.pbpDF.season=='2019-regular')]
            #self.pbpDF.set_index("playType", inplace=True)
            self.pbpDF.set_index("season", inplace=True, append=True)
            #self.pbpDF.set_index("playType", inplace=True)
            self.pbpDF['yardsRushed'] = pd.to_numeric(self.pbpDF['yardsRushed'])

        seasons = str(seasons)
        if seasons not in self.cachedSeasonDFs:
            if seasons:
                self.cachedSeasonDFs[seasons] = self.pbpDF.query('season.isin({})'.format(seasons))
            else:
                self.cachedSeasonDFs[seasons] = self.pbpDF

        return self.cachedSeasonDFs[seasons]

    @contendo_classfunction_logger
    def update_players_data(self):
        playersQuery = ProUtils.get_string_from_file('{}/queries/players_info.sql'.format(Path(__file__).parent))
        _playersDF = self.bqu.execute_query_to_df(playersQuery)
        logger.debug('Read players query data, shape=%s, columns=%s', _playersDF.shape, _playersDF.columns)
        ProUtils.create_path_directories(self.resourceDir)
        _playersDF.to_csv(self.playersDataFileName)
        logger.debug('Updated players file %s', self.playersDataFileName)

    @contendo_classfunction_logger
    def _read_players_data(self):
        #
        # Read the pbp data from file.
        logger.debug('Checking players file existance')
        if not os.path.exists(self.playersDataFileName):
            self.update_players_data()

        logger.debug('Checking players DF existance')
        if self.playersDF is None:
            self.playersDF = pd.read_csv(self.playersDataFileName)

    @contendo_classfunction_logger
    def _get_player_by_id(self, playerId):
        self._read_players_data()
        playerDF = self.playersDF[self.playersDF.playerId == playerId]
        if playerDF.shape[0] == 0:
            # Error
            logger.error('Player id %s not found', playerId)
            return {}

        return dict(playerDF.iloc[0])


    def get_games(self, filter='game.homeTeam!=""'):
        if self.gamesDF == None:
            query = """
                SELECT
                  schedule.id as gameid,
                  schedule.homeTeam.abbreviation as homeTeam,
                  schedule.awayTeam.abbreviation as awayTeam,
                  schedule.startTime,
                  score.homeScoreTotal,
                  score.awayScoreTotal,
                  schedule.playedStatus,
                  Season  
                FROM
                  `sportsight-tests.NFL_Data.seasonal_games`
                LEFT JOIN
                  UNNEST (Seasondata.games)
                where schedule.playedStatus = 'COMPLETED'
                order by startTime desc            
            """
            self.gamesDF = self.bqu.execute_query_to_df(query)
        game = self.gamesDF
        return eval('game[({})]'.format(filter))


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
            self._save_trace_df(filteredDF, finalDF.columns, sheetName='trace-{}-{}-{}-{}'.format(statName, object, playDimension, gameDimension))

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
                playerDict = self._get_player_by_id(playerId)
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
            key = 'teamId'
        else:
            key = ['playerId', 'teamId']
        #
        # get the numerator data
        numeratorDF = self.pbp_get_stat(numerator, object, dimensions, seasons, filter=filter).set_index(key)
        if numeratorDF.shape[0]==0:
            return numeratorDF
        #
        # get the denominator data
        denominatorDF = self.pbp_get_stat(denominator, object, dimensions, seasons, filter=filter).set_index(key)
        if denominatorDF.shape[0]==0:
            return denominatorDF

        df = numeratorDF.join(
            denominatorDF,
            rsuffix='_dn',
            on=key,
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
        #
        # disposing of irrelevant (duplicate) denominator columns.
        retCols = list()
        for col in df.columns:
            if col.find('_dn')==-1 or col==denominatorDef['AggField']+'_dn':
                retCols.append(col)
        #df = df.reset_index(level = ['playerId', 'teamId'])
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
    #generator.update_pbp_data()
    logger.info('Start querying data, delta = %s', dt.now() - startTime)
    df = generator.pbp_get_stat(statName='yardsPassed', object='defenseTeam', dimensions=['all', 'all'], seasons=['2019-regular'])
    df = df.set_index('teamId')
    logger.info('Columns={}, Shape={}\n\n{}\n\n'.format(df.columns, df.shape, df))
    #df = generator.pbp_get_stat('rushes', 'rushingPlayer', ['conversion3', '4thQ'], seasons=['2019-regular'], trace=False, playerId=12606)
    df = generator.pbp_get_stat('rushes', 'rushingPlayer', ['conversion3', '4thQ'], seasons=['2019-regular'], trace=False, playerId=12606)
    logger.info('Columns={}, Shape={}\n{}'.format(df.columns, df.shape, df))
    df = generator.pbp_get_composed_stat('yardsPerCarry', 'offenseTeam', seasons=['2019-regular'])
    logger.info('Columns={}, Shape={}\n{}'.format(df.columns, df.shape, df))
    logger.info('Done, delta=%s', dt.now() - startTime)

if __name__ == '__main__':
    contendo_logging_setup(default_level=logging.DEBUG)
    test()
