#!/usr/bin/python
#
# Subscribe to streaming job events, printing them out as they come in.
#
#
import sys
import time
import grpc
import threading
from datetime                 import timedelta
from dgpy.errors              import GrpcError
from dgpy.cms_client          import CmsClient
from dgpy.job                 import job_status
from dgpy.safehaven.api.types import types_enums_pb2
from dgpy.magicbus.command    import command_enums_pb2

try:
    for jobEvent in CmsClient().job_events():
        job = jobEvent.job
        status = job_status(job)
        if status == types_enums_pb2.NOT_STARTED:
            job.annotation = "Job waiting to be run"
        if jobEvent.is_new_job:
            job.annotation += " (new job)"
        elif status != types_enums_pb2.NOT_STARTED: # Job running time in seconds
            job.annotation += " ({0:.1f} sec)".format((job.updated.ToDatetime() - job.created.ToDatetime()).total_seconds())
        print "{3} #{0.job_id} {1} {0.resource_name}, {2:<12} {0.annotation}".format(job,
            command_enums_pb2.Cmd.Name(job.command),                      # Symbolic command name
            types_enums_pb2.JobState.Name(status) + ':',                  # Convert enum value to string
            time.strftime("%T", time.localtime(job.created.ToSeconds())), # Job start in local timezone
        )
except KeyboardInterrupt:
    # NOTE: keyboard interrupts are not always instantly caught. One reason is that the job_events() API call
    #       is only evaluated when the iteration starts. The other seems to be that the cython code queues up
    #       signals (CTRL-C being SIGINT) rather than handling them immediately. Hence the 'Exiting' printout
    #       may appear to be late.
    print "Exiting."
