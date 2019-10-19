#!python
"""
compute_job_recorder - Command to record the status of a compute job.
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
# Purpose:  Command line tool for running the system.
#
# Author: Pete Bunting
# Email: pfb@aber.ac.uk
# Date: 08/02/2019
# Version: 1.0
#
# History:
# Version 1.0 - Created.

import argparse
import json
import cjrlib.cjr_recorder

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--status", type=str, required=True, default=None,
                        choices=["START", "UPDATE", "FINISH"], help="Specify the job status.")
    parser.add_argument("-j", "--jobname", type=str, required=True,
                        help="Specify the job name, a generic name for a group of jobs.")
    parser.add_argument("-t", "--taskid", type=str, required=True,
                        help="Specify a job ID, unique within the 'jobname'.")
    parser.add_argument("-v", "--version", type=int, default=0, required=False,
                        help="Specify the version of the job and task.")
    parser.add_argument("-i", "--taskinfo", type=str, required=True,
                        help='''Specify the status info, this is stored in JSON and should be provided in that format:
                                * START - input parameters, helpful to include enough information to re-run the job.
                                * UPDATE - any information on job progress.
                                * FINISH - information on completion.
                             ''')
    parser.add_argument("--printprogress", action='store_true', default=False,
                        help="Specify that progress statements should be printed to the console - "
                             "useful for debugging.")

    args = parser.parse_args()

    if args.status == "START":
        status = cjrlib.cjr_recorder.JobStatus.START
    elif args.status == "FINISH":
        status = cjrlib.cjr_recorder.JobStatus.FINISH
    elif args.status == "UPDATE":
        status = cjrlib.cjr_recorder.JobStatus.UPDATE
    else:
        raise Exception("Status provided was not recognised.")

    # Parse the
    task_info_str = args.taskinfo
    task_info_dict = json.loads(task_info_str)

    cjrlib.cjr_recorder.record_task_status(status, args.jobname, args.taskid, args.version,
                                           task_info_dict, args.printprogress)
