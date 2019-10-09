from datetime import datetime
from test.base import ClientBaseCase

from lendsmart_api.objects import PredictionChunk, PredictionWorkflow
from lendsmart_api.objects.base import MappedObject


class PredictionChunkTest(ClientBaseCase):
    """
    Tests methods of the PredictionChunk class
    """
    def test_get_chunk(self):
        """
        Tests that a chunk is loaded correctly by ID
        """
        client = PredictionChunk(self.client, 1234)
        self.assertEqual(client._populated, False)

        self.assertEqual(client.label, 'test_client_1')
        self.assertEqual(client._populated, True)

        self.assertIsInstance(client.created, datetime)
        self.assertIsInstance(client.updated, datetime)

        self.assertIsInstance(client.apps, MappedObject)
        self.assertFalse(client.apps.nginx)
        self.assertFalse(client.apps.mysql)
        self.assertFalse(client.apps.apache)

        self.assertEqual(client.install_code, '12345678-ABCD-EF01-23456789ABCDEF12')
        self.assertEqual(client.api_key, '12345678-ABCD-EF01-23456789ABCDEF12')


class PredictionWorkflow(ClientBaseCase):
    """
    Tests methods of the PredictionWorkflow class
    """
    def test_get_prediction_workflow(self):
        """
        Tests that a prediction workflow is loaded correctly by ID
        """
        sub = PredictionWorkflow(self.client)
        self.assertEqual(sub.label, 'Longview Pro 40 pack')
