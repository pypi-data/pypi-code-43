# -*- coding: utf-8 -*-
from datetime import datetime
import os
import threading
import tarfile
import shutil
import getpass

from .process import process_log
from .system import system_log
from .user_log import user_log_collector


def log_aggregator(filename):

    robot_uuid = getpass.getuser() + '@' + os.uname()[1]
    home_path = os.environ['HOME']

    if filename:
        working_folder = filename
    else:
        working_folder = robot_uuid + '_' + datetime.now().strftime("%Y%m%d%H%M%S")

    log_folder = os.path.join(home_path, working_folder)
    os.makedirs(log_folder)

    process_thread = threading.Thread(target=process_log, args=(log_folder, ))
    system_thread = threading.Thread(target=system_log, args=(log_folder, ))
    user_log_collector_thread = threading.Thread(target=user_log_collector, args=(log_folder, ))

    process_thread.start()
    system_thread.start()
    user_log_collector_thread.start()

    process_thread.join()
    system_thread.join()
    user_log_collector_thread.join()

    # tar_ball
    os.chdir(home_path)
    with tarfile.open(log_folder + '.tar.gz', "w:gz") as tar_handle:
        tar_handle.add(working_folder)

    tar_handle.close()

    # delete folder
    shutil.rmtree(log_folder)
