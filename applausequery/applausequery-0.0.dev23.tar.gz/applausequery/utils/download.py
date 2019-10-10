# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
Module for downloading non-table content in APPLAUSE
"""

from os.path import basename
from urllib.request import urlretrieve


__all__ = ['get_file']

__basepath = "https://www.plate-archive.org/files/"


def get_file(path, filename=None):
    """
    Download file from APPLAUSE web server

    Parameters
    ----------
    path : str
        Path on APPLAUSE web server as listed in the database tables, typically
        something like DR3/logbooks/POT050/POT050-OB1-000390-000392.jpg

    save_filename : str, optional
        Filename/path to be used to save the result. If not passed as an
        arguement, the original filename will be used and saved in current dir
    """
    if filename is None:
        urlretrieve(__basepath+path, filename=basename(path))
    else:
        urlretrieve(__basepath+path, filename=filename)