""" Queries for hitting the Catan database """
from utils_package.data_controller.pg_util import PGUtil
from utils_package.data_controller import query_tools


class GamePlayerRelWriter(object):
    """ Queries for writing to the Catan database's player game relationship table """

    def __init__(self):
        """ Set up class variables """
        self.game_pg = PGUtil(user='writer', database='catan_local')

    def insert_new_game(self, rel_dict):
        """
        Inserts a new game into the database
        :param rel_dict: Dictionary of the relationship information
        :return: Row count and SQL response
        """
        columns, values = query_tools.insert_string_from_dict(rel_dict)
        sql = """
        INSERT INTO catan_game.game_player_rel
                    (%s)
        VALUES      (%s)
        """ % (columns, values)
        response = self.game_pg.execute_query(sql)
        assert response[0] == 1
        assert response[1] is None
        return response


class GamePlayerRelReader(object):
    """ Queries for reading the Catan database's game table """

    def __init__(self):
        """ Set up class variables """
        self.game_pg = PGUtil(user='reader', database='catan_local')

    def get_games_for_player_id(self, player_id):
        """
        Gets a record based on a value
        :param player_id:
        :return:
        """
        sql = """
        SELECT *
        FROM   catan_game.game_player_rel
        WHERE  player_id = %s
        """ % player_id
        response = self.game_pg.execute_query(sql)
        assert response[0] >= 1
        assert response[1] is not None
        return response[1]

    def get_players_for_game_id(self, game_id):
        """
        Gets a record based on a game_id
        :param game_id:
        :return:
        """
        sql = """
        SELECT *
        FROM   catan_game.game_player_rel
        WHERE  game_id = %s
        """ % game_id
        response = self.game_pg.execute_query(sql)
        assert response[0] >= 1
        assert response[1] is not None
        return response[1]

