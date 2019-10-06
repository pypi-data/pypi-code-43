import unittest
from io import StringIO
from unittest.mock import patch

from midpoint_cli.mpclient import MidpointClient, MidpointObject
from midpoint_cli.prompt import MidpointClientPrompt


class MidpointEmptyClientMockup(MidpointClient):
    def __init__(self):
        pass

    def get_tasks(self):
        return []


class MidpointTasksClientMockup(MidpointClient):
    def __init__(self):
        pass

    def get_tasks(self):
        t1 = MidpointObject()
        t1['OID'] = '00000000-0000-0000-0000-000000000005'
        t1['Name'] = 'Cleanup'
        t1['Execution Status'] = 'runnable'

        t2 = MidpointObject()
        t2['OID'] = '00000000-0000-0000-0000-000000000006'
        t2['Name'] = 'Validity Scanner'
        t2['Execution Status'] = 'runnable'

        t3 = MidpointObject()
        t3['OID'] = '00000000-0000-0000-0000-000000000007'
        t3['Name'] = 'Trigger Scanner'
        t3['Execution Status'] = 'runnable'

        return [t1, t2, t3]


class ParserTest(unittest.TestCase):

    @patch('sys.stdout', new_callable=StringIO)
    def test_no_tasks(self, mock_stdout):
        mock_client = MidpointEmptyClientMockup()
        prompt = MidpointClientPrompt(mock_client)
        prompt.onecmd('tasks')
        assert mock_stdout.getvalue().strip() == ''

    @patch('sys.stdout', new_callable=StringIO)
    def test_tasks(self, mock_stdout):
        mock_client = MidpointTasksClientMockup()
        prompt = MidpointClientPrompt(mock_client)
        prompt.onecmd('tasks')
        output = mock_stdout.getvalue()
        assert '00000000-0000-0000-0000-000000000006' in output
        assert 'Trigger Scanner' in output
        assert 'Execution Status' in output


if __name__ == '__main__':
    unittest.main()
