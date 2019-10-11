import sys
import concurrent.futures
from blowpipe.logger import Logger
from blowpipe import config

import os
from blowpipe import utils, model_db

BLOWPIPE_DEFAULT_CFG = """
[http]
enabled=False
port=80
ip=0.0.0.0

[grpc]
enabled=True
port=50051
ip=::

[database]
type=sqlite
"""


def init(filename):

    abs_filename = utils.resolve_file(filename)
    parent_dir, fname = utils.split_file(abs_filename)
    if not os.path.isdir(parent_dir):
        os.makedirs(parent_dir)

    Logger.console("Initialising '" + filename + "'.")
    f = open(abs_filename, 'w')
    f.write(BLOWPIPE_DEFAULT_CFG)
    f.close()

    cfg = utils.IniFile(abs_filename)
    if not os.path.isdir(cfg.get_root_dir()):
        os.makedirs(cfg.get_root_dir())

    Logger.console("Initialising '" + filename + "' ok.")

    log_dirname = cfg.get_root_dir() + "/logs"
    if not os.path.isdir(log_dirname):
        os.makedirs(log_dirname)

    sqlite_filename = "sqlite:///" + cfg.get_root_dir() + "/blowpipe.db"
    db = model_db.DB(cfg, sqlite_filename)
    db.connect()
    db.reset()
    cfg.save()

    Logger.console("Initialised Blowpipe in " + cfg.get_root_dir())
