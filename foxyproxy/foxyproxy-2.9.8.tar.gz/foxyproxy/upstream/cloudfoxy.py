#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
***
Module:
***

#
# Copyright (C) Smart Arcs Ltd registered in the United Kingdom.
# Unauthorized copying of this file, via any medium is strictly prohibited
#
# This file is provided under a license as specified in the "LICENSE" file, which is part
# of this software package.
#
# Written by Smart Arcs <support@smartarchitects.co.uk>, August 2018
from foxyproxy.upstream.base_upstream import BaseUpstream
"""
import logging
import requests
import requests.adapters

from foxyproxy.constant import Constant
from foxyproxy.upstream.base_upstream import BaseUpstream, BaseUpstreamConfig

__author__ = "Petr Svenda, Smart Arcs"
__copyright__ = 'Enigma Bridge Ltd, Smart Arcs Ltd'
__email__ = 'support@smartarchitects.co.uk'
__status__ = 'Beta'


logging.getLogger("urllib3").setLevel(logging.ERROR)
# noinspection PyProtectedMember

logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# ch = logging.StreamHandler()
# ch.setLevel(logging.INFO)
# logger.addHandler(ch)
# fh = logging.FileHandler('foxyproxy.log')
# fh.setLevel(logging.INFO)
# logger.addHandler(fh)


class CloudFoxy(BaseUpstream):
    """
    CloudFoxy server
    """
    def __init__(self, server_config):
        """
        Accepts a configuration of the upstream - using the SignerConfig object below

        :param server_config: an object with configuration parameters of the signing upstream, this object will be
                                stored in the attribute 'server'
        :type server_config: CloudFoxyConfig
        """
        super(CloudFoxy, self).__init__(server_config)

        # max_fds = resource.getrlimit(resource.RLIMIT_NOFILE)[0]  # getrlimit returns a couple
        #
        # self.session = requests.Session()
        # # pool_connections - how many "servers" we will remember - we need only one so 1 is ok
        # # pool_maxsize - how many sockets we keep for each pool_connection
        # adapter = requests.adapters.HTTPAdapter(max_retries=3, pool_connections=1, pool_maxsize=max_fds,
        #                                         pool_block=True)
        # adapter.config['keep_alive'] = False
        # self.session.mount('http://', adapter)
        # self.session.mount('https://', adapter)
        pass

    def getupstreamconnection(self):
        """
        Creates a new upstream session for command requests
        :return:
        """

        connection = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=1, pool_connections=120)
        connection.mount('http://', adapter)
        connection.mount('https://', adapter)

        return connection

    def closeupstreamconnection(self, session):
        """
        As described in the abstract class
        :param session:
        :type session: requests.Session
        :return:
        """

        if session:
            session.close()

    # Function for parsing input request
    # ><reader name>|><cmd ID>:<"APDU" / "RESET" / "ENUM">:<optional hexa string, e.g. "00A4040304">|

    def cmd(self, session, command, terminal, reset=0):
        """
        :type session: requests.Session
        :type command: str|None
        :type terminal: str
        :type reset: int
        """
        if command is None:
            payload = {'reset': str(reset), 'terminal': terminal}
        else:
            payload = {'reset': str(reset), 'terminal': terminal, 'apdu': command}

        response = self._get_request(session, self.server.upstream_cmd, payload)
        if response is None:
            response = [Constant.CMD_READER_NOT_FOUND]
        return response

    def is_down(self, session):
        """
        Test if the upstream responds

        :type session: requests.Session
        :return: time of the upstream server running time
        :rtype int
        """

        response_data = self._get_request(session, self.server.upstream_uptime, None)
        # let's parse the response, which is of 3 lines
        if response_data is None or len(response_data) == 0:
            return True
        else:
            return False

    def downtime(self, session):
        """
        :type session: requests.Session
        :return: time of the upstream server running time
        :rtype int
        """

        response_data = self._get_request(session, self.server.upstream_uptime, None)
        # let's parse the response, which is of 3 lines
        if response_data is None:
            # logging.error("Hello request returns incorrect data None")
            return False  # it's probably down just now
        elif len(response_data) < 3:
            logging.error("Hello request returns incorrect data %s " % '|'.join(response_data))
            return False

        # let's take the second string on 2nd line, convert to integer
        new_uptime = int(response_data[1].split()[1])
        if new_uptime < self.server.up_time:
            self.server.stale = True
        self.server.up_time = new_uptime
        return self.server.stale

    def inventory(self, session):
        """
        Method requests a list of smartcards available at the upstream server

        :type session: requests.Session
        :return:
        """
        return self._get_request(session, self.server.upstream_inventory, None)

    # #########################################################################
    # Private methods
    # #########################################################################
    def _get_request(self, session, cmd, payload):
        response_data = None
        r = None
        # noinspection PyBroadException
        try:
            hw_error = True
            tries = 0
            while hw_error and (tries < 3):
                tries += 1
                hw_error = False
                # logging.debug('Going to send request to CloudFoxy: %s' % payload)
                # 5 min timeout to prevent deadlock
                r = session.get(self.server.upstream_url + cmd,
                                params=payload, headers=self.server.upstream_headers, timeout=300)

                response_status = r.status_code
                if response_status == 200:
                    # process response
                    content = r.content.decode('utf-8').splitlines()
                    # check for HW errors
                    if (len(content) > 0) and (len(content[0]) >= 4):
                        ret_code = content[0][-4:-2]
                        if ret_code in ["C0", "c0"]:
                            hw_error = True
                            continue
                    logging.debug('Response received for %s:  %s' % (payload, ";".join(content)))
                    response_data = []
                    for line in content:
                        if line != 'null' and len(line) > 0:
                            response_data.append(line)
                else:
                    logging.error('Upstream server cloudfoxy has returned an error status code %d to request: %s'
                                  % (response_status, self.server.upstream_url + cmd))

        except requests.ConnectionError:
            logging.error('Problem with connection - check the upstream FoxyRest\'s host and port are correct %s' %
                          self.server.upstream_url)
        except Exception as ex:
            template = "Connection {0} error: an exception of type {1} occurred. Arguments:\n{2!r}"
            logging.error(template.format(self.server.upstream_url + cmd, type(ex).__name__, ex.args))
        finally:
            if r is not None:
                r.close()

        return response_data


class CloudFoxyConfig(BaseUpstreamConfig):
    """
    Configuration for CloudFoxy server
    """
    CLOUD_FOXY_HOST = 'http://localhost:8081'

    def __init__(self, server=None, token='b'):
        super(CloudFoxyConfig, self).__init__()

        if server is None:
            self.upstream_url = CloudFoxyConfig.CLOUD_FOXY_HOST
        else:
            self.upstream_url = server

        logging.info("FoxyProxy will connect to an upstream CloudFoxy at %s" % self.upstream_url)

        #  rest proxy for CloudFoxy hardware platform, use basicj for more info
        self.upstream_cmd = '/api/v1/basic'
        self.upstream_uptime = '/api/v1/hello'
        self.upstream_inventory = '/api/v1/inventory'

        self.upstream_headers = {'X-Auth-Token': token, 'Connection': 'close'}

        # #####################################################################
        # status information

        # up-time of the signer, if it can return the value - detection of resets
        self.up_time = 0
