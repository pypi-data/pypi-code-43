'''
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
'''

import time
import sys
import threading
import cgi

import socket
from http.server import HTTPServer
from trlib import SessionValidator
import trlib.ipconstants as IPConstants

import microserver.glb as glb
from microserver.servers import SSLServer, ThreadingServer, MyHandler


HTTP_VERSION = 'HTTP/1.1'


def getLookupKeyFromRequest(request):
    kpath = ""
    path = ""
    path = request.getURL()
    argsList = []
    keyslist = glb.lookupKey.split("}")

    for keystr in keyslist:
        if keystr == '{PATH':
            kpath = kpath + path
            continue  # do not include path in the list of header fields
        if keystr == '{HOST':
            # assuming we are always gonna get stuff from ATS, which strips the
            # host from url
            kpath = kpath + request.getHeaders()['Host']
            continue
        if keystr == '{URL':
            kpath = kpath + request.getURL()
            continue
        stringk = keystr.replace("{%", "")
        argsList.append(stringk)

    KeyList = []
    for argsL in argsList:
        if len(argsL) > 0:
            val = request.getHeaders()[argsL]
            if val:
                field_val, __ = cgi.parse_header(val)
            else:
                field_val = None
            if field_val is not None:
                KeyList.append(field_val)
    key = "".join(KeyList) + kpath

    return key


def populate_global_replay_dictionary(sessions):
    '''
    Populates the global dictionary of:
    {uuid (string): reponse (Response object)}
    '''
    for session in sessions:
        for txn in session.getTransactionIter():
            # fall back to client request if there's no proxy request
            # server response should always exist though
            sourceReq = txn.getProxyRequest() if txn.getProxyRequest() else txn.getClientRequest()
            glb.replayDict[getLookupKeyFromRequest(
                sourceReq)] = txn.getServerResponse()

    print("size", len(glb.replayDict))
    # from pprint import pprint
    # pprint(glb.replayDict)


class MicroServer:
    @staticmethod
    def serverFromArgs(cls, args):
        pass

    def __init__(self, data_dir, ip='INADDR_LOOPBACK', port=glb.DEFAULT_SERVER_PORT, s_port=glb.DEFAULT_SSL_SERVER_PORT,
                 delay=glb.DEFAULT_SERVER_DELAY, timeout=None, useSSL=False, sslKey='ssl/server.pem', sslCert='ssl/server.crt',
                 clientVerify=False, hooks='', lookupKey='{PATH}', both=False, verbose=True,
                 clientCA="/etc/ssl/certs/ca-certificates.crt"):

        glb.timeDelay = delay
        glb.lookupKey = lookupKey
        glb.verbose = verbose

        s = SessionValidator(data_dir)
        populate_global_replay_dictionary(s.getSessionIter())
        print("Dropped {0} sessions for being malformed".format(
            len(s.getBadSessionList())))

        # start servers
        MyHandler.protocol_version = HTTP_VERSION

        if IPConstants.isIPv6(ip):
            print("Server running on IPv6")
            HTTPServer.address_family = socket.AF_INET6

        self.servers = []
        self.server_threads = []

        if both:
            self.servers.append(SSLServer((IPConstants.getIP(
                ip), s_port), MyHandler, sslKey, sslCert, clientCA, hooks=hooks, clientverify=clientVerify))
            self.servers.append(ThreadingServer(
                (IPConstants.getIP(ip), port), MyHandler, hooks=hooks))
        elif useSSL:
            self.servers.append(SSLServer((IPConstants.getIP(
                ip), s_port), MyHandler, sslKey, sslCert, clientCA, hooks=hooks, clientverify=clientVerify))
        else:
            self.servers.append(ThreadingServer(
                (IPConstants.getIP(ip), port), MyHandler, hooks=hooks))

        for server in self.servers:
            server.timeout = 5
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.daemon = True
            server_thread.name = '{0} {1}'.format(
                server.server_address, 'over TLS' if type(server) == SSLServer else '')
            self.server_threads.append(server_thread)

    def serve_forever(self):
        for t in self.server_threads:
            print("Starting server on port {0}".format(t.name))
            t.start()

        try:
            while 1:
                time.sleep(1)
                sys.stderr.flush()
                sys.stdout.flush()
        except KeyboardInterrupt:
            print("\n=== ^C received, shutting down microservers ===")
            for s in self.servers:
                s.shutdown()

    def addResponseHeader(key, response_header):
        glb.replayDict[key] = response_header
