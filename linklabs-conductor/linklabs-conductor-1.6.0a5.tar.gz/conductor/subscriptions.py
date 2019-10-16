

class SubscriptionError(Exception):
    """
    Exception thrown when a subscription reaches a fatal state.
    """
    pass


class ConductorSubscription(object):
    """
    docstring for ConductorSubscription
    """

    def __init__(self, *args, **kwargs):
        super(ConductorSubscription, self).__init__()
        self.subject_name = kwargs.get('subject_name')
        self.subject_id = kwargs.get('subject_id')
        self.callback = kwargs.get('callback')
        self.session = kwargs.get('session')
        self.thread = None
        self.stop_event = threading.Event()
        self.url = '{}/data/uplinkPayload/{}/{}/subscriptions'.format(
                self.client_edge_url, self.subject_name, self.subject_id)
        self.data = {
            'channelRequest': {'type': ''},
            'subscriptionProperties': {'filterProperties': []}
        }

    def start(self):
        """ Start the Subscription Thread. """
        self.thread = threading.Thread(target=self._run)
        self._init_thread()
        self.thread.start()

    def _init_thread(self):
        """ initialize the thread w this function. """
        pass

    def _run(self):
        """ The Subscription Thread. """
        pass

    def stop(self):
        """ Kill the Subscription Thread. """
        pass


class ZeroMQSubscription(ConductorSubscription):
    """
    ZeroMQ subscriptions provide a way for a client to set up a ZeroMQ REQ/REP
    socket pair to stream events. The client should set up a ZeroMQ REP socket
    "server" to listen for events. When the server receives an event, it must
    send a Response json object back to acknowledge receipt of the event.
    If the acknowledgment is not received within 10 seconds, the ZeroMQ socket
    will be assumed to be dead and the subscription will be closed. It is
    recommended that the client send the response right away after receiving
    the event, and not after processing the event in order to ensure the
    channel stays alive.
    """

    def __init__(self, *args, **kwargs):
        super(ZeroMQSubscription, self).__init__(*args, **kwargs)
        self.data['channelRequest']['type'] = 'ZeroMQ2'
        # self.PORT = 2555
        self.PORT = 5001

        self.RSP = {
            "requestId": None,
            "responseStatus": {"OK": None},
            "service": "Subscription",
            "method": "Subscription",
            "responseData": None
        }
        self.CLOSE_RSP = {
            "subscriptionId": None,
            "messageType": None,
            "headers": {
                "matchedEventCount": 0,
                "ClosedReason": None,
                "publishedEventCount": 0
            },
            "event": None
        }

        self.event_count = 0
        self.published_event_count = 0
        self.subscription_id = None
        self.stop_event = threading.Event()
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.ip = requests.get('https://api.ipify.org').text

        # Open the ZeroMQ Server
        self.socket.bind("tcp://*:{}".format(self.PORT))
        self.data['channelRequest']['endpoint'] = self.endpoint

    def _init_thread(self):
        # Send URL Request...
        self.subscription_id = self._post(url, json=self.data)['id']

    def _run(self):
        LOG.info("Opening subscription for %s", self.subject_id)
        while not self.socket.closed and not self.stop_event.is_set():
            events = self.socket.poll(500)

            if not events:
                continue
            print(events)

            for event in events:
                print(event)
                self.event_count += 1
                self.callback(_result_to_uplink_message(event))

                try:
                    self._send_response(event['uuid'])
                except Exception as e:
                    LOG.error(e)
                    self.stop_event.set()

    def _send_response(self, uuid):
        """ """
        response = self.RSP
        response['requestId'] = uuid
        return self.socket.send_json(response)

    def _close_subscription(self, error=None):
        """ """
        response = self.CLOSE_RSP
        response['subscriptionId'] = self.subscription_id
        response['messageType'] = 'UnsubscribeRequest' if not error else "Error"
        response['headers']['matchedEventCount'] = self.event_count
        response['headers']['publishedEventCount'] = self.published_event_count
        response['headers']['ClosedReason'] = "Requested by user" if not error else error
        return self.socket.send_json(response)

    def stop(self):
        self.stop_event.set()

        # Close the socket.
        # LOG.info("Closing subscription for %s", self.subject_id)

        # while self.thread.is_alive():
        #     LOG.info("Thread is alive...")
        #     self.thread.join()

        # LOG.info("Thread is dead!")

        # if not self.socket.closed:
        #     self._close_subscription()
        #     self.socket.unbind("tcp://*:{}".format(self.PORT))

    @property
    def endpoint(self):
        """ The Endpoint is the protocol/address/port of the zmq server. """
        return "tcp://{}:{}".format(self.ip, self.PORT)
        # return "tcp://*:{}".format(self.PORT)
        # return "tcp://localhost:{}".format(self.PORT)


