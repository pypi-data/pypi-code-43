from datetime import datetime

from conductor.event_count import EventCount
from conductor.subject import UplinkSubject, DownlinkSubject

# TODO: Format Documentation.
# TODO: Supply properties for all avalible values.
# TODO: Unittest functionality.
# TODO: See what additional functionality can be added.
# TODO: Don't require net token.


def flatten_status(results):
    """ Flattens the status message's 'properties' dictionary. """
    for status in results:
        status['value']['properties'] = {d['name']: d['value']
                                         for d in status['value']['properties']}
    return results


class Gateway(UplinkSubject, DownlinkSubject, EventCount):
    """ Represents a single Symphony gateway. """
    subject_name = 'node' # TODO: gateway????

    def get_status(self):
        """ Returns the most recent gateway status dictionary """
        url = '{}/data/gatewayStatus/node/{}/mostRecentEvents?f.__prop.type=EQ.status&maxResults=2'.format(self.client_edge_url, self.subject_id)
        return flatten_status(self._get(url)['results'])

    def get_config(self):
        url = '{}/data/gatewayStatus/node/{}/mostRecentEvents?f.__prop.type=EQ.config&maxResults=2'.format(self.client_edge_url, self.subject_id)
        return flatten_status(self._get(url)['results'])

    def get_cell_status(self):
        """ Returns the most recent gateway cellular status dictionary if exists """
        url = '{}/data/gatewayStatus/node/{}/mostRecentEvents?f.__prop.type=EQ.misc_status'.format(self.client_edge_url, self.subject_id)
        return flatten_status(self._get(url)['results'])

    def get_statuses(self, start_time, stop_time):
        """ Returns the status messages for a particular time range. """
        url = '{}/data/gatewayStatus/node/{}/events/{}/{}'.format(self.client_edge_url,
                self.subject_id, format_time(stop_time), format_time(start_time))
        return flatten_status(self._get(url)['results'])

    def send_broadcast(self, payload, time_to_live_s=60.0, port=0, priority=10):
        """
        Sends a broadcast message to all nodes listening to this gateway.

        Returns a `DownlinkMessage` object.
        """
        broadcast_mod_address = '$301$0-0-0-FFFFFFFFF'
        body = {'commandRoutes':
                    {'linkAddresses': [broadcast_mod_address + '!101!' + self.subject_id]}}
        return self._send_message_with_body(body, payload, False, time_to_live_s, port, priority)

    def get_last_data(self, n=1):
        url = '{}/data/uplinkPayload/node/{}/mostRecentEvents?maxResults={}'.format(self.client_edge_url, self.subject_id, n)
        return self._get(url)

    def get_last_status(self, n=2):
        url = self.client_edge_url + '/data/gatewayStatus/node/{}/mostRecentEvents?f.__prop.type=EQ.status&maxResults={}'.format(
            self.subject_id, n)
        return self._get(url)

    def get_last_cell_status(self, n=2):
        """ Returns the most recent gateway cellular status dictionary if exists """
        url = '{}/data/gatewayStatus/node/{}/mostRecentEvents?f.__prop.type='\
                                'EQ.misc_status&maxResults={}'.format(self.client_edge_url, self.subject_id, n)
        return self._get(url)

    def restart_gateway(self):
        payload = '7f' + str(hex(int(datetime.now().timestamp() * 1000)).split('x')[1]).zfill(16)
        body = {"commandRoutes": {"linkAddresses": ["{}!FFD!{}".format(
            self.subject_id, self.subject_id)]}}
        return self._send_message_with_body(body, payload, True, 60.0, 0, 10)


