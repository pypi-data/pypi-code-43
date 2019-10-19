#!/usr/bin/env python
"""
cjr_recorder - Class to record job progress, this class is main interface to the library.
"""
# This file is part of 'compute_job_recorder'
# A library for recording compute job progress.
#
# Copyright 2019 Pete Bunting
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Purpose: class to record job progress, this class is main interface to the library.
#
# Author: Pete Bunting
# Email: pfb@aber.ac.uk
# Date: 08/02/2019
# Version: 1.0
#
# History:
# Version 1.0 - Created.

from enum import Enum
import datetime
import copy
from cjrlib.cjr_db_connection import CJRDBConnection, CJRJobName, CJRTaskInfo

class JobStatus(Enum):
    START = 1
    FINISH = 2
    UPDATE = 3


def record_task_status(status, job_name, task_id, version, task_info, print_progress=False):
    """
    Generic function to record the status of a job to the database.

    :param status: A JobStatus value specifying whether this is recording start, finish or just an intermediate update
                   to the job.
    :param job_name: The name of the job. This could be shared between a number of tasks.
    :param task_id: This is unique name for the task within the job - the combination of the job name and task ID need
                    to be unique.
    :param job_info: A dictionary of information which is to be stored for the task. When the status is START then this
                     is expected to be the parameters for running the task.
    :param print_progress: a boolean to specify whether an feedback should be printed to the console (Default: False)

    """
    cjrdb_conn = CJRDBConnection()
    if cjrdb_conn is None:
        raise Exception("Could not create the connection object...")
    cjrdb_conn.create_db_tables()

    if status == JobStatus.START:
        record_task_start(job_name, task_id, version, task_info, cjrdb_conn, print_progress)
    elif status == JobStatus.FINISH:
        record_task_finish(job_name, task_id, version, task_info, cjrdb_conn, print_progress)
    elif status == JobStatus.UPDATE:
        record_task_update(job_name, task_id, version, task_info, cjrdb_conn, print_progress)
    else:
        raise Exception("Do not recognise the status inputted.")


def record_task_start(job_name, task_id, version, task_info, cjrdb_conn, print_progress=False):
    """
    A function to record the start of a task within a job.

    :param job_name: The name of the job. This could be shared between a number of tasks.
    :param task_id: This is unique name for the task within the job - the combination of the job name and task ID need
                    to be unique.
    :param job_info: A dictionary of information which is to be stored for the task. This is expected to be the
    parameters for running the task.
    :param cjrdb_conn: a CJRDBConnection object for interfacing to the database.
    :param print_progress: a boolean to specify whether an feedback should be printed to the console (Default: False)

    """
    if print_progress:
        print("Start Job...")
    db_ses_obj = cjrdb_conn.get_db_session()

    qury_rslt = db_ses_obj.query(CJRJobName).filter(CJRJobName.JobName == job_name).one_or_none()
    if qury_rslt is None:
        db_ses_obj.add(CJRJobName(JobName=job_name))

    qury_rslt = db_ses_obj.query(CJRTaskInfo).filter(CJRTaskInfo.JobName == job_name).\
                                              filter(CJRTaskInfo.TaskID == task_id).\
                                              filter(CJRTaskInfo.Version == version).one_or_none()

    if qury_rslt is None:
        start_time = datetime.datetime.now()
        db_ses_obj.add(CJRTaskInfo(TaskID=task_id,  JobName=job_name, Version=version,
                                   StartTime=start_time, TaskParams=task_info))
    else:
        db_ses_obj.commit()
        db_ses_obj.close()
        raise Exception("The task '{} - {} v{}' have already been started - change the task ID or version.".\
                        format(job_name, task_id, version))

    db_ses_obj.commit()
    db_ses_obj.close()


def record_task_finish(job_name, task_id, version, task_info, cjrdb_conn, print_progress=False):
    """
    A function to record the end of a task within a job.

    :param job_name: The name of the job. This could be shared between a number of tasks.
    :param task_id: This is unique name for the task within the job - the combination of the job name and task ID need
                    to be unique.
    :param job_info: A dictionary of information which is to be stored at the end of the task.
    :param cjrdb_conn: a CJRDBConnection object for interfacing to the database.
    :param print_progress: a boolean to specify whether an feedback should be printed to the console (Default: False)

    """
    if print_progress:
        print("Finish Job...")
    db_ses_obj = cjrdb_conn.get_db_session()

    qury_rslt = db_ses_obj.query(CJRTaskInfo).filter(CJRTaskInfo.JobName == job_name). \
        filter(CJRTaskInfo.TaskID == task_id). \
        filter(CJRTaskInfo.Version == version).one_or_none()

    if qury_rslt is not None:
        qury_rslt.EndTime = datetime.datetime.now()
        qury_rslt.TaskEndInfo = task_info
        qury_rslt.TaskCompleted = True
    else:
        db_ses_obj.close()
        raise Exception("The task '{} - {} v{}' could not be found - check inputs.". \
                        format(job_name, task_id, version))

    db_ses_obj.commit()
    db_ses_obj.close()


def record_task_update(job_name, task_id, version, task_info, cjrdb_conn, print_progress=False):
    """
    A function to record the end of a task within a job.

    :param job_name: The name of the job. This could be shared between a number of tasks.
    :param task_id: This is unique name for the task within the job - the combination of the job name and task ID need
                    to be unique.
    :param job_info: A dictionary of information which is to be stored for the task.
    :param cjrdb_conn: a CJRDBConnection object for interfacing to the database.
    :param print_progress: a boolean to specify whether an feedback should be printed to the console (Default: False)

    """
    if print_progress:
        print("Update Job...")
    db_ses_obj = cjrdb_conn.get_db_session()

    qury_rslt = db_ses_obj.query(CJRTaskInfo).filter(CJRTaskInfo.JobName == job_name). \
        filter(CJRTaskInfo.TaskID == task_id). \
        filter(CJRTaskInfo.Version == version).one_or_none()

    if qury_rslt is not None:
        if qury_rslt.TaskCompleted:
            db_ses_obj.close()
            raise Exception("The task '{} - {} v{}' has already been finished - check inputs.". \
                        format(job_name, task_id, version))

        update_time = datetime.datetime.now()
        task_updates_info = qury_rslt.TaskUpdates
        if task_updates_info is None:
            lcl_task_updates_info = dict()
        else:
            lcl_task_updates_info = copy.deepcopy(task_updates_info)
        lcl_task_updates_info[update_time.isoformat()] = task_info
        qury_rslt.TaskUpdates = lcl_task_updates_info
    else:
        db_ses_obj.close()
        raise Exception("The task '{} - {} v{}' could not be found - check inputs.". \
                        format(job_name, task_id, version))

    db_ses_obj.commit()
    db_ses_obj.close()

