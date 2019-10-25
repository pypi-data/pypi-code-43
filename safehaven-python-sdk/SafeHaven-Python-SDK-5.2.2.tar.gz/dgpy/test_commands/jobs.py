#!/usr/bin/python
#
# List up to @max_jobs last jobs.
#
# Usage:
#   $0 [@max_jobs (default: 5)]
#
import sys
import time
from datetime                 import timedelta

from dgpy.cms_client          import CmsClient
from dgpy.job                 import job_status
from dgpy.safehaven.api.types import types_enums_pb2
from dgpy.magicbus.command    import command_enums_pb2

# The default order is in descending order of Job ID - reverse to ascending:
for job in reversed(CmsClient().job_list(max_jobs = 5 if len(sys.argv) == 1 else int(sys.argv[1]))):
    status = job_status(job)
    if status == types_enums_pb2.NOT_STARTED:
        job.annotation = "Job waiting to be run"
    print "#{0.job_id} {1} {0.resource_name}, {2}: {0.annotation}, {3} ({4:.0f} sec)".format(job,
        command_enums_pb2.Cmd.Name(job.command),                               # Symbolic command name
        types_enums_pb2.JobState.Name(status),                                 # Convert enum value to string
        time.strftime("%a %T", time.localtime(job.created.ToSeconds())),       # Job start in local timezone
        (job.updated.ToDatetime() - job.created.ToDatetime()).total_seconds()) # Job duration in seconds
