#!/usr/bin/python
#
# Create a legacy PG from a parameter text file.
#
# The file contains each of the individual CREATE_DVOL parameters.
# If a parameter contains spaces, it must be enclosed in quotes.
# The file can optionally contain 'dvol-create' as first parameter.
#
# See below and the 'example_configurations' folder for examples.
import os
import shlex
import argparse
from dgpy.cms_client import CmsClient
from dgpy.utils      import die, fatal
from dgpy.job        import status_printer
from dgpy.errors     import LegacyMessageError, GrpcError, TimeOutError

parser = argparse.ArgumentParser(description="Create a legacy DVOL from a .console @FILE")

parser.add_argument('FILE', type=argparse.FileType('r'),      help = 'Path to the .console file')
parser.add_argument('-w', '--wait',    action='store_true',   help = 'Wait for the job to complete')
parser.add_argument('-t', '--timeout', type=float, default=0, help = 'Optional timeout for the --wait operation in seconds')

args = parser.parse_args()

try:
    params = shlex.split(args.FILE.read())
    if 'dvol-create' in params:
        params = params[1:]

    client = CmsClient()
    res    = client.dvol_create(params)
    if args.wait or args.timeout > 0:
        client.wait_for_job(res.job_id, args.timeout, status_printer)
    else:
        print "Create-DVOL job #{0}".format(res.job_id)
except (LegacyMessageError, GrpcError) as e:
    die("Failed to create PG: {0}".format(e))
except TimeOutError as e:
    die("Timed out: {}".format(e))
except Exception as e:
    die("Oops: {}".format(e))

#
#  APPENDIX: sample '.console' file contents (split into multiple lines):
#
#  dvol-create CA2GRRTAWS-RH02-PG COW 17.0G 1048576 4352.0M             \
#	4352.0M 0 10.55.220.131 10.55.220.131 pool pool 10.55.220.229       \
#	10.55.220.229 pool pool CLC CLC false false <none> <none>           \
#	"<none>|<none>|CA2GRRTAWS-RH02|LINUX|Red Hat Enterprise Linux 6     \
#	(64-bit)|<none>|<none>|RSYNC|disk-0,18253611008,CA2GRRTAWS-RH02"    \
#	false  ""  ""  ""  ""  ""  ""  ""  "" Trlabs1!  ""  ""              \
#	""  ""  "CA2GRRTAWS-RH02,0,POWER_ON,30,0,SHUTDOWN,0,RHEL 6          \
#	guest VM,10.55.220.122,<none>,<none>,CA2GRRTAWS-RH02" <none>        \
#	"CA2GRRTAWS-RH02,0,POWER_ON,30,0,SHUTDOWN,0,RHEL 6 guest            \
#	VM,10.55.220.122,<none>,<none>,CA2GRRTAWS-RH02" <none>
