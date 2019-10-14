""" Unit tests for game queries """
from utils_package.data_controller.scripts.catan.player_queries import PlayerPGWriter, PlayerPGReader
from unittest import TestCase
import random


class TestPlayerQueries(TestCase):
    """ Unit tests for game queries """

    def setUp(self):
        """ Set up class variables """
        self.player_writer_q = PlayerPGWriter()
        self.player_reader_q = PlayerPGReader()

    def test_insert_read_player(self):
        """ Test to validate the insert of a new user into the player's table
        1. Generate a user dictionary (email must be unique)
        2. Send the insert user request
        3. Validate the user is inserted into the table
        """

        # 1. Generate a user dictionary (email must be unique)
        user_dict = {
            'first_name': 'Green',
            'last_name': 'Goblin',
            'email': 'GG_%s@hotmail.com' % str(random.randint(0, 999))
        }

        # 2. Send the insert user request
        response = self.player_writer_q.insert_new_player(user_dict)
        self.assertEqual(1, response[0])
        self.assertIsNone(response[1])

        # 3. Validate the user is inserted into the table
        response = self.player_reader_q.get_player_by_email(user_dict['email'])
        self.assertEqual(user_dict['first_name'], response[0]['first_name'])
        self.assertEqual(user_dict['last_name'], response[0]['last_name'])
        self.assertEqual(user_dict['email'], response[0]['email'])

    def test_update_player(self):
        """ Test to validate the update of a player on the player's table
        1. Generate a user dictionary (email must be unique)
        2. Generate an update dictionary
        3. Send the insert user request
        4. Validate the user is inserted into the table
        5. Send the update user request
        6. Validate the user is update on the table
        """

        # 1. Generate a user dictionary (email must be unique)
        user_dict = {
            'first_name': 'Peter',
            'last_name': 'Parker',
            'email': 'GG_%s@hotmail.com' % str(random.randint(0, 999))
        }

        # 2. Generate an update dictionary
        update_dict = {
            'first_name': 'Spiderman',
            'last_name': 'REDACTED'
        }

        # 3. Send the insert user request
        response = self.player_writer_q.insert_new_player(user_dict)
        self.assertEqual(1, response[0])
        self.assertIsNone(response[1])

        # 4. Validate the user is inserted into the table
        response = self.player_reader_q.get_player_by_email(user_dict['email'])
        self.assertIsNotNone(response)
        self.assertEqual(user_dict['first_name'], response[0]['first_name'])
        self.assertEqual(user_dict['last_name'], response[0]['last_name'])
        self.assertEqual(user_dict['email'], response[0]['email'])
        player_id = response[0]['id']

        # 5. Send the update user request
        response = self.player_writer_q.update_player_by_player_id(update_dict, player_id)
        self.assertIsNotNone(response)

        # 6. Validate the user is update on the table
        response = self.player_reader_q.get_player_by_id(player_id)
        self.assertIsNotNone(response)
        self.assertEqual(update_dict['first_name'], response[0]['first_name'])
        self.assertEqual(update_dict['last_name'], response[0]['last_name'])
        self.assertEqual(user_dict['email'], response[0]['email'])