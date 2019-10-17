# coding=utf-8
# Licensed Materials - Property of IBM
# Copyright IBM Corp. 2019

# imports
import requests
import json
import re
from tempfile import gettempdir
import random
import wget
import string
import os
import tarfile
import shutil
import glob

# product toolkits
tkprodList = ['com.ibm.streamsx.avro',
              'com.ibm.streamsx.datetime',
              'com.ibm.streamsx.dps',
              'com.ibm.streamsx.elasticsearch',
              'com.ibm.streamsx.eventstore',
              'com.ibm.streamsx.hbase',
              'com.ibm.streamsx.hdfs',
              'com.ibm.streamsx.inet',
              'com.ibm.streamsx.inetserver',
              'com.ibm.streamsx.iot',
              'com.ibm.streamsx.jdbc',
              'com.ibm.streamsx.jms',
              'com.ibm.streamsx.json',
              'com.ibm.streamsx.kafka',
              'com.ibm.streamsx.mail',
              'com.ibm.streamsx.messagehub',
              'com.ibm.streamsx.messaging',
              'com.ibm.streamsx.mqtt',
              'com.ibm.streamsx.network',
              'com.ibm.streamsx.objectstorage',
              'com.ibm.streamsx.rabbitmq',
              'com.ibm.streamsx.sparkmllib',
              'com.ibm.streamsx.topology'
            ]

pypackagelist = ['streamsx',
                 'streamsx.avro',
                 'streamsx.database',
                 'streamsx.elasticsearch',
                 'streamsx.endpoint',
                 'streamsx.eventstore',
                 'streamsx.eventstreams',
                 'streamsx.hbase', 
                 'streamsx.hdfs',
                 'streamsx.inet',
                 'streamsx.kafka',
                 'streamsx.objectstorage',
                 'streamsx.pmml',
                 'streamsx.toolkits',
                ]



def _sorted_version(an_iterable):
    """ Sorts the given iterable in the way that is expected.

    Required arguments:
    an_iterable -- The iterable to be sorted.

    """
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(an_iterable, key = alphanum_key)


def _clean_dir(tmp_path, toolkit_dir, target_dir):
    for i in glob.glob(os.path.join(tmp_path, "*")):
        if os.path.isfile(i):
            os.remove(os.path.realpath(i))
        elif os.path.isdir(i):
            dirname = os.path.basename(i)
            if toolkit_dir != dirname:
                shutil.rmtree(os.path.realpath(i))
    shutil.move(os.path.join(tmp_path, toolkit_dir), target_dir)
    shutil.rmtree(tmp_path)


def _download_tk(url, name, toolkit_dir):
    """Downloads and unpacks the toolkit.
    
    Args:
        url(str): the download URL
        name(str): the subdirectory relative to the temporary directory (/tmp), where the toolkit is unpacked to
        toolkit_dir(str): the toolkit directory in the archive (where toolkit.xml is located)
    
    Returns:
        str: the absolute toolkit directory
    """
    rnd = ''.join(random.choice(string.digits) for _ in range(10))
    targetdir = os.path.join(gettempdir(), name) + '-' + rnd
    tmp_dir = targetdir + 'tmp'
    tmpfile = gettempdir() + '/' + 'toolkit-' + rnd + '.tgz'
    if os.path.isdir(tmp_dir):
        shutil.rmtree(tmp_dir)
    if os.path.isdir(targetdir):
        shutil.rmtree(targetdir)
    if os.path.isfile(tmpfile):
        os.remove(tmpfile)
    wget.download(url, tmpfile)
    #print (tmpfile + ": " + str(os.stat(tmpfile)))
    tar = tarfile.open(tmpfile, "r:gz")
    tar.extractall(path=tmp_dir)
    tar.close()
    # delete archive file
    os.remove(tmpfile)
    # clean-up all non toolkit dirs
    _clean_dir(tmp_dir, toolkit_dir, targetdir)
    # final toolkit location
    toolkit_path = targetdir
    # dump toolkit version
    tkfile = toolkit_path + '/toolkit.xml'
    if os.path.isfile(tkfile):
        f = open(tkfile, "r")
        for x in f:
            if 'toolkit name' in x:
                version_dump = re.sub(r' requiredProductVersion="[^ ]*"', '', x)
                print('\n'+version_dump)
                break
        f.close()
    return toolkit_path


def download_toolkit(toolkit_name, repository_name=None, url=None, target_dir=None):
    r"""Downloads the latest SPL toolkit from GitHub for the given toolkit name.

    Example for adding the com.ibm.streams.nlp toolkit with latest toolkit from GitHub::

        import streamsx.toolkits as tkutils
        # download toolkit from GitHub
        location = tkutils.download_toolkit('com.ibm.streamsx.nlp')
        # add toolkit to topology
        streamsx.spl.toolkit.add_toolkit(topo, location)

    Args:
        toolkit_name(str): the toolkit directory in the archive (where toolkit.xml is located), for example "com.ibm.streamsx.nlp"
        repository_name(str): name of the GitHub repository at "github.com/IBMStreams", for example "streamsx.nlp". Set this parameter if repository name is not part of toolkit name without "com.ibm.".
        url(str): the download URL, apply link to toolkit archive (\*.tgz) to be downloaded. 'https://github.com/IBMStreams/REPOSITORY-NAME/releases/latest' is used per default.
        target_dir(str): the directory where the toolkit is unpacked to. If a relative path is given,
            the target_dir is appended to the system temporary directory, for example to /tmp on Unix/Linux systems.
    
    Returns:
        str: the absolute path of the toolkit directory

    .. note:: This function requires an outgoing Internet connection
    """
    if repository_name is None:
        repo_name = toolkit_name[8::]
    else:
        repo_name = repository_name

    if target_dir is None:
        target_dir = toolkit_name

    if url is None:
        # get latest toolkit
        r = requests.get('https://github.com/IBMStreams/'+repo_name+'/releases/latest')
        r.raise_for_status()
        if r.text is not None:
            s = re.search(r'/IBMStreams/'+repo_name+'/releases/download/.*tgz', r.text).group()
            url = 'https://github.com/' + s
    if url is not None:
        print('Download: ' + url)
        spl_toolkit = _download_tk(url, target_dir, toolkit_name)
    else:
        raise ValueError("Invalid URL")
    return spl_toolkit


def get_pypi_packages(package_name=None):
    """ Discover the latest Python packages available on pypi.org.
    
    Args:
        package_name(str): the name of the Python package to be searched for. If ``None`` is given,
        the function searches for all available streamsx Python packages.
        
    Returns:
        dict: A dictionary with mappings from Python package name to the package version

    .. note:: This function requires an outgoing Internet connection
    """
    pypi_packages = {}
    _pkg_list = pypackagelist if package_name is None else [package_name]

    for pkg_name in _pkg_list:
        r = requests.get('https://pypi.python.org/pypi/'+pkg_name+'/json')
        if r.status_code==200:
            data_json = r.json()
            releases = list(data_json["releases"].keys())
            latest_version = _sorted_version(releases)[-1]
            print(pkg_name + ' - ' + latest_version)
            pypi_packages[pkg_name]=latest_version
    return pypi_packages


def get_installed_packages():
    """ Discover installed `streamsx` python packages in your Python environment.

     Returns:
        dict: A dictionary with mappings from Python package name to the package version
   """
    installed_packages = {}
    for pkg_name in pypackagelist:
        try:
            import importlib
            i = importlib.import_module(pkg_name)
            if pkg_name is 'streamsx':
                import streamsx.topology.context
                print(pkg_name+' - ' + i.topology.context.__version__)
                installed_packages[pkg_name] = i.topology.context.__version__
            else:
                print(pkg_name+' - ' + i.__version__)
                installed_packages[pkg_name] = i.__version__
        except ImportError as error:
            print(pkg_name + ' NOT INSTALLED')
    return installed_packages


def get_build_service_toolkits(streams_cfg):
    """ Discover toolkits on IBM Streams build service.
    
    Args:
        streams_cfg(dict): Service instance details of the IBM Streams instance.
        
    Returns:
        dict: A dictionary with mappings from toolkit name to the toolkit version

    .. warning:: The function can be used only in IBM Cloud Pak for Data
    """
    build_service_toolkits = {}
    token = streams_cfg['service_token']
    build_endpoint = streams_cfg['connection_info']['serviceBuildEndpoint']
    toolkits_url = build_endpoint.replace('/builds', '/toolkits', 1)
    #print (toolkits_url)
    r = requests.get(toolkits_url, headers={"Authorization": "Bearer " + token}, verify=False)
    if r.status_code==200:
        sr = r.json()
        #print(sr)
        for x in sr['toolkits']:
            print (x['name'] + ' - ' + x['version'])
            build_service_toolkits[x['name']]=x['version']
    else:
        print(str(r))
    return build_service_toolkits
        

def get_github_toolkits(toolkit_name=None):
    """ Discover the latest releases of product toolkits available on public GitHub.
    
    Args:
        toolkit_name(str): the name of the toolkit to be searched for. If ``None`` is given,
        the function searches for all product toolkits.
        
    Returns:
        dict: A dictionary with mappings from toolkit name to the toolkit version

    .. note:: This function requires an outgoing Internet connection
    """
    if toolkit_name is None:
        _tk_list = tkprodList
    else:
        _tk_list = [toolkit_name]
    github_toolkits = {}
    for tk_name in _tk_list:
        repo_name = tk_name[8::]
        r = requests.get('https://github.com/IBMStreams/'+repo_name+'/releases/latest')
        #print (r.url)
        if r.status_code==200:
            urlstr = r.url
            tk_version = None
            idx = urlstr.find('tag/v')
            if idx > -1:
                tk_version = urlstr[idx+5:]
            else:
                idx = urlstr.find('tag/')
                if idx > -1:
                    tk_version = urlstr[idx+4:]
            if tk_version is not None:
                print (tk_name + ' - ' + tk_version)
                github_toolkits[tk_name]=tk_version
    return github_toolkits

