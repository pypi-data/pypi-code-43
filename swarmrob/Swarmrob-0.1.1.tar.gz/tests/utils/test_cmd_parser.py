import sys
import os

from unittest import TestCase
from unittest.mock import patch
from swarmrob.utils import cmd_parser


class TestArgument(TestCase):
    def test_argument_creation(self):
        verbose = cmd_parser.Argument.VERBOSE
        self.assertEqual(verbose.value, 0)
        self.assertEqual(verbose.short_name, '-v')
        self.assertEqual(verbose.long_name, '--verbose')
        self.assertEqual(verbose.destination, 'verbose')
        self.assertEqual(verbose.action, 'store_true')
        self.assertEqual(verbose.data_type, None)
        self.assertEqual(verbose.required, False)
        self.assertEqual(verbose.help_msg, 'Enable verbose logging mode')


class TestCmdParser(TestCase):
    def test_none_program_path(self):
        _, filename = os.path.split(sys.argv[0])
        path = cmd_parser.CMDParser._get_program_path(None)
        self.assertEqual(path, filename)

    def test_sub_program_path(self):
        _, filename = os.path.split(sys.argv[0])
        path = cmd_parser.CMDParser._get_program_path("sub")
        self.assertEqual(path, filename + " sub")

    def test_default_cmd_parser(self):
        parser = cmd_parser.CMDParser()
        self.assertEqual(parser.parse_arguments().__dict__, {'verbose': False},
                         msg="Default parser must contain verbose argument")

    @patch('sys.argv', ['--verbose'])
    def test_default_cmd_parser_verbose_true(self):
        parser = cmd_parser.CMDParser()
        self.assertEqual(parser.parse_arguments().__dict__, {'verbose': True},
                         msg="Default parser must contain verbose argument")

    @patch('sys.argv', ['--uuid', 'foo', '--interface', 'bar'])
    def test_parser_with_arguments(self):
        parser = cmd_parser.CMDParser(arguments=[cmd_parser.Argument.UUID, cmd_parser.Argument.INTERFACE])
        args = parser.parse_arguments()
        self.assertEqual(args.__dict__, {'verbose': False, 'uuid': 'foo', 'interface': 'bar'},
                         msg='Parsed arguments: "' + str(args.__dict__) + '" are missing something')
