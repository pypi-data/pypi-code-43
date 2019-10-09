import os
import pandas as pd
from datetime import datetime as dt
from pathlib import Path

from gspread_pandas import Spread, Client

from contendo_utils import ProUtils
from sports_insights import SportsStatsGenerator
import nfl_insights

class FinanceStatsGenerator(ProducerConsumersEngine):
    #
    # read in the configurations
    def __init__(self):
        self.domain = 'Finance.Stocks'
        self.domainGID = 284194018
        ProducerConsumersEngine.__init__(self, )
        #
        # get the initial configuration
    def query_executor(self, queryJob, startTime, **kwargs):
        try:
            nRows = self.bqUtils.execute_query_with_schema_and_target(**queryJob['params'])
            print('Returened for Statname: {} ({} rows), StatObject: {}, StatTimeframe: {}, Detlatime: {}'.format(
                queryJob['StatName'],
                nRows,
                queryJob['StatObject'],
                queryJob['StatTimeframe'],
                dt.now() - startTime),
                  flush=True)
            queryFile = 'results/queries/{}.sql'.format(queryJob['params']['targetTable'])
            f = open(queryFile, 'w')
            f.write(queryJob['params']['query'])
            f.close()
        except Exception as e:
            queryFile = 'errors/{}.sql'.format(queryJob['params']['targetTable'])
            f = open(queryFile, 'w')
            f.write(queryJob['params']['query'])
            f.close()
            # print(queryJob['query'],flush=True)
            print('Error {} with Statname: {}, StatObject: {}, StatTimeframe: {}'.format(e,
                                                                                   queryJob['StatName'],
                                                                                   queryJob['StatObject'],
                                                                                   queryJob['StatTimeframe']),
                                                                                   flush=True)


    def finance_queries_generator(self, queriesQueue, sourceConfig, startTime, stats=None):
        #
        # target table definitions
        financeTableFormat = 'Stat_Finance_{StatSource}_{StatName}_{StatObject}_Rolling_{RollingDays}'
        financeStatsDataset = 'Finance_Stats'
        self.bqUtils.create_dataset(financeStatsDataset)

        #
        # create jobs for all relevant metrics.
        for statDef in sourceConfig['StatsDefDict'].values():

            if statDef['Doit']!='y':
                continue

            #print('Metric: {}, Sport:{}, Delta time: {}'.format(statDef['StatName'], statDef['SportCode'], dt.now() - startTime), flush=True)

            for statObject in statDef['StatObject'].split(',')[:1]:
                for rollingDays in statDef['RollingDaysList'].split(','):
                    _statDef = statDef.copy()
                    _statDef['StatObject'] = statObject
                    rollingDaysInst = {'RollingDays': rollingDays}
                    query = sourceConfig['query']
                    query=ProUtils.format_string(query, _statDef)
                    query=ProUtils.format_string(query, sourceConfig)
                    query=ProUtils.format_string(query, rollingDaysInst)
                    #print (query)
                    #
                    # define the destination table
                    instructions = _statDef
                    instructions['StatTimeframe'] = sourceConfig['StatTimeframe']
                    instructions['StatSource'] = sourceConfig['StatSource']
                    instructions['RollingDays'] = rollingDays
                    targetTable = ProUtils.format_string(financeTableFormat, instructions).replace('.', '_').replace('-', '_')
                    jobDefinition = {
                        'params': {
                            'query': query,
                            'targetDataset': financeStatsDataset,
                            'targetTable': targetTable,
                        },
                        'StatName': _statDef['StatName'],
                        'StatObject': statObject,
                        'StatTimeframe': '{}_Rollingdays'.format(rollingDays)
                    }
                    queriesQueue.put(jobDefinition)

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
