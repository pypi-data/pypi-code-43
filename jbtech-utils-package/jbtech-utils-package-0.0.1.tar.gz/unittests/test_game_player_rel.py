""" Unit tests for game queries """
from data_controller.scripts.catan.game_player_rel import GamePlayerRelWriter, GamePlayerRelReader
from data_controller.scripts.catan.player_queries import PlayerPGWriter, PlayerPGReader
from data_controller.scripts.catan.games_queries import GamePGWriter, GamePGReader
from unittest import TestCase
import random


class TestGamePlayerRelQueries(TestCase):
    """ Unit tests for game queries """

    def setUp(self):
        """ Set up class variables """
        self.pgr_writer = GamePlayerRelWriter()
        self.pgr_reader = GamePlayerRelReader()
        self.player_writer = PlayerPGWriter()
        self.player_reader = PlayerPGReader()
        self.game_writer = GamePGWriter()
        self.game_reader = GamePGReader()

    def test_new_player_and_game(self):
        """ Validate the querying of the game_player_rel table
        1. Generate test data
        2. Generate new player
        3. Validate player created successfully
        4. Generate new game
        5. Validate game created succesfully
        6. Create new game, player relationship record
        7. Validate that record generated apprpriately
        """
        # 1. Generate test data
        user_dict = {
            'first_name': 'John',
            'last_name': 'Parker',
            'email': 'JP_%s@hotmail.com' % str(random.randint(0, 999))
        }
        game_dict = {
            'game_name' : 'Who is this: Never gonna lie',
            'game_json': 'test_game_json/rel/test.json'
        }

        # 2. Generate new player
        response = self.player_writer.insert_new_player(user_dict)
        self.assertIsNotNone(response)

        # 3. Validate player created successfully
        response = self.player_reader.get_player_by_email(user_dict['email'])
        player_id = response[0]['id']
        self.assertIsNotNone(response)

        # 4. Generate new game
        response = self.game_writer.insert_new_game(game_dict)
        self.assertIsNotNone(response)

        # 5. Validate game created succesfully
        game_id = self.game_reader.get_max_id()
        response = self.game_reader.get_games_by_id(game_id)
        self.assertIsNotNone(response)

        # 6. Create new game, player relationship record
        record = {
            'game_id': game_id,
            'player_id': player_id
        }
        response = self.pgr_writer.insert_new_game(record)
        self.assertIsNotNone(response)

        # 7. Validate that record generated apprpriately
        response = self.pgr_reader.get_games_for_player_id(player_id)
        p_id = response[0]['id']
        response = self.pgr_reader.get_players_for_game_id(game_id)
        g_id = response[0]['id']
        self.assertEqual(g_id, p_id)
