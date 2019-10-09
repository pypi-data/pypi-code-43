"""Common verify functions for routing"""

# Python
import re
import logging
from prettytable import PrettyTable

# pyATS
from pyats.utils.objects import find, R

# Genie
from genie.utils.timeout import Timeout
from genie.libs.sdk.libs.utils.normalize import GroupKeys
from genie.metaparser.util.exceptions import SchemaEmptyParserError

# BGP
from genie.libs.sdk.apis.iosxe.bgp.get import (
    get_ip_bgp_summary,
    get_bgp_route_from_neighbors,
    get_bgp_neighbors_advertised_routes,
)

# ROUTING
from genie.libs.sdk.apis.iosxe.routing.get import get_routing_routes
from genie.libs.sdk.apis.iosxe.routing.get import (
    get_routing_repair_path_information,
)

log = logging.getLogger(__name__)


def verify_ip_cef_nexthop_label(device, ip, table=None, expected_label=None, vrf=None,
                                max_time=30, check_interval=10):
    """ Verify nexthop does (not) have expected label

        Args:
            device (`obj`): Device object
            ip (`str`): IP address
            expected_label (`str`): Expected label. None if no label expected
            vrf (`str`): Not used on JuniperOS
            table (`str`): Route table
            max_time (`int`): Max time, default: 30
            check_interval (`int`): Check interval, default: 10
        Returns:
            result (`bool`): Verified result
        Raises:
            N/A
    """

    timeout = Timeout(max_time, check_interval)
    while timeout.iterate():
        try:
            if table:
                out = device.parse('show route table {table} {ip}'.format(table=table, ip=ip))
            else:
                out = device.parse('show route {ip}'.format(ip=ip))
        except SchemaEmptyParserError:
            log.info('Failed to parse. Device output might contain nothing.')
            timeout.sleep()
            continue

        reqs = R(['table_name',
                  table if table else '(.*)',
                  'routes',
                  '(?P<route>){ip}.*'.format(ip=ip),
                  'next_hop',
                  'next_hop_list',
                  '(.*)',
                  'mpls_label',
                  '(.*)'])

        found = find([out], reqs, filter_=False, all_keys=True)

        if expected_label and found and expected_label in found[0][0]:
            log.info('Excepted nexthop label found: "{expected_label}"'
                     .format(expected_label=found[0][0]))
            return True

        elif not expected_label and not found:
            log.info('Expected to find no nexthop label and found none')
            return True

        elif expected_label and found and expected_label not in found[0][0]:
            log.info('Expected nexthop label "{expected_label}" was not found. '
                     'The found nexthop label is "{found}"'
                     .format(expected_label=expected_label, found=found[0][0]))
            timeout.sleep()
            continue

        elif expected_label and not found:
            log.info('Expected a nexthop label but none was found')
            timeout.sleep()
            continue

        elif not expected_label and found:
            log.info('Expected to find no nexthop label but found "{found}"'
                     .format(found=found[0][0]))
            timeout.sleep()
            continue

        # Incase a False case was missed. All True cases exist.
        timeout.sleep()

    return False
