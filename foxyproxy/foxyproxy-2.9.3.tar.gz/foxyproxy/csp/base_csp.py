#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
***
Module: base_csp - an abstract class for new CSPs
***
#
# Copyright (C) Smart Arcs Ltd registered in the United Kingdom.
# Unauthorized copying of this file, via any medium is strictly prohibited
#
# This file is provided under a license as specified in the "LICENSE" file, which is part
# of this software package.
#
# Written by Smart Arcs <support@smartarchitects.co.uk>, March 2019
"""
import base64
import datetime
import logging
import os
import platform
import socket

import traceback
from typing import Dict, Union
from multiprocessing import Queue
from threading import Lock

from foxyproxy.constant import Constant
from foxyproxy.upstream import BaseUpstream

__author__ = "Smart Arcs"
__copyright__ = 'Smart Arcs Ltd'
__email__ = 'support@smartarchitects.co.uk'
__status__ = 'Development'

logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# ch = logging.StreamHandler()
# ch.setLevel(logging.INFO)
# logger.addHandler(ch)


class BaseCryptoService(object):
    """
    The abastract class for crypto service providers - definitions of functions working with smartcards.
    """
    server = None  # type: BaseUpstream

    def __init__(self, server):
        """
        The constructor shows a set of suggested data structures
        :param server: this is a configuration of the upstream server, or process this proxy connects to
        :type server: BaseUpstream
        """

        # connection details for the signing server
        self.server = server
        self.storage = BaseCryptoServiceStorage()
        self.process_queue = Queue()  # multiprocessing queue to sync data changes from processes
        self.initialized = False

        # we also create a user configuration folder
        # first we read certificates from the user's home folder
        home_dir = os.path.expanduser("~")
        config_dir = os.path.join(home_dir, r'.cloudfoxy')
        if platform.system() == 'Windows':
            self.user_dir = os.path.join(home_dir, r'CloudFoxy')
        elif platform.system() == 'Darwin':
            self.user_dir = os.path.join(home_dir, r'CloudFoxy')
        else:
            self.user_dir = os.path.join(home_dir, r'CloudFoxy')

        self.cert_dir = os.path.join(config_dir, r'certs')
        self.token_dir = os.path.join(config_dir, r'tokens')
        self.inbox_dir = os.path.join(config_dir, r'inbox')
        self.outbox_dir = os.path.join(config_dir, r'outbox')
        if not os.path.exists(self.cert_dir):
            os.makedirs(self.cert_dir)
        elif not os.path.isdir(self.cert_dir):
            logging.error("We can't create configuration folder as there's a file with the same name: %s"
                          % self.cert_dir)
            exit(4)
        if not os.path.exists(self.token_dir):
            os.makedirs(self.token_dir)
        elif not os.path.isdir(self.token_dir):
            logging.error("We can't create configuration folder as there's a file with the same name: %s"
                          % self.cert_dir)
            exit(4)
        if not os.path.exists(self.inbox_dir):
            os.makedirs(self.inbox_dir)
        elif not os.path.isdir(self.inbox_dir):
            logging.error("We can't create configuration folder as there's a file with the same name: %s"
                          % self.inbox_dir)
            exit(4)
        if not os.path.exists(self.outbox_dir):
            os.makedirs(self.outbox_dir)
        elif not os.path.isdir(self.outbox_dir):
            logging.error("We can't create configuration folder as there's a file with the same name: %s"
                          % self.outbox_dir)
            exit(4)
        if not os.path.exists(self.user_dir):
            os.makedirs(self.user_dir)
        elif not os.path.isdir(self.user_dir):
            logging.error("We can't create configuration folder as there's a file with the same name: %s"
                          % self.user_dir)
            exit(4)

    # def process_updates(self):
    #     """
    #     Checks for configuration data updates in multiprocessing queue and updates the master copy
    #     """
    #     while not self.process_queue.empty():
    #         item = self.process_queue.get_nowait()
    #         try:
    #             if item:
    #                 if item['type'] == 'pin':
    #                     self.storage.cert_names[item['alias']].pin = item['data']
    #                 else:
    #                     logging.error("Missing processing of items in multiprocessin queue: %s" % item['type'])
    #         except Exception as ex:
    #             logging.error("Error in process_updates %s" % str(ex))
    #     pass

    def init(self, session, config=None):
        """
        Initialization function, which will be called periodically by a scheduler. It does any necessary
        initialization of the csp signing provider as well as reacts to changes.
        :param session: open TCP/HTTP connection if required
        :type session: requests.Session|None
        :param config: configuration data, as appropriate for a given csp provider
        :return:
        """
        raise NotImplementedError("Please Implement the method 'init'")

    def sign(self, session, alias, fingerprint, password=None, hash_alg=None, sign_alg=None):
        """
        The actual signing function. It needs two parameters: fingerprint, and alias. The alias is the name
        to look-up a key, fingerprint is a hex-encoding fingerprint. It also accepts 2 optional parameters
        :param session: upstream server connection if TCP/HTTP
        :type session: requests.Session
        :param alias: an identification of the key - e.g., a name on the relevant certificate.
        :type alias: str
        :param fingerprint: a hex-encoded data that will be signed,
        :type fingerprint: str
        :param password: an optional password needed to obtain access to the signing key
        :type password: str
        :param sign_alg: identifier of the signing algorithm - if not specified, it shall be RSA
        :type sign_alg: int
        :param hash_alg: identifier of the hash algorithm used to create the fingerprint; if not specified, it will
                         be one of SHA functions derived from the length of the fingerprint
        :type hash_alg: int
        :return: the signature of the 'fingerprint' using the sign_alg and a key identified by the alias
        :rtype: str the signature in hex encoding - each 8bits are encoded as two characters of 0-9a-f
        """

        raise NotImplementedError("Please Implement the method 'sign'")

    def aliases(self):
        """
        This function provides a list of names to identify signing keys/certificates. It doesn't take any parameters
        :return: A list of key/certificate aliases, e.g., names of persons whose keys are available
        ":rtype: list of str
        """
        raise NotImplementedError("Please Implement the method 'aliases'")

    def chain(self, alias, sign_alg=0):
        """
        This function returns a complete chain of certificates for a given alias and an optional sign_alg, e.g., RSA.
        The list should not contain the "root" certificate. The order is from the certificate signed by a root
        certificate. The last certificate is the certificate issued for the "alias".
        :param alias: An identifier that can be used to identify the required certificate chain.
        :type alias: str
        :param sign_alg is an optional parameter, which can help identify the correct set of certificates if a given
                        alias has keys for more than one signing algorithm
        :type sign_alg: int
        :return: a list of hex-encoded certificates in the correct order - parent certificate precedes the certificate
                 it signed
        :rtype: list of string
        """
        raise NotImplementedError("Please Implement the method 'chain'")

    def reset(self, session, token):
        """
        The method adds an ability to reset the token to return it to an initial state, if it's required
        :param session: upstream server connection if TCP/HTTP
        :type session: requests.Session|None
        :param token:
        :type token: string
        :return:
        """

        raise NotImplementedError("Please Implement the method 'reset'")

    def apdu(self, session, token, command):
        """
        Execute any of the atomic operations available from the token
        :param session: upstream server connection if TCP/HTTP
        :type session: requests.Session|None
        :param token: identification of the token
        :type token: str
        :param command: a complete command, in hex-encoding
        :type command: str
        :return: a hex-encoded response from the token
        :rtype str:
        """
        raise NotImplementedError("Please Implement the method 'reset'")

    # #########################################################################
    # the remaining methods are already implemented
    # #########################################################################

    def getupstreamconnection(self):
        """
        Returns a connection to the upstream server, primarily used for TCP / HTTP based servers
        :return: a new connection / session
        :rtype requests.Session|None
        """

        if self.server:
            return self.server.getupstreamconnection()
        else:
            return None

    def closesession(self, session):
        """
        Close the connection session, if needed
        :param session:
        :return:
        """

        if self.server:
            self.server.closeupstreamconnection(session)

    @classmethod
    def check_response(cls, response, reader, message, index=0, error=1):
        """

        :param response: response received from the upstream signer
        :param reader: name of the response source
        :param message: text message that should be logged when there's an error
        :param index: the line of the response that should be processed
        :param error: if 1, logging will report errors, otherwise it's just a debug level
        """
        response_data = None

        if response is None:
            if error:
                logging.error("%s: %s %s - no response" % (cls.__name__, message, reader))
            else:
                logging.debug("%s: %s %s - no response" % (cls.__name__, message, reader))
            response_data = Constant.CMD_UPSTREAM_ERROR
        else:
            if not isinstance(response, list):
                response = [response]

            # response processing
            if len(response) <= index:  # index=0 -> we need at least len() = 1
                if error:
                    logging.error("%s: %s, reader: %s - response array too small as requested %d (%s)"
                                  % (cls.__name__, message, reader, index, response))
                else:
                    logging.debug("%s: %s, reader: %s - response array too small as requested %d (%s)"
                                  % (cls.__name__, message, reader, index, response))

                response_data = Constant.CMD_INTERNAL_ERROR
            elif len(response[index]) < 4:
                if error:
                    logging.error("%s: %s, reader: %s - code: %s"
                                  % (cls.__name__, message, reader, response[index]))
                else:
                    logging.debug("%s: %s, reader: %s - response array too small as requested %d (%s)"
                                  % (cls.__name__, message, reader, index, response))
                response_data = Constant.CMD_UPSTREAM_ERROR
            elif response[index][-4:] != "9000":
                if error:
                    logging.error("%s: %s, reader: %s - code: %s"
                                  % (cls.__name__, message, reader, response[index]))
                else:
                    logging.debug("%s: %s, reader: %s - code: %s"
                                  % (cls.__name__, message, reader, response[index]))
                response_data = response[index][-4:]

        if response_data:
            response_data = response_data.upper()

        return response_data

    @staticmethod
    def unix_time(dt):
        """
        Get a unix_time regardless of the timezone
        :param dt:
        :return:
        """
        if dt is None:
            return None
        cur = datetime.datetime.utcfromtimestamp(0)
        if dt.tzinfo is not None:
            cur.replace(tzinfo=dt.tzinfo)
        else:
            cur.replace(tzinfo=None)
        # noinspection PyBroadException
        try:
            return (dt - cur).total_seconds()
        except Exception:
            pass

    def downtime(self, session):
        """
        Returns true if the terminal / server of terminals has been restarted
        :type session: requests.Session
        :return:
        """
        return self.server.downtime(session)

    def tokens(self, regex_name, maximum=0):
        """
        No parameters, returns a list of readers with valid certificates
        :return:
        """
        _maximum = 0
        if regex_name is None:
            regex_name = ""

        if not isinstance(maximum, int):
            # noinspection PyBroadException
            try:
                _maximum = int(maximum)
            except Exception:
                _maximum = 0
        elif maximum >= 0:
            _maximum = maximum

        if ((_maximum > self.storage.max_enum_readers) or (_maximum == 0)) and (self.storage.max_enum_readers > 0):
            _maximum = self.storage.max_enum_readers

        readers = []
        # noinspection PyBroadException
        try:
            counter = 0
            for one_name in self.storage.cert_names:  # type: TokenRecord
                name = BaseCryptoService.encode_cf_reader(one_name.reader)
                user = one_name.name
                priority = one_name.priority

                # no regex (it's empty string), or it is "*" -> all, or it matches the reader name or it matches
                if (len(regex_name) == 0) or (regex_name == '*') or (regex_name in name) \
                        or (regex_name in user):
                    if (_maximum > 0) and (counter >= _maximum):
                        already_in = None
                        for already_in in readers:
                            if self.storage.cert_names[already_in].priority < priority:
                                break
                        if already_in and (self.storage.cert_names[already_in].priority < priority):
                            readers.remove(already_in)
                            readers.append(base64.b64encode(name.encode('utf-8')).decode('ascii'))
                    else:
                        readers.append(base64.b64encode(name.encode('utf-8')).decode('ascii'))
                        counter += 1
                    break
        except Exception as ex:
            logging.error("Exception in 'tokens', case: %s, traceback %s" % (str(ex), traceback.format_exc()))
        finally:
            return readers

    # noinspection PyUnusedLocal
    def get_readers(self, regex_name, source="", subset="0", do_encode=True):
        """
        No parameters, returns a list of readers - all readers, regardless of whether they have a valid certificates
        :param regex_name it can filter readers by their name
        :type regex_name: str
        :param source - name of the library that requested the list - this way we can adjust logic for Win/Linux/App
        :type source: str
        :param subset -  "0" no filtering, "1" no filtering, replace reader name with certifitate name when there's one
                         "1" only with valid tokens "2" only without tokens (unitialized certificates)
        :type subset: str
        :param do_encode
        :return:
        """

        if source is None:
            source = "unknown"

        source = source.strip().lower()

        if not isinstance(subset, int):
            # noinspection PyBroadException
            try:
                subset = int(subset.strip())
            except Exception:
                subset = 0

        readers = []
        # noinspection PyBroadException
        try:
            counter = 0

            # let's sort the dict certificates reversed and get first self.storage.max_enum_readers
            ordered = sorted(self.storage.certificates.items(), key=lambda x: x[1].priority, reverse=True)

            if self.storage.max_enum_readers > 0:
                ordered = ordered[:self.storage.max_enum_readers]
            else:
                ordered = ordered

            for _reader, _content in ordered:  # type: str, ReaderRecord
                # and add to the list
                if _content.subject is None:
                    value = BaseCryptoService.encode_cf_reader(_reader)
                else:
                    value = BaseCryptoService.encode_cf_reader(_reader)
                    # value = _content.subject
                logging.debug("Card reader enumerated: reader={0} - as {1}, option={2}".format(_reader, value, subset))

                if do_encode:
                    # noinspection PyArgumentEqualDefault
                    readers.append(base64.b64encode(value.encode('utf-8')).decode('ascii'))
                else:
                    readers.append(value)

        except Exception as ex:
            logging.error("Exception in get_readers, reason: {0}, {1}".format(str(ex), traceback.format_exc()))
        finally:

            return readers

    def prioritize(self, regex_name, limit=5):
        """
        Make one more terminals show at the top of a list of terminals  returned by ENUM. If limit=0, no changes will
        be made
        :param regex_name:
        :param limit:
        :return:
        """

        if limit == 0:
            readers = self.get_readers("*", do_encode=False)
            return readers, {}, self.storage.last_priority
            pass

        else:
            self.storage.max_enum_readers = limit
            priorities = {}
            updated_names = []
            if (regex_name is not None) and (len(regex_name) > 0):
                for key, value in self.storage.certificates.items():  # type: str, ReaderRecord
                    terminal_name = BaseCryptoService.encode_cf_reader(key)
                    user = value.subject
                    if user is None:
                        user = ""
                    if (len(regex_name) > 0) and terminal_name.endswith(regex_name):
                        self.storage.last_priority += 1
                        value.priority = self.storage.last_priority
                        priorities[key] = value.priority
                        if len(user) > 0:
                            updated_names.insert(0, "%s (%s)" % (terminal_name, user))
                        else:
                            updated_names.insert(0,  "%s (%s)" % (terminal_name, "---"))

                # self.storage.cert_names.sort(key=BaseCryptoService._cert_names_sort, reverse=True)

            return_list = updated_names
            # return_list = []
            # count = 0
            # if self.storage.cert_names is not None:
            #     for one_name in self.storage.cert_names:  # type: TokenRecord
            #         return_list.append("%s (%s)" %
            #                            (BaseCryptoService.encode_cf_reader(one_name.reader), one_name.short_name))
            #         count += 1
            #         if (count > limit) and (limit > 1):
            #             break

            return return_list, priorities, self.storage.last_priority

    @staticmethod
    def _cert_names_sort(e):
        """
        Sorting parameter for certificates
        :param e:
        :type e: TokenRecord
        :return:
        """
        return e.priority

    def get_certs(self, reader_id):
        """
        Returns a string of certificates in the correct format for FoxyProxy
        :param reader_id: e.g., /192.168.42.10@1
        :return:
        """
        str_certs = ""
        if reader_id in self.storage.certificates.keys():
            #                 'subject': "",
            #                 'cert': None,
            #                 'chain': None,
            #                 'token': None
            str_certs += self.storage.certificates.get(reader_id).cert.decode('ascii')
            for ca_cert in self.storage.certificates.get(reader_id).chain:  # type: CertificateRecord
                str_certs += ":" + ca_cert.cert.decode('ascii')

        return str_certs

    def get_token(self, subject):
        """
        Accepts names of certificate owners and returns a list of readers that have certs with this string in cert names
        :param subject: a substring of a name from a certificate
        :return:
        :rtype [TokenRecord]
        """
        token = []
        tries = 0
        patterns = []
        for one_name in self.storage.cert_names:  # type: TokenRecord
            tries += 1
            if subject in one_name.name:
                token.append(one_name)
            if len(token) < 1:
                patterns.append(one_name.name)
        logging.debug("get_token() tested %d names for %s and found %d readers" % (tries, subject, len(token)))
        if len(token) < 1:
            for _x in patterns:
                logging.debug("Pattern tested: %s" % _x)
        return token

    @staticmethod
    def encode_cf_reader(name):
        """
        Adds decoration to CloudFoxy reader names
        :type name: str
        """
        if name[0] == '/' and name.find('@') > 1:
            name = "Foxy NET " + name[1:]  # also remove the '/' at the beginning
            name = name.replace('@', '-')
        else:
            name = "Foxy USB " + name
        return name

    @staticmethod
    def decode_cf_reader(name_in):
        """
        Removes a decoration from CloudFoxy reader names.
        :type name_in: str
        """

        if name_in is None:
            logging.error("decode_cf_reader called with reader set to None")
            return ""
        
        # let's try to do base64 decode first
        # noinspection PyBroadException
        try:
            name_in = base64.b64decode(name_in).decode()
        except Exception:
            pass

        prefix_net = "Foxy NET"
        prefix_usb = "Foxy USB"
        name = name_in.strip()
        if name.find(prefix_net) == 0:  # network name - strip prefix, add '/' and replace '-' with '@'
            name = '/' + name[len(prefix_net):].strip()
            name = name.replace('-', '@')
        elif name.find(prefix_usb) == 0:  # local/usb name - strip prefix only
            name = name[len(prefix_usb):].strip()

        logging.debug(u'Updating token name "{0}" to "{1}"'.format(name_in, name))

        return name.strip()


class BaseCryptoServiceStorage(object):
    """
    Storage of smartcard data for the base class.
    """
    cert_names = None  # type: [TokenRecord]

    def __init__(self):
        """
        # this is a hash table of certificates we need to initialize now
        # the key is a name of the token, values are {'cert': <certificate}, 'chain': []}
        """
        self.certificates = {}  # type: Dict[ReaderRecord]

        # this will contain a mapping from names to tokens {name:<>, reader:<>}
        self.cert_names = []  # type: [TokenRecord]

        # for future use - a hash map - list of CA certs on a token
        # possibly for appending to signatures if tokens do not have certificates
        self.card_cas = {}

        # # a list of all readers with smartcards
        # self.card_readers = []

        # this will increment with each request to show a particular terminal in ENUM command
        # self.last_priority = [0]
        self.last_priority = 0
        # create a dictionary for card locks - regardless of whether multiprocessing or not
        self.card_locks = {}
        # when there is a limit on the number of readers that can be sent to the client for enumeration, this is last id
        self.last_enum_reader = 0
        # maximum readers to return - 0 = no limit
        self.max_enum_readers = 2

        pass

    def reset(self):
        """
        Reset a smart-card.
        """
        raise NotImplementedError("Please Implement the method 'reset' in your CSP module")

    def initialize(self):
        """
        Initialize the storage = forget all the information about smartcards so we can re-read it.
        """
        self.certificates.clear()  # type: Dict[str, ReaderRecord]
        self.cert_names[:] = []
        self.card_cas.clear()
        self.last_priority = 0
        self.last_enum_reader = 0


class ReaderRecord(object):
    """
    A base record for storage.certificates
    """
    def __init__(self):
        self.cert = None
        self.chain = None
        self.subject = None
        self.token = None
        self.key = None
        self.last_enum = 0
        self.priority = 0


class CertificateRecord(object):
    """
    A base record for storage.card_cas
    """
    name = None
    issuer = None
    cert = None


class TokenRecord(object):
    """
    Operational date for the reader / card
    """
    def __init__(self):
        self.name = None
        self.short_name = None
        self.reader = None
        self.pin = None
        self.priority = 0
        self.file_id = 0


class ClientWork(object):
    """
    A structure for submitting a new request from downstream client
    """
    CMD_PROCESS = 1
    CMD_KILL = 2
    CMD_SELECT_TERM = 3

    def __init__(self):
        self.protocol = 'tcp'
        self.connection = None  # type: Union(socket.socket,None)
        self.command = None  # it can be 1 = work or 2 = die
        self.req_commands = None
        self.req_reader = None
        self.req_password = None
        self.reader_name = None
        self.real_reader_name = None
        # True -> use the rest queue
        self.alt_result_queue = False


class ClientResult(object):
    """
    An object returned by ClientThread at the end of processing
    """
    TYPE_PIN = 1
    TYPE_LAST_READER = 2
    TYPE_ACK = 3
    TYPE_PRIORITY = 4

    def __init__(self):
        self.reader = None
        self.type = 0
        self.pin = None
        self.file_id = None
        self.last_enum_id = None
        self.process_id = None
        self.last_priority = 0
        self.max_readers = 2
        self.priority_dict = {}  # to update priorities in the master copy

        self.response = []  # a response back (TCP&REST)
        self.response_sent = False  # TCP -> True, HTTP -> False
        self.connection = None  # connection to be used when response_set is False


class WorkerMap(object):
    """
    A dictionary of workers and a map from names to the worker dictionary keys
    """
    CAPACITY = 120
    instance_lock = Lock()
    workers = {}
    workers_running = {}
    workers_running_lock = {}  # type: Dict[int,Lock]
    map = {}
    map_all = {}
    last_mapped = 0
    result_queue = None


class WorkerRecord(object):
    """
    A simple class to capture properties stored in the dictionary of workers / Client Thread
    """

    def __init__(self):
        self.worker = None
        self.work = None  # type: Queue, None
        self.result = None   # type: Queue, None
        self.ack = None  # type: Queue, None
        self.rest = None  # type: Queue, None
        self.internal = None  # type: Queue, None
