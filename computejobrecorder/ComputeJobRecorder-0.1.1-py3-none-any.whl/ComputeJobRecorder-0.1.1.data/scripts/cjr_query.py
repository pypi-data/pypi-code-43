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
# Date: 28/07/2019
# Version: 1.0
#
# History:
# Version 1.0 - Created.

import argparse
import pprint
import cjrlib.cjr_queries

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-q", "--query", type=str, required=True, default=None,
                        choices=["JOBS", "ALLTASKS", "INCOMPLETE", "TASK"], help="Specify the query to be made.")
    parser.add_argument("-j", "--jobname", type=str, required=False, default=None,
                        help="Specify the job name, a generic name for a group of jobs.")
    parser.add_argument("-t", "--taskid", type=str, required=False, default=None,
                        help="Specify a job ID, unique within the 'jobname'.")
    parser.add_argument("-v", "--version", type=int, default=0, required=False,
                        help="Specify the version of the job and task.")
    parser.add_argument("--queryhelp", action='store_true', default=False,
                        help="Get help for the command, if specify a query then help for that query will be printed.")

    args = parser.parse_args()

    if args.queryhelp:
        if args.query == "JOBS":
            print("Prints a list of job names.")
            print("\tDoes not require any inputs.")
        elif args.query == "ALLTASKS":
            print("Prints all tasks associated with a job name and version")
            print("\tProvide:")
            print("\t\t --jobname <string>")
            print("\t\t --version <integer>")
        elif args.query == "INCOMPLETE":
            print("Prints all uncompleted tasks associated with a job name and version")
            print("\tProvide:")
            print("\t\t --jobname <string>")
            print("\t\t --version <integer>")
        elif args.query == "TASK":
            print("Prints tasks associated with a job name and task ID")
            print("\tProvide:")
            print("\t\t --jobname <string>")
            print("\t\t --taskid <string>")
            print("\t\t --version <integer>")
        else:
            raise Exception("Query type provided was not recognised.")
    else:
        if args.query == "JOBS":
            job_names = cjrlib.cjr_queries.query_job_names()
            i = 0
            for job_name in job_names:
                print("{}: {}".format(i, job_name))
                i = i + 1
        elif args.query == "ALLTASKS":
            tasks_dict = cjrlib.cjr_queries.get_all_tasks(args.jobname, args.version, datetimeobjs=True)
            for task in tasks_dict:
                pprint.pprint(task)
        elif args.query == "INCOMPLETE":
            tasks_dict = cjrlib.cjr_queries.get_uncompleted_tasks(args.jobname, args.version, datetimeobjs=True)
            for task in tasks_dict:
                pprint.pprint(task)
        elif args.query == "TASK":
            task_dict = cjrlib.cjr_queries.get_task(args.jobname, args.taskid, args.version, datetimeobjs=True)
            pprint.pprint(task_dict)
        else:
            raise Exception("Query type provided was not recognised.")


