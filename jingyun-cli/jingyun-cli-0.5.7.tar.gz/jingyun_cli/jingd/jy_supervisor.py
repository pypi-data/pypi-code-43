#! /usr/bin/env python
# coding: utf-8

import os
import sys
from supervisor.supervisorctl import main as supervisorctl_main
from supervisor.supervisord import main as supervisord_main
from jingyun_cli.util.env import source_local
try:
    from .help import g_help, error_and_exit
except ValueError:
    from help import g_help, error_and_exit

__author__ = '鹛桑够'


def set_conf():
    source_local()
    conf_dir = os.environ.get("JINGD_CONF_DIR")
    if conf_dir is None:
        error_and_exit(g_help("defect_env", "JINGD_CONF_DIR"))
    conf_path = os.path.join(conf_dir, "supervisord.conf")
    if os.path.exists(conf_path) is False:
        error_and_exit(g_help("file_lost"))
    sys.argv.insert(1, "-c")
    sys.argv.insert(2, conf_path)


def jy_supervisorctl():
    set_conf()
    code = supervisorctl_main()
    sys.exit(code)


def jy_supervisord():
    set_conf()
    code = supervisord_main()
    sys.exit(code)


if __name__ == "__main__":
    import sys
    sys.argv.append("status")
    jy_supervisorctl()