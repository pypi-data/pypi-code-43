import os
import pandas as pd
from datetime import datetime as dt
from pathlib import Path

from gspread_pandas import Spread, Client

from contendo_utils import ProUtils
from sports_insights import SportsStatsGenerator
import nfl_insights

class NFLStatsGenerator(SportsStatsGenerator):
    #
    # read in the configurations
    def __init__(self):
        self.domain = NFL_DOMAIN_NAME
        SportsStatsGenerator.__init__(self, self.domain, domainConfigGID=NFL_DOMAIN_CONFIG_GID, queriesRoot=str(Path(__file__).parent))
        #
        # get the initial configuration

    def nfl_pbp_queries_generator(self, queriesQueue, sourceConfig, startTime, stats=None):
        #
        # create jobs for all relevant metrics.

        #
        # Get the dimentions and player/team map definitions.
        dimentionsDict = self.ccm.get_configuration_dict(self.domain, 550054182, 'ConditionCode')
        ptmapDict = self.ccm.get_configuration_dict(self.domain, 1185264127, 'Object')

        for statDef in sourceConfig['StatsDefDict'].values():
            if stats:
                if statDef['StatName'] not in stats:
                    continue
            #
            # only produce if the condition is defined.
            if statDef['Condition']=='':
                continue

            if statDef['DoIT']!='y':
                continue

            sourceDefinitions = self.definitions[sourceConfig['StatSource']]
            statTimeframe = sourceConfig['StatTimeframe']
            for condCode, condDef in dimentionsDict.items():
                for object, objectDef in ptmapDict.items():
                    #
                    # only do if defined as 1
                    if condDef[object] != 1 or statDef[object]=='' or condDef['Condition']=='':
                        continue

                    statObject = objectDef['StatObject']

                    query = sourceConfig['query']
                    query = query.replace('{StatObject}', statObject)
                    query = query.replace('{StatTimeframe}', statTimeframe)
                    if sourceConfig['StatCondition'] != '':
                        query = ProUtils.format_string(query, eval("self."+sourceConfig['StatCondition']))
                    else:
                        query = ProUtils.format_string(query, {'StatCondition': True})

                    queryInst = {
                        'DaysRange':        sourceConfig['DateProperty'],
                        'PBPCondition':     '{} and {}'.format(condDef['Condition'], statDef['Condition']),
                        'StatName':         'pbp.{}.{}.{}'.format(statDef['StatName'], object, condCode),
                        'BaseStat':         statDef['StatName'],
                        'ObjectType':       object,
                        'ConditionCode':    condCode,
                        'TeamType':         objectDef['TeamType'],
                        'PlayerProperty':   statDef[object],
                        #'PropertyName':     '{}{}{}'.format(objectDef['Prefix'], statDef[object], objectDef['Suffix']),
                    }

                    query = ProUtils.format_string(query, sourceDefinitions['StatObject'][statObject])
                    query=ProUtils.format_string(query, queryInst)
                    query=ProUtils.format_string(query, statDef)
                    query=ProUtils.format_string(query, sourceConfig)
                    #
                    # define the destination table
                    instructions = statDef.copy()
                    instructions['StatName'] = queryInst['StatName']
                    instructions['StatObject'] = statObject
                    instructions['StatTimeframe'] = statTimeframe
                    instructions['StatSource'] = sourceConfig['StatSource']
                    instructions['DaysRange'] = instructions.get('DaysRange', 'N/A')
                    targetTable = ProUtils.format_string(self.targetTableFormat, instructions).replace('.', '_')
                    jobDefinition = {
                        'queryJob': {
                            'params': {
                                'query': query,
                                'targetDataset': self.targetDataset,
                                'targetTable': targetTable,
                            },
                            'StatName': queryInst['StatName'],
                            'StatObject': statObject,
                            'StatTimeframe': statTimeframe,
                        }
                    }

                    queriesQueue.put(ProducerConsumersEngine.PCEngineJobData(self.query_executor, jobDefinition))

    def nfl_pbp_metricsdef_generator(self):
        #
        # Get the dimentions and player/team map definitions.
        gameDimentionsDict = self.ccm.get_configuration_dict(self.domain, 1621060823, 'ConditionCode')
        playDimentionsDict = self.ccm.get_configuration_dict(self.domain, 1120955874, 'ConditionCode')
        ptmapDict = self.ccm.get_configuration_dict(self.domain, 582380093, 'Object')
        metricsList=[]
        #
        # internal function that calculates
        def calc_questions_for_basestat(statDef, qDef, statTimeframe, statBaseName):
            for gameCondCode, gameCondDef in gameDimentionsDict.items():
                for playCondCode, playCondDef in playDimentionsDict.items():
                    for object, objectDef in ptmapDict.items():
                        #
                        # only do if defined as 1
                        if gameCondDef[object] != 1 or statDef[object] != 1 \
                                or gameCondDef['Condition']=='' or gameCondDef['Condition']=='':
                            continue
                        if playCondDef['playType'] != 'all' and playCondDef['playType'].find(statDef['playType'])==-1:
                            continue

                        #
                        # build the statname
                        statName = 'pbp.{}.{}.{}.{}'.format(statBaseName, object, gameCondCode, playCondCode)
                        if playCondCode == 'all':
                            playConditionText = ''
                        else:
                            playConditionText = 'and ' + playCondDef['TextPrimary']

                        inst = {
                            'Description': statDef['Description'],
                            'GameConditionText': gameCondDef['Conditiontext'],
                            'PlayConditionText': playConditionText,
                            'ObjectType': objectDef['ObjectType'],
                            #'Timeframe': timeFrameTexts[random.randint(0,len(timeFrameTexts)-1)],
                        }
                        description = ProUtils.format_string(statDef['DescriptionTemplate'], inst)
                        while description.find('  ')  > -1:
                            description = description.replace('  ', ' ')
                        #
                        # set the question definition.
                        questionDef = {
                            #'QuestionCode': statName,
                            'StatName': statName,
                            'Description': description,
                            'BaseStat': statBaseName,
                            'Object': object,
                            'GameDimention': gameCondCode,
                            'PlayDimention': playCondCode,
                            #'StatObject': objectDef['StatObject'],
                            #'Level': '',
                            #'Value1Template': qDef['ValueTemplate'],
                            #'Value2Template': qDef['ValueTemplate'],
                            #'Question2Objects': question,
                            #'Doit': 'y'
                        }
                        metricsList.append(questionDef)

        #
        # create jobs for PBP metrics
        pbpConfig = self.get_source_configuration('Football.PBP.Season')

        for statDef in pbpConfig['StatsDefDict'].values():
            #
            # only produce if the condition is defined.
            if statDef['Condition']=='':
                continue

            #timeFrameTexts = sourceConfig['Timeframe'].split(',')

            statTimeframe = pbpConfig['StatTimeframe']
            statBaseName = statDef['StatName']
            calc_questions_for_basestat(statDef, statDef, statTimeframe, statBaseName)

        composedConfig = self.get_source_configuration('Football.PBPComposed')
        for compDef in composedConfig['StatsDefDict'].values():
            #
            # only produce if the condition is defined.
            statDef = pbpConfig['StatsDefDict'][compDef['NumeratorStatNames']]
            statTimeframe = composedConfig['StatTimeframe']
            statBaseName = compDef['StatName']
            calc_questions_for_basestat(statDef, compDef, statTimeframe, statBaseName)

        keys = metricsList[0].keys()
        questionsDF = pd.DataFrame(metricsList, columns=keys)
        questionsDF.to_csv('mlb-pbp-questionsList.csv')
        spread = Spread(self.ccm.get_domain_docid('Football.NFL'))
        spread.df_to_sheet(questionsDF, index=False, sheet='PBP Stat Description', start='A1', replace=True)


    def nfl_complex_queries_generator(self, queriesQueue, sourceConfig, startTime, stats=None):
        #
        # create jobs for all relevant metrics.
        for statDef in sourceConfig['StatsDefDict'].values():

            if statDef['Doit']!='y':
                continue

            #print('Metric: {}, Sport:{}, Delta time: {}'.format(statDef['StatName'], statDef['SportCode'], dt.now() - startTime), flush=True)
            inst={}
            inst ['StatTimeframes'] = ProUtils.commastring_to_liststring(statDef['StatTimeframes'])
            inst['StatObjects'] = ProUtils.commastring_to_liststring(statDef['StatObjects'])
            inst['NumeratorStatNames'] = ProUtils.commastring_to_liststring(statDef['NumeratorStatNames'])
            inst['DenominatorStatNames'] = ProUtils.commastring_to_liststring(statDef['DenominatorStatNames'])
            query = sourceConfig['query']
            query=ProUtils.format_string(query, inst)
            query=ProUtils.format_string(query, statDef)
            query=ProUtils.format_string(query, sourceConfig)
            #print (query)
            #
            # define the destination table
            instructions = statDef
            instructions['StatObject'] = statDef['StatObjects'].replace(',', '_')
            instructions['StatTimeframe'] = statDef['StatTimeframes'].replace(',', '_')
            instructions['StatSource'] = sourceConfig['StatSource']
            targetTable = ProUtils.format_string(self.targetTableFormat, instructions).replace('.', '_')
            jobDefinition = {
                'queryJob': {
                    'params': {
                        'query': query,
                        'targetDataset': self.targetDataset,
                        'targetTable': targetTable,
                    },
                    'StatName': statDef['StatName'],
                    'StatObject': instructions['StatObject'],
                    'StatTimeframe': instructions['StatTimeframe']
                }
            }
            queriesQueue.put(ProducerConsumersEngine.PCEngineJobData(self.query_executor, jobDefinition))


def test():
    startTime=dt.now()
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "{}/sportsight-tests.json".format(os.environ["HOME"])
    os.chdir('{}/tmp/'.format(os.environ["HOME"]))
    generator = NFLStatsGenerator()#'Baseball.PlayerSeasonStats')
    generator.nfl_pbp_metricsdef_generator()
    #generator.run()
    #generator.run(configurations=['Baseball.GameStats.Game'], stats=['batting.atBats'], startTime=startTime)
    #generator.run(configurations=['Baseball.ComposedStats'], numExecutors=5)
    #generator.run(configurations=['Baseball.PBPv2.Season', 'Baseball.SeasonStats'])
    #generator.run(numExecutors=0, configurations=['Baseball.PBPv2.Season'], stats=['hits'], startTime=startTime)
    #generator.run(configurations=['Baseball.PBPv2.Game', 'Baseball.GameStats.Game'])
    #generator.run(configurations=['Baseball.PBPComposedStats'])

if __name__ == '__main__':
    #print(globals())
    #print(__file__)
    #print(Path(__file__).parent)
    test()
    #print(spread.sheets)
