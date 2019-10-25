#!/usr/bin/python
#
# Await the completion of a job, given its job ID.
#
# Usage:
#   $0 <JobID>
#
import argparse
from dgpy.cms_client import CmsClient
from dgpy.utils      import die
from dgpy.job        import status_printer
from dgpy.errors     import GrpcError,TimeOutError

parser = argparse.ArgumentParser(description="Await completion of @JobId and print progress (caveat: @JobId must be running)")
parser.add_argument('JobId',           type=int, help = 'Id of the Job to wait for')
parser.add_argument('-t', '--timeout', type=float, default=0, help = 'Wait timeout in (fractional) seconds (0: no timeout)')

args = parser.parse_args()

try:
    CmsClient().wait_for_job(args.JobId, args.timeout, status_printer)
except TimeOutError as e:
    die("Timed out: {}".format(e))
except GrpcError as g:
    die("Failed to await #{0}: {1}".format(args.JobId, g))
