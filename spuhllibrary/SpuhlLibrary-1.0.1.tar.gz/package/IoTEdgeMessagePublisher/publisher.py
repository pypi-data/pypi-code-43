# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import json
# pylint: disable=E0611
from iothub_client import IoTHubModuleClient, IoTHubTransportProvider, IoTHubMessage

# messageTimeout - the maximum time in milliseconds until a message times out.
# The timeout period starts at IoTHubModuleClient.send_event_async.
# By default, messages do not expire.
MESSAGE_TIMEOUT = 10000

# global counters
SEND_CALLBACKS = 0

# Choose HTTP, AMQP or MQTT as transport protocol.  Currently only MQTT is supported.
PROTOCOL = IoTHubTransportProvider.MQTT


def send_confirmation_callback(message, result, user_context):
    """
    Callback received when the forwarded message has been processed.
    """
    global SEND_CALLBACKS
    SEND_CALLBACKS += 1
    map_properties = message.properties()
    key_value_pair = map_properties.get_internals()
    print("Confirmation[%d] received for message with result = %s" % (user_context, result))
    print("    Properties: %s" % key_value_pair)
    print("    Total calls confirmed: %d" % SEND_CALLBACKS)


class HubManager(object):

    def __init__(self):
        self.client_protocol = PROTOCOL
        self.client = IoTHubModuleClient()
        self.client.create_from_environment(PROTOCOL)

        # set the time until a message times out
        self.client.set_option("messageTimeout", MESSAGE_TIMEOUT)

    def forward_event_to_output(self, output_queue_name, event, send_context):
        """
        Forwards the message received onto the next stage in the process.
        """
        self.client.send_event_async(output_queue_name, event, send_confirmation_callback, send_context)


class Publisher:

    def __init__(self):
        self.hub_manager = HubManager()

    def create_message(self, values) -> IoTHubMessage:
        """
        Creates the message with the values to forward to the routing.
        """
        return IoTHubMessage(bytearray(json.dumps(values), 'utf-8'))

    def send_message(self, output_queue_name, message):
        """
        Forwards the message to the output.
        """
        self.hub_manager.forward_event_to_output(output_queue_name, message, 0)
