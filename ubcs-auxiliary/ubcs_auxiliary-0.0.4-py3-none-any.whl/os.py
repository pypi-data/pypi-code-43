def find(topdir, name=[], exclude=[]):
    """A list of files found starting at 'topdir' that match the patterns given
    by 'name', excluding those matching the patterns given by 'exclude'.
    returns a vector of integers on logarithmic scale starting from decade start, ending decade end with M per decade

    Parameters
    ----------
    topdir (string)
    name (list)
    exclude (list)

    Returns
    -------
    file_list (list)

    Examples
    --------
    >>> res = anfinrud_auxiliary.os.walk('anfinrud_auxiliary/')
    >>> for i in res: print(i[0])
            ...:
        anfinrud_auxiliary/
        anfinrud_auxiliary/tests
        anfinrud_auxiliary/tests/__pycache__
        anfinrud_auxiliary/__pycache__

    Comments:
    ---------

    Python 3.7.4 (v3.7.4:e09359112e, Jul  8 2019, 14:54:52)
    Type 'copyright', 'credits' or 'license' for more information
    IPython 7.8.0 -- An enhanced Interactive Python. Type '?' for help.
    In [1]: from time import time
    In [2]: import anfinrud_auxiliary
    In [3]: res = anfinrud_auxiliary.os.walk('/Volumes/C/All Projects/APS/Instrumentation/Software/Lauecollect/')
    In [4]: t1 = time(); lst = list(res); t2 = time(); print(t2-t1, len(lst))
    3.9815242290496826 1346

    Python 2.7.16 (v2.7.16:413a49145e, Mar  2 2019, 14:32:10)
    Type "copyright", "credits" or "license" for more information.
    IPython 5.8.0 -- An enhanced Interactive Python.
    In [1]: from time import time
    In [2]: import anfinrud_auxiliary
    In [3]: res = anfinrud_auxiliary.os.walk('/Volumes/C/All Projects/APS/Instrumentation/Software/Lauecollect/')
    In [4]: t1 = time(); lst = list(res); t2 = time(); print(t2-t1, len(lst))
    (0.77646803855896, 1346)
    """

    def glob_to_regex(pattern):
        return "^"+pattern.replace(".", "\.").replace("*", ".*").replace("?", ".")+"$"
    try:
        from scandir import walk
    except ImportError:
        from os import walk
    import re
    if type(name) == str:
        name = [name]
    if type(exclude) == str:
        exclude = [exclude]
    name = [re.compile(glob_to_regex(pattern)) for pattern in name]
    exclude = [re.compile(glob_to_regex(pattern)) for pattern in exclude]

    file_list = []
    for (directory, subdirs, files) in walk(topdir):
        for file in files:
            pathname = directory+"/"+file
            match = any([pattern.match(pathname) for pattern in name]) and\
                not any([pattern.match(pathname) for pattern in exclude])
            if match:
                file_list += [pathname]
    return file_list

def exclude():
    """Returns a list of patterns to exclude from a search. Add
    terms as required."""
    exclude = ['*/alignment*',
               '*/trash*',
               '*/_Archived*',
               '*/backup*',
               '*/Commissioning*',
               '*/Test*',
               '*/.AppleDouble*',
               '*LaserX*',
               '*LaserZ*',
               '*Copy*',
               '*._*',
               '.DS_Store']
    return exclude

def image_file_names_from_path(beamtime,path_name):
    """Returns image file names found under path_name. Typically used with
    'Reference_*() , which specifies which directories contain data for which
    zinger-free-statistics are to be acquired. The zinger-free-statistics
    include Imean and Ivar, which are used to construct UC_psi.npy."""
    from db_functions import find,exclude
    from numpy import sort
    data_dir,analysis_dir = data_dir_analysis_dir(beamtime)
    terms = ['*.mccd','*.rx']
    image_files = sort(find(data_dir+path_name, name=terms, exclude=exclude()))
    return image_files

def N_files_in_dir(folder = '/Volumes/C/All Projects/APS/Instrumentation/Software/Lauecollect/', match = '*'):
    import os
    import fnmatch
    integer = len(fnmatch.filter(os.listdir(folder), match))
    return integer
