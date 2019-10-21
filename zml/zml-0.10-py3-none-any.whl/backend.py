import requests
import ipfshttpclient
from functools import lru_cache
import functools
from datetime import datetime, timedelta
import magic


def timed_cache(**timedelta_kwargs):

    def _wrapper(f):
        update_delta = timedelta(**timedelta_kwargs)
        next_update = datetime.utcnow() - update_delta
        # Apply @lru_cache to f with no cache size limit
        f = functools.lru_cache(None)(f)

        @functools.wraps(f)
        def _wrapped(*args, **kwargs):
            nonlocal next_update
            now = datetime.utcnow()
            if now >= next_update:
                f.cache_clear()
                next_update = now + update_delta
            return f(*args, **kwargs)
        return _wrapped
    return _wrapper


class Backend:

    def load(self):
        raise NotImplementedError("Method load not implemented.")

    def save(self):
        raise NotImplementedError("Method save not implemented.")


class FileBackend(Backend):

    def load(self, filename):
        with open(filename) as f:
            raw = f.read()
        mime_type = magic.from_buffer(raw, mime=True)
        return raw, mime_type

    def save(self, filename, code):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(code)


class IpfsBackend(Backend):

    def __init__(self):
        self.client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001/http')

    @lru_cache()
    def get_peer_id(self):
        return self.client.key.list()['Keys'][0]['Id']

    @lru_cache()
    def get_peer_cid(self):
        peer_id = self.get_peer_id()
        profile_cid = self.client.name.resolve(peer_id)['Path'].split('/')[-1]
        return profile_cid

    @lru_cache()
    def get_profile(self):
        profile_cid = self.get_peer_cid()
        return self.client.cat(profile_cid).decode('utf-8')

    def cache_clear(self):
        self.get_peer_id.cache_clear()
        self.get_profile.cache_clear()

    def add_str(self, code):
        return self.client.add_str(code)

    def load(self, address):
        raw = self.client.cat(address)
        mime_type = magic.from_buffer(raw, mime=True)
        if mime_type in ['image/jpeg', 'image/png', 'image/gif']:
            res = raw
        else:
            res = raw.decode('utf-8')
        return res, mime_type

    def save(self, code):
        return self.add_str(code)


class RestBackend(Backend):

    def load(self, address):
        url = address
        if not url.startswith('https'):
            url = 'https://' + url
            response = requests.get(url)
        root = response.json()
        mime_type = 'text/html'
        return root, mime_type

    def save(self, code):
        pass
