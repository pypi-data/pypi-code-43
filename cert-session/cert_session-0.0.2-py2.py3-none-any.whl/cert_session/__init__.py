"""Wraps a requests.Session object
"""

import tempfile
import shutil
import os
import sys

import requests
import certifi

class Session(requests.Session):
    """Wraps a requests.Session object
    in order to append root certificates to its default collection.
    """
    def __init__(self, certs_filepath):
        super().__init__()
        self.verify = _create_certifi_temp(certs_filepath)


    def __enter__(self):
        if hasattr(super(), '__enter__'):
            return super().__enter__()

        return self


    def __exit__(self, exc_type, exc_value, traceback):  # pylint: disable=arguments-differ
        if exc_type:
            print(f'Temporary certificate authority file: {self.verify}\n', file=sys.stderr)
            print('You can delete this.')
        else:
            os.unlink(self.verify)

        super().__exit__()


    def __del__(self):
        os.unlink(self.verify)


def _create_certifi_temp(certs_filepath):
    """Returns a path to a new file whose contents
    are the contents of the file certifi.where()
    followed by an empty line
    followed by the contents of certs_filepath.
    """
    (_, tmpfilepath) = tempfile.mkstemp(suffix='.crt')
    os.close(_)
    shutil.copyfile(certifi.where(), tmpfilepath)

    with open(tmpfilepath, mode='a') as fdest:
        fdest.write('\n')

        with open(certs_filepath) as fsrc:
            shutil.copyfileobj(fsrc, fdest)

    return tmpfilepath
