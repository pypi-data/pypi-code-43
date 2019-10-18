from datetime import datetime

from test.base import ClientBaseCase

from lendsmart_api import PredictionWorkflow


class LendsmartClientGeneralTest(ClientBaseCase):
    def test_get_documents(self):
        r = self.client.documents()

        self.assertEqual(len(r), 4)
        for doc in r:
            self.assertTrue(doc._populated)
            self.assertIsNotNone(doc.id)

    def test_doc_create(self):
        """
        Tests that an Document can be created successfully
        """
        with self.mock_post('documents') as m:
            i = self.client.document_create(654, 'Test-Image', 'This is a test')

            self.assertIsNotNone(i)
            self.assertEqual(i.id, 'private/123')

            self.assertEqual(m.call_url, '/images')

            self.assertEqual(m.call_data, {
                "disk_id": 654,
                "label": "Test-Image",
                "description": "This is a test",
            })


class PredictionGroupTest(ClientBaseCase):
    """
    Tests methods of the PredictionGroup
    """
    def test_get_chunks(self):
        """
        Tests that a list of PredictionChunks can be retrieved
        """
        r = self.client.prediction.chunks()

        self.assertEqual(len(r), 2)
        self.assertEqual(r[0].label, "test_client_1")
        self.assertEqual(r[0].id, 1234)
        self.assertEqual(r[1].label, "longview5678")
        self.assertEqual(r[1].id, 5678)

    def test_chunk_create(self):
        """
        Tests that creating a chunk calls the api correctly
        """
        with self.mock_post('prediction_chunks') as m:
            client = self.client.prediction.chunk_create()

            self.assertIsNotNone(client)
            self.assertEqual(client.id, 5678)
            self.assertEqual(client.label, 'longview5678')

            self.assertEqual(m.call_url, '/prediction_chunks')
            self.assertEqual(m.call_data, {})

    def test_chunk_create_with_label(self):
        """
        Tests that creating a chunk with a label calls the api correctly
        """
        with self.mock_post('prediction_chunks') as m:
            client = self.client.prediction.chunk_create(label='test_client_1')

            self.assertIsNotNone(client)
            self.assertEqual(client.id, 1234)
            self.assertEqual(client.label, 'test_client_1')

            self.assertEqual(m.call_url, '/prediction_chunks')
            self.assertEqual(m.call_data, {"label": "test_client_1"})

    def test_get_workflows(self):
        """
        Tests that PredictionWorkflow can be retrieved
        """
        r = self.client.prediction.workflows()

        self.assertEqual(len(r), 4)

        expected_results = (
            ("longview-10", "Longview Pro 10 pack"),
            ("longview-100", "Longview Pro 100 pack"),
            ("longview-3", "Longview Pro 3 pack"),
            ("longview-40", "Longview Pro 40 pack"),
        )

        for result, (expected_id, expected_label) in zip(r, expected_results):
            self.assertEqual(result.id, expected_id)
            self.assertEqual(result.label, expected_label)
