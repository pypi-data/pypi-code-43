from zml.backend import IpfsBackend, RestBackend


class Resource:

    def __init__(self, address=None, lazy=True, code=None, mime_type=None):
        self.address = address
        self.code = code
        self.mime_type = mime_type
        self.is_media = False
        self.lazy = lazy
        self.loaded = False
        if not lazy:
            self.load()

    def load(self):
        if self.address[0] == 'Q':
            backend = IpfsBackend()
            self.type = 'ipfs'
            raw, mime_type = backend.load(self.address)
        elif self.address.startswith('http://'):
            backend = FileBackend()
            self.type = 'file'
            raw, mime_type = backend.load(self.address)
        else:
            backend = RestBackend()
            self.type = 'rest'
            raw, mime_type = backend.load(self.address)

        if mime_type in ['image/jpeg', 'image/png', 'image/gif']:
            self.code = raw
            self.is_media = True
        else:
            self.code = raw
            if not isinstance(raw, str) and not isinstance(raw, dict):
                self.code = self.code.decode('utf-8')
        self.mime_type = mime_type
        self.loaded = True

    def import_resource(self, document):
        if not self.loaded:
            self.load()
        if self.type in ['ipfs', 'file']:
            if self.mime_type in ['image/jpeg', 'image/png', 'image/gif']:
                raise Exception('Cannot import media files')
            else:
                return document.import_source(self.code)
        else:
            # update local context with json from rest document
            document.local_context.update(self.code)
