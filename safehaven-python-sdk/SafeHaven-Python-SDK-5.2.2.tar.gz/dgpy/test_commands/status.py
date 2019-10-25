#!/usr/bin/python
#
# Print the status of a given job.
#
# Usage:
#   $0 <JobID>
#
import time
import argparse
from datetime                 import timedelta, datetime

from dgpy.cms_client          import CmsClient
from dgpy.job                 import job_status
from dgpy.utils               import die
from dgpy.errors              import GrpcError, NotFoundError
from dgpy.safehaven.api.types import types_enums_pb2
from dgpy.magicbus.command    import command_enums_pb2

parser = argparse.ArgumentParser(description="Print the status of @JobId")
parser.add_argument('JobId',   type=str, help = 'Id of the job to query')

args = parser.parse_args()

try:
    job = CmsClient().job_status(args.JobId)
    status = job_status(job)
    runtime = (job.updated.ToDatetime() - job.created.ToDatetime()).total_seconds()
    if status == types_enums_pb2.INPROGRESS:
        runtime = time.time() - time.mktime(time.localtime(job.created.ToSeconds()))
    for e in (
        ("Command", command_enums_pb2.Cmd.Name(job.command)),
        ("Resource", "{0}.{1}".format(types_enums_pb2.ResourceType.Name(job.resource_type), job.resource_name)),
        ("Status", types_enums_pb2.JobState.Name(status)),
        ("Notes", job.annotation),
        ("Created", "{0} by {1}".format(time.strftime("%T", time.localtime(job.created.ToSeconds())), job.owner)),
        ("Updated", "{0} (runtime {1:.1f}s)".format(time.strftime("%T", time.localtime(job.updated.ToSeconds())), runtime))
    ):
        print "{0:<10} {1}".format(*e)
except NotFoundError as n:
    die("No such job #{}".format(args.JobId))
