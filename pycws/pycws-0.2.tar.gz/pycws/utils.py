# Utilities
import base64
import six

ENCODING = 'utf-8'


def b64encode(txt):
    """ Handle encoding of mostly passwords in a py2/py3 compatible way so that they can be used in json """
    if isinstance(txt, six.string_types):
        # b64encode in python 3 expects a bytes-like
        txt = txt.encode('utf-8')
    b64_txt = base64.b64encode(txt)
    if isinstance(b64_txt, six.binary_type):
        b64_txt = b64_txt.decode(ENCODING)
    return b64_txt
