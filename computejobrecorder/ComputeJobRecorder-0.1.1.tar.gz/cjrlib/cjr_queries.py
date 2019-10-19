#!/usr/bin/env python
"""
cjr_queries - Class to query job progress database.
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
# Date: 28/07/2019
# Version: 1.0
#
# History:
# Version 1.0 - Created.

import sqlalchemy
from cjrlib.cjr_db_connection import CJRDBConnection, CJRJobName, CJRTaskInfo, task_to_dict


def query_job_names(cjr_db_file=None):
    """
    A function to retrieve a list of job names within the database.

    :return: list of strings.

    """
    if cjr_db_file is None:
        cjrdb_conn = CJRDBConnection()
        if cjrdb_conn is None:
            raise Exception("Could not create the connection object...")
        db_ses_obj = cjrdb_conn.get_db_session()
    else:
        db_engine = sqlalchemy.create_engine(cjr_db_file)
        ses_sqlalc = sqlalchemy.orm.sessionmaker(bind=db_engine)
        db_ses_obj = ses_sqlalc()

    job_names = list()
    qury_rslt = db_ses_obj.query(CJRJobName).all()
    if qury_rslt is not None:
        for job_name_rcd in qury_rslt:
            job_names.append(job_name_rcd.JobName)
    db_ses_obj.close()

    return job_names

def get_job_versions(job_name, cjr_db_file=None):
    """
    A function which retrieves the list of versions available for a job.
    :param job_name: the name of the job
    :return: list of integers
    """
    if cjr_db_file is None:
        cjrdb_conn = CJRDBConnection()
        if cjrdb_conn is None:
            raise Exception("Could not create the connection object...")
        db_ses_obj = cjrdb_conn.get_db_session()
    else:
        db_engine = sqlalchemy.create_engine(cjr_db_file)
        ses_sqlalc = sqlalchemy.orm.sessionmaker(bind=db_engine)
        db_ses_obj = ses_sqlalc()

    versions_lst = list()
    qury_rslt = db_ses_obj.query(CJRTaskInfo.Version).filter(CJRTaskInfo.JobName == job_name).distinct().all()
    if qury_rslt is not None:
        for version_rcd in qury_rslt:
            versions_lst.append(version_rcd.Version)
    db_ses_obj.close()

    return versions_lst


def get_all_tasks(job_name, version, datetimeobjs=False, cjr_db_file=None):
    """
    A function which retrieves all the tasks associated with a job and version

    :param job_name: a string for the name of the job
    :param version: an integer for the version of the task.

    :return: returns a list of dictionaries of the tasks
    """
    if cjr_db_file is None:
        cjrdb_conn = CJRDBConnection()
        if cjrdb_conn is None:
            raise Exception("Could not create the connection object...")
        db_ses_obj = cjrdb_conn.get_db_session()
    else:
        db_engine = sqlalchemy.create_engine(cjr_db_file)
        ses_sqlalc = sqlalchemy.orm.sessionmaker(bind=db_engine)
        db_ses_obj = ses_sqlalc()

    task_lst = list()
    qury_rslt = db_ses_obj.query(CJRTaskInfo).filter(CJRTaskInfo.JobName == job_name,
                                                     CJRTaskInfo.Version == version).all()
    if qury_rslt is not None:
        for task_rcd in qury_rslt:
            task_lst.append(task_to_dict(task_rcd, datetimeobjs))
    db_ses_obj.close()

    return task_lst


def get_uncompleted_tasks(job_name, version, datetimeobjs=False, cjr_db_file=None):
    """
    A function which retrieves the uncompleted tasks associated with a job and version

    :param job_name: a string for the name of the job
    :param version: an integer for the version of the task.

    :return: returns a list of dictionaries of the tasks
    """
    if cjr_db_file is None:
        cjrdb_conn = CJRDBConnection()
        if cjrdb_conn is None:
            raise Exception("Could not create the connection object...")
        db_ses_obj = cjrdb_conn.get_db_session()
    else:
        db_engine = sqlalchemy.create_engine(cjr_db_file)
        ses_sqlalc = sqlalchemy.orm.sessionmaker(bind=db_engine)
        db_ses_obj = ses_sqlalc()

    task_lst = list()
    qury_rslt = db_ses_obj.query(CJRTaskInfo).filter(CJRTaskInfo.JobName == job_name,
                                                     CJRTaskInfo.Version == version,
                                                     CJRTaskInfo.TaskCompleted == False).all()
    if qury_rslt is not None:
        for task_rcd in qury_rslt:
            task_lst.append(task_to_dict(task_rcd, datetimeobjs))
    db_ses_obj.close()

    return task_lst


def get_task(job_name, task_id, version, datetimeobjs=False, cjr_db_file=None):
    """
    A function which retrieves the tasks associated with a job name and ID.

    :param job_name: a string for the name of the job
    :param task_id: n string for the task ID.
    :param version: an integer for the version of the task.

    :return: returns a dictionary of the task or None if not task not present
    """
    if cjr_db_file is None:
        cjrdb_conn = CJRDBConnection()
        if cjrdb_conn is None:
            raise Exception("Could not create the connection object...")
        db_ses_obj = cjrdb_conn.get_db_session()
    else:
        db_engine = sqlalchemy.create_engine(cjr_db_file)
        ses_sqlalc = sqlalchemy.orm.sessionmaker(bind=db_engine)
        db_ses_obj = ses_sqlalc()

    task_lst = list()
    qury_rslt = db_ses_obj.query(CJRTaskInfo).filter(CJRTaskInfo.JobName == job_name,
                                                     CJRTaskInfo.TaskID == task_id,
                                                     CJRTaskInfo.Version == version).one_or_none()
    task = None
    if qury_rslt is not None:
        task = task_to_dict(qury_rslt, datetimeobjs)
    db_ses_obj.close()

    return task
