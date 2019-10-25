# -*- coding: utf-8 -*-
"""
   Helper functions that have to do with jobs.
"""
import sys
import grpc
import grpc._channel
import time
import datetime
from threading                import Timer

from dgpy.errors              import TimeOutError, GrpcError
from dgpy.safehaven.api.types import types_enums_pb2
from dgpy.magicbus.command    import command_enums_pb2

def job_status(job):
    """Determine the overall job status from the status of its stages.
       @job: a safehaven.jobsystem.jobsystem_pb2.Job instance
    """
    # Meaning of states:
    # - NOT_STARTED means stage has not been entered yet,
    # - INPROGRESS means stage is currently progressing,
    # - SKIPPED means stage was skipped over,
    # - SUCCESS/ERROR mean stage completed (in)successfully,
    # - STAGE_FAILED means the stage failed, but it does not affect the outcome of the job,
    # - UNKNOWN is set externally, it means the stage did not complete or aborted (e.g. crash).
    if len(job.stages) > 0:
        states = set(stage.status for stage in job.stages)
        if len(states) == 1:
            return states.pop()
        elif states.issubset(set([types_enums_pb2.SKIPPED, types_enums_pb2.STAGE_FAILED])):
            return types_enums_pb2.SKIPPED
        elif states.issubset(set([types_enums_pb2.SKIPPED, types_enums_pb2.STAGE_FAILED, types_enums_pb2.SUCCESS])):
            return types_enums_pb2.SUCCESS
        elif types_enums_pb2.ERROR in states:
            return types_enums_pb2.ERROR
        elif types_enums_pb2.UNKNOWN in states:
            return types_enums_pb2.UNKNOWN
        elif states.intersection(set([types_enums_pb2.INPROGRESS, types_enums_pb2.NOT_STARTED])):
            return types_enums_pb2.INPROGRESS
    return types_enums_pb2.UNKNOWN


def is_final_status(status):
    """Return True if @status (a types_enums_pb2.JobState) is a no-longer-running job state."""
    return status not in (types_enums_pb2.NOT_STARTED, types_enums_pb2.INPROGRESS)


def job_is_done(job):
    """Return True if @job (a safehaven.jobsystem.jobsystem_pb2.Job) is done."""
    return is_final_status(job_status(job))


def status_printer(job):
    """Callback for CmsClient.wait_for_job which prints each of the @job events until completion."""
    status = job_status(job)
    if status == types_enums_pb2.NOT_STARTED:
        job.annotation = "Job waiting to be run"
    runningTime = job.updated.ToDatetime() - job.created.ToDatetime()
    print "{3} #{0.job_id} {1} {0.resource_name}, {2:<12} {0.annotation}".format(job,
        command_enums_pb2.Cmd.Name(job.command),                      # Symbolic command name
        types_enums_pb2.JobState.Name(status) + ':',                  # Convert enum value to string
        (datetime.datetime.min + runningTime).time(),                 # Total running time so far
    )
    return is_final_status(status)
