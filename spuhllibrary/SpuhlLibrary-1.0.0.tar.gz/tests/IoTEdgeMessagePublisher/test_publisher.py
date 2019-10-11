import unittest
from unittest.mock import MagicMock, patch
from package.IoTEdgeMessagePublisher.publisher import Publisher, HubManager, send_confirmation_callback


class PublisherTest(unittest.TestCase):

    @patch('package.IoTEdgeMessagePublisher.publisher.HubManager')
    def setUp(self, hub_manager_mock):
        self.publisher = Publisher()
        self.hub_manager_mock = hub_manager_mock

    def test_send_message(self):
        iot_hub_message_mock = MagicMock()
        self.publisher.send_message("anyOutputQueue", iot_hub_message_mock)
        self.hub_manager_mock().forward_event_to_output.assert_called_with("anyOutputQueue", iot_hub_message_mock, 0)

    @patch('package.IoTEdgeMessagePublisher.publisher.IoTHubMessage')
    def test_create_message(self, iot_hub_message_mock):
        self.publisher.create_message({"temperature": 20})
        iot_hub_message_mock.assert_called_once()


class HubManagerTest(unittest.TestCase):

    @patch('package.IoTEdgeMessagePublisher.publisher.IoTHubModuleClient')
    @patch('package.IoTEdgeMessagePublisher.publisher.PROTOCOL', "MQTT")
    def setUp(self, client_mock):
        self.hub_manager = HubManager()
        self.client_mock = client_mock

    def test_init(self):
        message_timeout = 10000
        self.client_mock.assert_called_once()
        self.client_mock().create_from_environment.assert_called_with("MQTT")
        self.client_mock().set_option.assert_called_with("messageTimeout", message_timeout)

    @patch('package.IoTEdgeMessagePublisher.publisher.send_confirmation_callback')
    def test_forward_event_to_output(self, send_confirmation_callback_mock):
        io_t_hub_message = MagicMock()
        self.hub_manager.forward_event_to_output("outputQueue", io_t_hub_message, 0)
        self.client_mock().send_event_async.assert_called_with("outputQueue", io_t_hub_message,
                                                               send_confirmation_callback_mock, 0)

    def test_send_confirmation_callback(self):
        iot_hub_message_mock = MagicMock()
        result_mock = MagicMock()
        user_context_mock = MagicMock()
        properties_mock = MagicMock()
        iot_hub_message_mock.properties.return_value = properties_mock
        send_confirmation_callback(iot_hub_message_mock, result_mock, user_context_mock)
        iot_hub_message_mock.properties.assert_called_once()
        properties_mock.get_internals.assert_called_once()
