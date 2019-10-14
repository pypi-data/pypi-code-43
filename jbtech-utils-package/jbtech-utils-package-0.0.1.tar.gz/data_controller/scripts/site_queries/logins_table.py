from data_controller.pg_util import PGUtil
from data_controller import query_tools
from datetime import date


class LoginsTableWriter(object):
    """ Queries for writing to the Catan database's logins table """

    def __init__(self):
        """ Initialize class variables """
        self.login_pg = PGUtil(user='writer', database='catan_local')

    def insert_new_login(self, rel_dict):
        """
        Inserts a new login into the database
        :param rel_dict: Dictionary of the relationship information
        :return: Row count and SQL ewsponse
        """
        columns, values = query_tools.insert_string_from_dict(rel_dict)
        sql = """
        INSERT INTO catan_game.logins_table
                    (%s)
        VALUES      (%s)
        """ % (columns, values)
        response = self.login_pg.execute_query(sql)
        assert response[0] == 1
        assert response[1] is None
        return response

    def update_login_by_id(self, rel_dict, login_id, update_date=None):
        """
        Updates a login record on the database
        :param rel_dict: Dictionary of the game update information
        :param login_id: ID associated with the game being updated
        :param update_date: Datetime of the date
        :return: Row count and SQL response
        """
        if 'update' in rel_dict.keys():
            update_str = query_tools.update_string_from_dict(rel_dict)
        elif 'update' not in rel_dict.keys():
            if update_date is None:
                update_date = date.today()
            rel_dict['update'] = str(update_date)
            update_str = query_tools.update_string_from_dict(rel_dict)
        else:
            update_str = 'Something has gone wrong'

        sql = """
        UPDATE catan_game.logins_table
        SET    %s
        WHERE  id = %s
        """ % (update_str, login_id)
        response = self.login_pg.execute_query(sql)
        assert response[0] == 1
        assert response[1] is None
        return response


class LoginsTableReader(object):
    """ Queries for reading the Catan database's logins table """

    def __init__(self):
        """ Initialize class variables """
        self.login_pg = PGUtil(user='reader', database='catan_local')

    def get_login_for_username(self, username):
        """
        Gets the login for a username
        :param username: String of the username
        :return: Response of full record from the database
        """
        sql = """
        SELECT *
        FROM   catan_game.logins_table
        WHERE  username = '%s'
        """ % username
        response = self.login_pg.execute_query(sql)
        assert response[0] >= 1
        assert response[1] is not None
        return response[1]