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

import argparse
import os

import microserver
import microserver.microserver
import microserver.glb as glb
import signal

def _path(exists, arg):
    path = os.path.abspath(arg)
    if not os.path.exists(path) and exists:
        msg = '"{0}" is not a valid path'.format(path)
        raise argparse.ArgumentTypeError(msg)
    return path


def main():
    if signal.SIG_IGN == signal.getsignal(signal.SIGINT):
        print("Setting default_int_handler for SIGINT signal")
        signal.signal(signal.SIGINT, signal.default_int_handler)
    parser = argparse.ArgumentParser()

    parser.add_argument("--data-dir", "-d",
                        type=lambda x: _path(True, x),
                        required=True,
                        help="Directory with data file"
                        )

    parser.add_argument("--ip_address", "-ip",
                        type=str,
                        default='INADDR_LOOPBACK',
                        help="IP address of the interface to serve on"
                        )

    parser.add_argument("--port", "-p",
                        type=int,
                        default=glb.DEFAULT_SERVER_PORT,
                        help="Port to use")

    parser.add_argument("--delay", "-dy",
                        type=float,
                        default=glb.DEFAULT_SERVER_DELAY,
                        help="Response delay")

    parser.add_argument("--timeout", "-t",
                        type=float,
                        default=None,
                        help="socket time out in seconds")

    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s {0}'.format(microserver.__version__))

    parser.add_argument("--ssl", "-ssl",
                        action='store_true',
                        help="Use SSLServer")

    parser.add_argument("--key", "-k",
                        type=str,
                        default="server.pem",
                        help="key for ssl connnection")

    parser.add_argument("--cert", "-cert",
                        type=str,
                        default="server.crt",
                        help="certificate")

    parser.add_argument("--clientverify", "-cverify",
                        action='store_true',
                        default=False,
                        help="verify client cert")

    parser.add_argument("--clientCA",
                        type=str,
                        default='/etc/ssl/certs/ca-certificates.crt',
                        help="CA for client certificates")

    parser.add_argument("--load",
                        dest='load',
                        type=str,
                        default='',
                        help="A file which will install observers on hooks")

    parser.add_argument("--lookupkey",
                        type=str,
                        default="{PATH}",
                        help="format string used as a key for response lookup: \
                        example: \"{%%Host}{%%Server}{PATH}\", \"{HOST}{PATH}\", \"{PATH}\"\
                        All the args preceded by %% are header fields in the request\
                        The only two acceptable arguments which are not header fields are : fqdn (represented by HOST) and the url path (represented by PATH) in a request line.\
                        Example: given a client request as  << GET /some/resource/location HTTP/1.1\nHost: hahaha.com\n\n >>, if the user wishes the host field and the path to be used for the response lookup\
                        then the required format will be {%%Host}{PATH}")

    parser.add_argument("--verbose", "-v",
                        action="store_true",
                        default=True,
                        help="More informative outputs")

    parser.add_argument("--both",
                        action="store_true",
                        help="Run both SSL and non-SSL servers")

    parser.add_argument("--s_port", "-s",
                        type=int,
                        default=glb.DEFAULT_SSL_SERVER_PORT,
                        help="SSL port to use")

    args = parser.parse_args()

    server = microserver.MicroServer(args.data_dir, ip=args.ip_address, port=args.port, s_port=args.s_port, delay=args.delay,
                                     timeout=args.timeout, useSSL=args.ssl, sslKey=args.key, sslCert=args.cert,
                                     clientVerify=args.clientverify, hooks=args.load, lookupKey=args.lookupkey, both=args.both, verbose=args.verbose, clientCA=args.clientCA)

    server.serve_forever()


if __name__ == '__main__':
    main()
