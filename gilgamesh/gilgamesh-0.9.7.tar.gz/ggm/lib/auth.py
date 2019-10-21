"""
    Copyright (c) 2019 Contributors as noted in the AUTHORS file
    This file is part of ggm, the GILGAMESH core engine in Python.
    ggm is free software; you can redistribute it and/or modify it under
    the terms of the GNU Lesser General Public License (GPL) as published
    by the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.
    As a special exception, the Contributors give you permission to link
    this library with independent modules to produce an executable,
    regardless of the license terms of these independent modules, and to
    copy and distribute the resulting executable under terms of your choice,
    provided that you also meet, for each linked independent module, the
    terms and conditions of the license of that module. An independent
    module is a module which is not derived from or based on this library.
    If you modify this library, you must extend this exception to your
    version of the library.
    ggm is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
    License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import sys
import zmq
import socket
import zmq.auth
from zmq.auth.asyncio import AsyncioAuthenticator

from .kontext import Kontext

from pprint import pprint

class GAuthServer(object):
    """
        TODO: write doc
    """
    def __init__(self, *args, **kwargs):
        from pathlib import Path
        if not kwargs['server_key']:
            raise Exception('Nope!')

        keys_dir = kwargs['keys_path']
        public_keys_dir = keys_dir / 'public_keys'
        secret_keys_dir = keys_dir / 'private_keys'

        if not (keys_dir.exists() and
                public_keys_dir.exists() and
                secret_keys_dir.exists()):
            print("CURVE Server: Certificate missing -- this device needs to be comissioned first!")
            print(public_keys_dir, secret_keys_dir)
            sys.exit(1)

        ctx = kwargs['context']
        # Start an authenticator for this context.
        auth = AsyncioAuthenticator(ctx)
        auth.start()
        #auth.allow('127.0.0.1')
        auth.allow()
        # Tell authenticator to use the certificate in a directory
        auth.configure_curve(domain='*', location=public_keys_dir)

        self.server = ctx.socket(zmq.ROUTER)

        server_secret_file = secret_keys_dir / Path(f'{kwargs["server_key"]}.key_secret')
        server_public, server_secret = zmq.auth.load_certificate(server_secret_file)
        self.server.curve_secretkey = server_secret
        self.server.curve_publickey = server_public
        self.server.curve_server = True  # must come before bind
        self.server.bind(f'tcp://*:{kwargs["port"]}')

class GAuthClient(object):
    """
        TODO: write doc
    """
    def __init__(self, *args, **kwargs):
        from pathlib import Path
        if not kwargs['server_key']:
            raise Exception('Nope!')
        if not kwargs['client_key']:
            raise Exception('Nope!')

        keys_dir = kwargs['keys_path']
        public_keys_dir = keys_dir / 'public_keys'
        secret_keys_dir = keys_dir / 'private_keys'

        if not (keys_dir.exists() and
                public_keys_dir.exists() and
                secret_keys_dir.exists()):
            print("CURVE Server: Certificate missing -- this device needs to be comissioned first!")
            print(public_keys_dir, secret_keys_dir)
            sys.exit(1)

        self.ctx = Kontext()
        self.client = self.ctx.socket(zmq.DEALER)

        client_secret_file = secret_keys_dir / Path(f'{kwargs["client_key"]}.key_secret')
        client_public, client_secret = zmq.auth.load_certificate(client_secret_file)
        self.client.curve_secretkey = client_secret
        self.client.curve_publickey = client_public

        server_public_file = public_keys_dir / Path(f'{kwargs["server_key"]}.key')
        server_public, _ = zmq.auth.load_certificate(server_public_file)
        # The client must know the server's public key to make a CURVE connection.
        self.client.curve_serverkey = server_public
        #woohoo
        retry = 0
        hostname = kwargs['hostname']
        ## FIXME retrying forever is bad practice!
        while True:
            if 'ip' in kwargs:
                break
            retry+=1
            try:
                ip = socket.gethostbyname(hostname)
                kwargs['ip'] = ip
                break
            except Exception as e:
                #print(f'Could not resolve {hostname} - retry {retry}/inf')
                continue
            #if retry == 100:
            #    sys.exit(1)
        # TODO what if the IP changes?!
        # maybe with setsockopt(zmq.heartbeat) ?
        self.client.connect(f'tcp://{kwargs["ip"]}:{kwargs["port"]}')
