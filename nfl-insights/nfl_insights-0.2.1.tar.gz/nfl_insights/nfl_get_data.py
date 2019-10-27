import os
import pandas as pd
from datetime import datetime as dt
from pathlib import Path
import logging

import gspread

from contendo_utils import *
from nfl_insights import *

# noinspection PyUnresolvedReferences
class NFLGetData():
    #
    # read in the configurations
    def __init__(self, project=None):
        #
        # get the initial configurations
        self.ccm = ContendoConfigurationManager()
        #
        # initialize BQ
        self.bqu = BigqueryUtils(project)
        #
        # data files definitions
        self.dataObjects = ['games', 'teams', 'players']
        self.resourceDir = 'resource'
        self.pbpDataFileName = '{}/pbp_data.csv'.format(self.resourceDir)
        #
        # data variables
        self.pbpDF = None
        self.dataDFs = dict()

    @contendo_classfunction_logger
    def get_games(self, filter='game.homeTeam!=""'):
        if self.gamesDF == None:
            gamesQuery = ProUtils.get_string_from_file(
                '{}/queries/nfl_games_info.sql'.format(Path(__file__).parent)
            )
            self.gamesDF = self.bqu.execute_query_to_df(query)
        game = self.gamesDF
        return eval('game[({})]'.format(filter))

    @contendo_classfunction_logger
    def _update_nfl_data(self, source, outfile):
        assert source in self.dataObjects, 'Illegal source: {}, must be one of {}'.format(source, self.dataObjects)
        _query = ProUtils.get_string_from_file('{}/queries/nfl_{}_info.sql'.format(Path(__file__).parent, source))
        _df = self.bqu.execute_query_to_df(_query)
        logger.debug('Read %s query data, shape=%s, columns=%s', source, _df.shape, _df.columns)
        ProUtils.create_path_directories(outfile)
        _df.to_csv(outfile, index=False)
        logger.debug('Updated players file %s', outfile)
        self.dataDFs[source]=_df

    @contendo_classfunction_logger
    def _read_nfl_data(self, source):
        #
        # Read the pbp data from file.
        _datafile = '{resourceDir}/{source}_data.csv'.format(resourceDir=self.resourceDir, source=source)
        if not os.path.exists(_datafile):
            logger.debug('Getting players data')
            self._update_nfl_data(source, _datafile)

        logger.debug('Checking players DF existance')
        if not source in self.dataDFs:
            self.dataDFs[source] = pd.read_csv(_datafile)

    @contendo_classfunction_logger
    def get_player_by_id(self, playerId, season='2019-regular'):
        self._read_nfl_data('players')
        query = '(playerId=={}) & (season=="{}")'.format(playerId, season)
        logger.debug('Players query= %s', query)
        _playerDF = self.dataDFs['players'].query(query)
        if _playerDF.shape[0] == 0:
            # Error
            logger.error('Player id %s not found', playerId)
            return {}

        return dict(_playerDF.iloc[0])

    @contendo_classfunction_logger
    def get_players_df(self, season):
        self._read_nfl_data('players')
        _playersDF = self.dataDFs['players'].query('season=="{}"'.format(season))
        _playersDF.set_index(['playerId', 'teamId'], inplace=True)
        return _playersDF

    @contendo_classfunction_logger
    def get_teams_df(self, season):
        self._read_nfl_data('teams')
        _teamsDF = self.dataDFs['teams'].query('season=="{}"'.format(season))
        _teamsDF.set_index(['teamId'], inplace=True)
        return _teamsDF

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

    def _update_pbp_data(self):
        #
        # generate the pbp BQ query and execute.
        pbpQuery = self._generate_pbp_query()
        _pbpDF = self.bqu.execute_query_to_df(pbpQuery)
        #
        # make sure the directory exists and save the file.
        ProUtils.create_path_directories(self.pbpDataFileName)
        _pbpDF.to_csv(self.pbpDataFileName)

    def get_pbp_data(self):
        #
        # Read the pbp data from file.
        if not os.path.exists(self.pbpDataFileName):
            self._update_pbp_data()
        if self.pbpDF is None:
            self.pbpDF = pd.read_csv(self.pbpDataFileName)

        return self.pbpDF

# Main Test function
@contendo_function_logger
def test():
    startTime=dt.now()
    pd.set_option('display.max_columns', 20)
    pd.set_option('display.width', 200)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "{}/sportsight-tests.json".format(os.environ["HOME"])
    os.environ['CONTENDO_DEV']='y'
    os.chdir('{}/tmp/'.format(os.environ["HOME"]))
    nfldata = NFLGetData()
    print(nfldata.get_players_df(season='2019-regular'))
    print(nfldata.get_player_by_id(playerId=12606))
    print(nfldata.get_teams_df(season='2019-regular'))

if __name__ == '__main__':
    contendo_logging_setup(default_level=logging.DEBUG)
    test()
