# TODO: Format Documenation.
# TODO: See what additional functionality can be added.
# TODO: Unittests

from conductor.subject import UplinkSubject, DownlinkSubject


class AppToken(UplinkSubject, DownlinkSubject):
    """ Represents an application designated by an app token for an account. """
    subject_name = 'applicationToken'

    def send_message(self, payload, gateway_addr=None, acked=False,
                     time_to_live_s=60.0, port=0, priority=10):
        """
        Sends a multicast message to all nodes registered to this app token.

        The 'acked' parameter is there to have the same function signature as other 'send_message'
        methods, but it must be False.
        """
        if acked:
            raise ValueError("Multicast messages cannot be acknowledged")

        body = {}
        if gateway_addr:
            body['commandRoutes'] = {
                'linkAddresses': [self._to_node_address() + '!101!' + gateway_addr]}
        else:
            body['commandTargets'] = {'targetAppToken': self.subject_id}

        return self._send_message_with_body(body, payload, False, time_to_live_s, port, priority)

    # We need to override query_downlink because we need to use the node address form
    def query_downlink(self, *args, **kwargs):
        """ Queries Conductor for all downlink sent to this subject. """
        temp = deepcopy(self)
        temp.subject_name = 'node'
        temp.subject_id = self._to_node_address()
        return super(AppToken, temp).query_downlink(*args, **kwargs)

    def _to_node_address(self):
        """
        Converts an app token to the node address format that Conductor understands.

        Example
        -------
        : app_token
        AppToken(1bcda4a2e8c1af83d330)
        : app_token._to_node_address()
        '$401$1bcda4a2-e8c1af83-0-00000d330'
        """
        app_token = str(self.subject_id)
        return '$401${}-{}-{}-{:0>9}'.format(app_token[:8], app_token[8:16], 0, app_token[16:])


# TODO: Add functionality.
# TODO: Format Documenation.
class NetToken(UplinkSubject):
    """ Represents a network designated by a network token for an account. """
    subject_name = 'networkToken'


