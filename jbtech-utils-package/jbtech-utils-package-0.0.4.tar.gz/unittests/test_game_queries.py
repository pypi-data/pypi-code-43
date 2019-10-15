""" Unit tests for game queries """
from utils_package.data_controller.scripts.catan.games_queries import GamePGWriter, GamePGReader
from unittest import TestCase


class TestGameQueries(TestCase):
    """ Unit tests for game queries """

    def setUp(self):
        """ Set up class variables """
        self.game_writer_q = GamePGWriter()
        self.game_reader_q = GamePGReader()

    def test_insert_read_game(self):
        """ Validate that a game can be appropriately created and read
        1. Generate a game dictionary
        2. Send the insert game request
        3. Validate the game is created
        """

        # 1. Generate a game dictionary
        insert_dict = {
            'game_name' : 'Spiderman 4: Never gonna happen',
            'game_json': 'test_game_json/test_file/thing.json'
        }

        # 2. Send the insert game request
        response = self.game_writer_q.insert_new_game(insert_dict)

        # 3. Validate the game is created
        self.assertIsNotNone(response)

    def test_update_game(self):
        """ Validate that a game can be appropriately created and read
        1. Generate a update dictionary
        2. Send in the update game request
        3. Valudate the change is made
        """

        # 1. Generate a update dictionary
        update_dict = {
            'game_name': 'Spiderman 5: This is a joke'
        }

        # 2. Send in the update game request
        response = self.game_writer_q.update_game_by_id(update_dict,1)

        # 3. Valudate the change is made
        self.assertIsNotNone(response)

    def test_get_game_by_id(self):
        """ Quick test to validate get game by ID
        1. Build the request
        2. Assert there is some value
        """
        response = self.game_reader_q.get_games_by_id(1)
        self.assertIsNotNone(response)

    def test_get_max_game_id(self):
        """ Quick test to validate get max game ID
        1. Build the request
        2. Assert there is some value
        """
        response = self.game_reader_q.get_max_id()
        self.assertIsNotNone(response)