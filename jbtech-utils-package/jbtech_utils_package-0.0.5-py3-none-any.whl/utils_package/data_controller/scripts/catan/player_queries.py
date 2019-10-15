""" Queries for hitting the Catan database """
from utils_package.data_controller.pg_util import PGUtil
from utils_package.data_controller import query_tools


class PlayerPGWriter(object):
    """ Queries for writing to the Catan database's player table """

    def __init__(self):
        """ Set up class variables """
        self.game_pg = PGUtil(user='writer', database='catan_local')

    def insert_new_player(self, user_dict):
        """
        Inserts a new user into the database
        :param user_dict: Dictionary of user setup information
        :return: Row count and SQL response
        """
        columns, values = query_tools.insert_string_from_dict(user_dict)
        sql = """
        INSERT INTO catan_game.players 
                    (%s) 
        VALUES      (%s) 
        """ % (columns, values)
        response = self.game_pg.execute_query(sql)
        assert response[0] == 1
        assert response[1] is None
        return response

    def update_player_by_player_id(self, update_dict, player_id):
        """
        Updates the fields based on the update dict
        :param update_dict: Dictionariy of SQL updates
        :param player_id: Player ID for the record to be returned
        :return:
        """
        update_str = query_tools.update_string_from_dict(update_dict)
        sql = """
        UPDATE catan_game.players 
        SET    %s
        WHERE  id = %s
        """ % (update_str, player_id)
        response = self.game_pg.execute_query(sql)
        assert response[0] == 1
        assert response[1] is None
        return response


class PlayerPGReader(object):
    """ Queries for reading the Catan database's player table """
    def __init__(self):
        """ Set up class variables """
        self.game_pg = PGUtil(user='reader', database='catan_local')

    def get_player_by_email(self, email):
        """
        Get's the player's record by email address
        :param email:
        :return:
        """
        sql = """
        SELECT * 
        FROM   catan_game.players 
        WHERE  email = '%s'
        """ % email
        response = self.game_pg.execute_query(sql)
        assert response[0] == 1
        assert response[1] is not None
        return response[1]

    def get_player_by_id(self, player_id):
        """
        Get's the player's record by ID
        :param player_id:
        :return:
        """
        sql = """
        SELECT * 
        FROM   catan_game.players 
        WHERE  id = '%s'
        """ % player_id
        response = self.game_pg.execute_query(sql)
        assert response[0] == 1
        assert response[1] is not None
        return response[1]
