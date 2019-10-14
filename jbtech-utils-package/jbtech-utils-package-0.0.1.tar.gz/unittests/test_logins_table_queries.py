""" Unit tests for the logins table queries """
from data_controller.scripts.site_queries.logins_table import LoginsTableWriter, LoginsTableReader
from unittest import TestCase
import random


class TestLogingsTableQuereis(TestCase):
    """ Unit tests for logins table queries """

    def setUp(self):
        """ Set up class variables """
        self.logins_writer_q = LoginsTableWriter()
        self.logins_reader_q = LoginsTableReader()

    def test_insert_read_login(self):
        """ Test to validate the insert of a new login into the logins table
        1. Generate the proper dictionary
        2. Send the insert request
        3. Validate the user is inserted into the table
        """

        # 1. Generate the proper dictionary
        logins_dict = {
            'username': 'green_goblin' + str(random.randint(000, 999)),
            'pass_hash': '$2b$12$gaNFpXmQ/pvD7/RAw4oQxuBITtcc/KBQ4poAHj0baL9uiGuT/Fdji',
        }

        # 2. Send the insert request
        response = self.logins_writer_q.insert_new_login(logins_dict)
        self.assertEqual(1, response[0])
        self.assertIsNone(response[1])

        # 3. Validate the user is inserted into the table
        response = self.logins_reader_q.get_login_for_username(logins_dict['username'])
        self.assertEqual(logins_dict['username'], response[0]['username'])
        self.assertEqual(logins_dict['pass_hash'], response[0]['pass_hash'])

    def test_update_read_login(self):
        """ Test to validate the insert of a new login into the logins table
        1. Generate the proper dictionaries
        2. Send the insert request
        3. Validate the user is inserted into the table
        4. Update the user and password
        5. Validate the user is updated in the table
        """

        # 1. Generate the proper dictionaries
        logins_dict = {
            'username': 'peter_parker' + str(random.randint(000, 999)),
            'pass_hash': 'is_spiderman',
        }

        update_dict = {
            'pass_hash': 'is_not_spiderman'
        }

        # 2. Send the insert request
        response = self.logins_writer_q.insert_new_login(logins_dict)
        self.assertEqual(1, response[0])
        self.assertIsNone(response[1])

        # 3. Validate the user is inserted into the table
        response = self.logins_reader_q.get_login_for_username(logins_dict['username'])
        self.assertEqual(logins_dict['username'], response[0]['username'])
        self.assertEqual(logins_dict['pass_hash'], response[0]['pass_hash'])

        # 4. Update the user and password
        response = self.logins_writer_q.update_login_by_id(update_dict, response[0]['id'])
        self.assertIsNotNone(response)

        # 5. Validate the user is updated in the table
        response = self.logins_reader_q.get_login_for_username(logins_dict['username'])
        self.assertEqual(update_dict['pass_hash'], response[0]['pass_hash'])
        self.assertEqual(logins_dict['username'], response[0]['username'])