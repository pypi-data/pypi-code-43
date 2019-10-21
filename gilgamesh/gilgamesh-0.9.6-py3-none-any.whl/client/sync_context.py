import zlib
import json
import pickle
import zmq

class GSock(zmq.Socket):
    """A class with some extra serialization methods
    
    """
    def psend(self, msg, compression=False):
        """
        send msg with internal routing as list
        and pickled payload
        """
        # if msg is dict -- return immediately
        # if msg len is 1 -- return immediately
        if isinstance(msg, dict):
            ret = self.send_pyobj(msg)
            return ret
        elif not isinstance(msg, list):
            return True # !!! FIXME
        elif len(msg) <= 1:
            ret = self.send_pyobj(msg)
            return ret

        p = []
        p.extend(msg[:-1])
        if compression:
            comp = zlib.compress(pickle.dumps(msg[-1]))
            p.append(comp)
        else:
            p.append(pickle.dumps(msg[-1]))
        ret = self.send_pyobj(p)
        return ret

    def precv(self, compression=False):
        """
        recv msg with internal routing as list
        and unpickle payload
        """
        msg = self.recv_pyobj()
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

    def dsend(self, msg, z_route=None, compression=False):
        """
        sending as dealer to dealer (resource worker/client/...)

        emtpy frame for compatibility with req/rep OR zmq internal route
        """
        p = z_route or [b'']

        # if msg is dict return immediately
        if isinstance(msg, dict):
            p.append(pickle.dumps(msg))
            ret = self.send_multipart(p)
            return ret
        elif not isinstance(msg, list):
            return True # !!! FIXME
        elif len(msg) <= 1:
            p.append(pickle.dumps(msg))
            ret = self.send_multipart(p)
            return ret

        # internal app route
        payload = msg[:-1]

        if compression:
            comp = zlib.compress(pickle.dumps(msg[-1]))
            payload.append(comp)
        else:
            payload.append(pickle.dumps(msg[-1]))

        p.append(pickle.dumps(payload))
        ret = self.send_multipart(p)
        return ret

    def drecv(self, compression=False):
        """receiving as dealer from dealer(resource worker)
        compatible with req/rep
        """
        rawmsg = self.recv_multipart()
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


class Kontext(zmq.Context):
    _socket_class = GSock
