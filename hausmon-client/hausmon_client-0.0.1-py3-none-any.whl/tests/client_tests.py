import unittest as test

import os

from hausmon_client.client import HausMonClient

# The URL and token to use for live API testing.
TEST_API_URL = os.getenv('HAUSMON_TEST_API_URL', 'http://localhost:8000/api')
TEST_API_TOKEN = os.getenv('HAUSMON_TEST_API_TOKEN', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')


def test_server_available() -> bool:
    """Detects if a test server is available at TEST_API_URL."""
    import requests
    try:
        response = requests.get(TEST_API_URL)
    except requests.ConnectionError as e:
        return False
    return True


@test.skipIf(not test_server_available(), "Test server not available, skipping direct tests.")
class LiveClientTests(test.TestCase):
    """Test the API client, using calls to a test API. The test API should have the live test fixture created."""
    def setUp(self) -> None:
        """Set up the client to use for all the tests in this class."""
        self.client = HausMonClient(TEST_API_URL, TEST_API_TOKEN)

    def test_devices_can_be_listed(self):
        """Test that devices can be listed"""
        devices = self.client.list_devices()
        self.assertEqual(3, len(devices), "Expected three devices")
        for device in devices:
            self.assertIn(device['name'], ['device_A', 'device_B', 'device_C'])
            if device['name'] == 'device_B':
                self.assertIsNone(device['heartbeat_id'])
            else:
                self.assertIsNotNone(device['heartbeat_id'])

    def test_get_device(self):
        """Test that a specific device can be retrieved."""
        device = self.client.get_device('device_A')
        self.assertIsNotNone(device, "Expected device_A to be returned")

    def test_heartbeat_spec_is_returned(self) -> None:
        """Test that a full heartbeat spec is returned, given the device name."""
        heartbeat_spec = self.client.get_heartbeat('device_A')
        self.assertIsNotNone(heartbeat_spec, "Expected a heartbeat specification.")
        self.assertEqual(1000, heartbeat_spec['period_seconds'])
        heartbeat_spec = self.client.get_heartbeat('device_B')
        self.assertIsNone(heartbeat_spec, "device_B has no heartbeat")

    def test_heartbeat_beat_resets_timer(self) -> None:
        """Test that calling the 'beat' function resets the timer."""
        heartbeat_at_start = self.client.get_heartbeat('device_A')
        self.client.send_heartbeat(heartbeat_at_start.id)
        heartbeat_at_end = self.client.get_heartbeat('device_A')
        self.assertGreater(
            heartbeat_at_end.timeout_on,
            heartbeat_at_start.timeout_on,
            "Timeout time at end should be greater than at start"
        )
