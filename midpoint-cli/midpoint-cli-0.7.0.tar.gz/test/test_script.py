import unittest
from io import StringIO
from unittest.mock import patch

from midpoint_cli.prompt import MidpointClientPrompt


class ScriptTest(unittest.TestCase):
    def test_run_simple_script(self):
        with patch('sys.stdin', StringIO('print("Hello world !")')), \
             patch('sys.stdout', StringIO()) as mock_stdout, \
                patch('midpoint_cli.mpclient.MidpointClient') as mock_client:
            prompt = MidpointClientPrompt(mock_client)
            prompt.onecmd('script run -')
            self.assertIn('Hello', mock_stdout.getvalue().strip())

    def test_assertion_success(self):
        self._run_script('assert 2 == 2')

    def test_assertion_failure(self):
        script = 'assert 2 == 4'

        with patch('sys.stdin', StringIO(script)), \
             patch('sys.stdout', StringIO()), \
             patch('midpoint_cli.mpclient.MidpointClient') as mock_client:
            prompt = MidpointClientPrompt(mock_client)

            try:
                prompt.onecmd('script run -')
                self.fail()
            except AssertionError as ae:
                pass

    def test_globals_client(self):
        self._run_script('assert client is not None')

    def test_globals_tc(self):
        self._run_script('assert tc is not None')

    def test_tc_assertions(self):
        self._run_script('tc.assertEqual(2,2)')
        self._run_script('tc.assertIn("d", "abcde")')

    def _run_script(self, script):
        with patch('sys.stdin', StringIO(script)), \
             patch('sys.stdout', StringIO()), \
             patch('midpoint_cli.mpclient.MidpointClient') as mock_client:
            prompt = MidpointClientPrompt(mock_client)
            prompt.onecmd('script run -')
