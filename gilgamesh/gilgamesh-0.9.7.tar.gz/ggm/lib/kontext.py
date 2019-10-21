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
import zlib
import json
import pickle
import asyncio
import zmq.asyncio

class GSock(zmq.asyncio.Socket):
    """A class with some extra serialization methods
        this is the place for the nasty protocol code
        roll your is advised
    """
    async def psnd(self, msg, compression=False):
        """
        send msg with internal routing as list
        and pickled payload
        """
        # if msg is dict -- return immediately
        # if msg len is 1 -- return immediately
        if isinstance(msg, dict):
            ret = await self.send_pyobj(msg)
            return ret
        elif not isinstance(msg, list):
            return True # !!! FIXME
        elif len(msg) <= 1:
            ret = await self.send_pyobj(msg)
            return ret

        p = []
        p.extend(msg[:-1])
        if compression:
            comp = zlib.compress(pickle.dumps(msg[-1]))
            p.append(comp)
        else:
            p.append(pickle.dumps(msg[-1]))
        ret = await self.send_pyobj(p)
        return ret

    async def precv(self, compression=False):
        """
        recv msg with internal routing as list
        and unpickle payload
        """
        msg = await self.recv_pyobj()
        if isinstance(msg, dict):
            return msg
        elif not isinstance(msg, list):
            return True # !!! FIXME
        elif len(msg) <= 1:
            return msg

        route = msg[:-1]
        if compression:
            decomp = pickle.loads(zlib.decompress(msg[-1]))
            msg[-1] = decomp
        else:
            msg[-1] = pickle.loads(msg[-1])

        return msg

    async def dsend(self, msg, z_route=None, compression=False):
        """
        sending as dealer to dealer (resource worker/client/...)

        emtpy frame for compatibility with req/rep OR zmq internal route
        """
        p = z_route or [b'']

        # if msg is dict return immediately
        if isinstance(msg, dict):
            p.append(pickle.dumps(msg))
            ret = await self.send_multipart(p)
            return ret
        elif not isinstance(msg, list):
            return True # !!! FIXME
        elif len(msg) <= 1:
            p.append(pickle.dumps(msg))
            ret = await self.send_multipart(p)
            return ret

        # internal app route
        payload = msg[:-1]

        if compression:
            comp = zlib.compress(pickle.dumps(msg[-1]))
            payload.append(comp)
        else:
            payload.append(pickle.dumps(msg[-1]))

        p.append(pickle.dumps(payload))
        ret = await self.send_multipart(p)
        return ret

    async def drecv(self, compression=False):
        """receiving as dealer from dealer(resource worker)
        compatible with req/rep
        """
        rawmsg = await self.recv_multipart()
        route = rawmsg[:-1]
        msg = pickle.loads(rawmsg[-1])
        if isinstance(msg, dict):
            return route, msg
        elif not isinstance(msg, list):
            return True # !!! FIXME
        elif len(msg) <= 1:
            return route, msg

        if compression:
            decomp = pickle.loads(zlib.decompress(msg[-1]))
            msg[-1] = decomp
        else:
             msg[-1] = pickle.loads(msg[-1])
        #print(route, msg)
        return route, msg

    async def upstream(self, cmd, segment, source, compression=False):

        CHUNK_SIZE = 1000
        PIPELINE = 1

        credit = PIPELINE   # Up to PIPELINE chunks in transit
        total = 0           # Total records received
        chunks = 0          # Total chunks received
        offset = 0          # Offset of next chunk request

        up_cmd = ['series', 'upload']
        up_cmd.extend(cmd[2:])
        up_cmd.append(b'') #FIXME WTF

        cmd.append(segment)

        while True:
            while credit:
                segment['offset'] = offset
                segment['limit']= CHUNK_SIZE
                cmd[-1] = segment
                await source.dsend(cmd)
                offset += CHUNK_SIZE
                credit -= 1
            route, msg = await source.drecv(compression)
            up_cmd[-1] = msg
            if msg:
                await self.dsend(up_cmd)
                route, reply = await self.drecv()
            chunks += 1
            credit += 1
            size = len(msg)
            if size < CHUNK_SIZE:
                break
            # FIXME hack for upload 'flow control'
            await asyncio.sleep(3)

        # 'empty' pipeline
        while credit < PIPELINE:
            route, msg = await source.drecv(compression)
            up_cmd[-1] = msg
            if msg:
                await self.dsend(up_cmd)
                route, reply = await self.drecv()
            credit += 1
        #!!
        return await asyncio.sleep(0.1)

    async def psend_noerr(self, msg):
        await self.psnd({"Error": False, 'Reason': msg})
    async def dsend_noerr(self, msg, z_route=None):
        await self.dsend({"Error": False, 'Reason': msg}, z_route)
    async def psend_err(self, errmsg):
        await self.psnd({"Error": True, 'Reason': errmsg})
    async def dsend_err(self, errmsg, z_route=None):
        await self.dsend({"Error": True, 'Reason': errmsg}, z_route)

class Kontext(zmq.asyncio.Context):
    _socket_class = GSock
