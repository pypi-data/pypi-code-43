#!/usr/bin/python
#
# Create a non-legacy PG from a .yaml or .json input file.
#
# There are too many parameters for a command-line application.
import os
import argparse
from dgpy.cms_client      import CmsClient
from dgpy.aggregates.dvol import dvol_pb2
from dgpy.utils           import die, fatal, load_protobuf
from dgpy.job             import status_printer
from dgpy.errors          import GrpcError, NotFoundError, TimeOutError

parser = argparse.ArgumentParser(description="Create a non-legacy PG from a .yaml or .json input file")

parser.add_argument('FILE', type=argparse.FileType('r'),      help = 'Path to the JSON or YAML parameter file')
parser.add_argument('-w', '--wait',    action='store_true',   help = 'Wait for the job to complete')
parser.add_argument('-t', '--timeout', type=float, default=0, help = 'Optional timeout for the --wait operation in seconds')

args = parser.parse_args()
try:
    client = CmsClient()
    req    = load_protobuf(args.FILE.name, dvol_pb2.PgCreateRequest())
    res    = client.pg_create(req)
    if args.wait or args.timeout > 0:
        client.wait_for_job(res.job_id, args.timeout, status_printer)
    else:
        print "Create {0.name} Job ID: {1}".format(req, res.job_id)
except NotFoundError as e:
    die("No such PG: '{0}'".format(args.PG))
except GrpcError as e:
    die("Failed to create {0.name}: {1}".format(req, e))
except TimeOutError as e:
    die("Timed out: {}".format(e))
