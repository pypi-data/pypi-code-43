"""
This is the core file to import into any notebook or program to create a pipeline.
It is not needed by worker_process. Hence this code is kept separate to __init__.py

usage::

    from pipemaker.master.init import *
"""
import socket
import requests
import logging
log = logging.getLogger()

from .flask import view
from .db import db
from .config import creds, config
from .function import config

from ..worker import workers
from ..queues import eventq, logq
from ..filesystem import ftpserver
from ..filesystem.filepath import Filepath

from .pipeline import make, make_all

### enable shortnames without using full path ###############################################################

def name2filepath(name):
    """ return filepath from name
    """
    path = config.paths.get(name, config.path)
    config.pathvars.name = name
    return Filepath(path.format(**config.pathvars))

def load(name):
    """ return contents
    """
    fp = name2filepath(name)
    return fp.load()

def save(obj, name):
    """ save obj to filename or url """
    fp = name2filepath(name)
    fp.save(obj)

def start(force=False):
    """ start everything and delete processes. Just restarting notebook leaves processes running.
    """
    if not force:
        try:
            # if flask running then don't start
            r = requests.get("http://localhost:5000")
            if r.status_code == 200:
                log.warning("already running")
                return
        except:
            pass

    log.info("starting everything")
    cleanup()

    workers.terminate()
    workers.start()

    view.restart()

    eventq.restart()

    logq.Logq().delete()

    db.delete_tables()

def set_ftp():
    """ switch filesystem to ftp for distributed processing """
    log.info("setting ftp")
    # lan address
    config.ftp_address = socket.gethostbyname(socket.getfqdn())

    # datapath is part of filesystem so ftp server can expose only that folder
    config.path = "{filesystem}|{job}/{name}{extension}"
    config.pathvars.filesystem = f"ftp://{creds.username}:{creds.password}@{config.ftp_address}:{config.ftp_port}"
    ftpserver.start()

def cleanup(datapath=None, check=False):
    """ cleanup all temp folders
    :param check: ask for confirmation before delete
    """
    if datapath is None:
        datapath = config.pathvars.datapath
    fp = Filepath(datapath)
    globber = fp.ofs.glob(f"{fp.path}/**/temp/")
    folders = "\n".join([f.path for f in globber])
    if not folders:
        return
    r = "y"
    if check:
        r = input(f"Cleanup will delete the following temp folders. Please enter y to confirm.\n{folders}\n")
    if r=="y":
        globber.remove()
        log.info("deleted temp folders")
    else:
        log.info("cancelled deletion of temp folders")