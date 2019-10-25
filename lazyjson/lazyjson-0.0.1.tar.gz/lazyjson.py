"""
lazyjson.py v0.0.1

MIT License

Copyright (c) 2019 Will Stott

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json


class LazyJSON:
    """
    A wrapper for json-encoded strings which allows them to be passed around
    as known-encoded JSON and only decoded when needed within your programs.

    If you completely trust the data you can use the SafeJSON wrapper which
    allows the JSON to be embedded in JSON documents encoded by
    JSONPassthroughEncoder.
    """
    __slots__ = ['json_str']
    def __init__(self, json_str):
        self.json_str = json_str

    def parse(self):
        return json.loads(self.json_str)


class SafeJSON(LazyJSON):
    """
    A wrapper for json-encoded strings which allows them to be output within a
    JSON document by the JSONPassthroughEncoder without decoding first.

    Blindly wrapping untrusted JSON strings using this could result in JSON
    injection attacks. Please be careful.
    """
    def __init__(self, json_str):
        if isinstance(json_str, LazyJSON):
            self.json_str = json_str.json_str
        else:
            self.json_str = json_str


class SafeJSONFile():
    """
    A wrapper for json-encoded files which allows them to be output within a
    JSON document by the JSONPassthroughEncoder without decoding first.

    Blindly wrapping untrusted JSON strings using this could result in JSON
    injection attacks. Please be careful.
    """
    __slots__ = ['json_file', 'chunk_size']
    def __init__(self, json_file, chunk_size=2048):
        self.json_file = json_file
        self.chunk_size = chunk_size


class JSONPassthrough(object):
    _lazy = None

    def default(self, o):
        if isinstance(o, (SafeJSON, SafeJSONFile)):
            # Store the string for next yield of iterencode.
            self._lazy = o
            # Return any easily encodable value.
            return True
        return super().default(o)
    default.__doc__ = json.JSONEncoder.__doc__

    def iterencode(self, o, _one_shot=False):
        """
        Encode the given object and yield each string representation as it
        becomes available.

        For example::
    
            for chunk in JSONEncoder().iterencode(bigobject):
                mysocket.write(chunk)
        """
        # _one_shot avoid all the iterative behaviour that we rely upon to make
        # this whole trick work. So we disable it here. This is why the
        # performance is so abysmal :(
        for t in super().iterencode(o, _one_shot=False):
            if self._lazy is None:
                yield t
            else:
                l = self._lazy
                self._lazy = None
                if isinstance(l, SafeJSONFile):
                    if _one_shot:
                        yield l.json_file.read()
                    else:
                        while True:
                            dat = l.json_file.read(l.chunk_size)
                            if dat:
                                yield dat
                            else:
                                break
                else:
                    yield l.json_str


class JSONPassthroughEncoder(JSONPassthrough, json.JSONEncoder):
    """
    A JSON encoder which will output strings wrapped with the SafeJSON class
    exactly as they appear without any additional encoding or verification.

    Only use this class with trusted JSON input wrapped with SafeJSON
    making up an large proportion of the JSON document, as this class adds
    significant overhead to normal primitive encoding.

    For example::
        st = os.stat('my.json')
        content = open('my.json').read():
        doc = {
            "size": st.st_size,
            "mtime": st.st_mtime,
            "content": SafeJSON(content),
        }
        for t in JSONPassthroughEncoder().iterencode(doc):
            socket.write(t)

    Files can also be read lazily::
        st = os.stat('massive.json')
        with open('massive.json') as f:
            doc = {
                "size": st.st_size,
                "mtime": st.st_mtime,
                "content": SafeJSONFile(f),
            }
        for t in JSONPassthroughEncoder().iterencode(doc):
            socket.write(t)
    """
    pass

