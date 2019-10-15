""" Queries for hitting the Catan database """
from utils_package.data_controller.pg_util import PGUtil
from utils_package.data_controller import query_tools


class GamePGWriter(object):
    """ Queries for writing to the Catan database's player table """

    def __init__(self):
        """ Set up class variables """
        self.game_pg = PGUtil(user='writer', database='catan_local')

    def insert_new_game(self, game_dict):
        """
        Inserts a new game into the database
        :param game_dict: Dictionary of the game information
        :return: Row count and SQL response
        """
        columns, values = query_tools.insert_string_from_dict(game_dict)
        sql = """
        INSERT INTO catan_game.games
                    (%s)
        VALUES      (%s)
        """ % (columns, values)
        response = self.game_pg.execute_query(sql)
        assert response[0] == 1
        assert response[1] is None
        return response

    def update_game_by_id(self, update_dict, game_id):
        """
        Updates a game on the database
        :param update_dict: Dictionary of the game update information
        :param game_id: ID associated with the game being updated
        :return: Row count and SQL response
        """
        update_str = query_tools.update_string_from_dict(update_dict)
        sql = """
        UPDATE catan_game.games 
        SET    %s
        WHERE  id = %s
        """ % (update_str, game_id)
        response = self.game_pg.execute_query(sql)
        assert response[0] == 1
        assert response[1] is None
        return response


class GamePGReader(object):
    """ Queries for reading the Catan database's game table """

    def __init__(self):
        """ Set up class variables """
        self.game_pg = PGUtil(user='reader', database='catan_local')

    def get_games_by_id(self, game_id):
        """
        Get's the game by the game ID associated
        :param game_id: ID of the game to be looked up
        :return:
        """
        sql = """
        SELECT *
        FROM   catan_game.games
        WHERE  id = %s
        """ % game_id
        response = self.game_pg.execute_query(sql)
        assert response[0] == 1
        assert response[1] is not None
        return response[1]

    def get_max_id(self):
        """
        Returns the max id on the games table
        :return:
        """
        sql = """
        SELECT  MAX(id)
        FROM    catan_game.games
        """
        response = self.game_pg.execute_query(sql)[1][0][0]
        return response