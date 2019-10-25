#!/usr/bin/python
#
# Set the periodic snapshot interval in seconds on the given legacy Protection Group:
# - a value of 0 disables periodic checkpointing,
# - a value > 0 sets the checkpoint interval in units of seconds.
#
# WARNING: this call only works on legacy Protection Groups.
# For non-legacy PGs, use 'pg-checkpoint-config.py' instead.
#
import argparse
from dgpy.cms_client import CmsClient
from dgpy.utils      import die
from dgpy.job        import status_printer
from dgpy.errors     import LegacyMessageError, GrpcError, TimeOutError

parser = argparse.ArgumentParser(description="Set periodic snapshot interval of @DVOL to @PERIOD")

parser.add_argument('DVOL',   type=str, help = 'Name of the Protection Group')
parser.add_argument('PERIOD', type=int, help = 'Snapshot interval in seconds (0: disable periodic snapshots)')
parser.add_argument('-w', '--wait',    action='store_true',   help = 'Wait for the job to complete')
parser.add_argument('-t', '--timeout', type=float, default=0, help = 'Optional timeout for the --wait operation in seconds')

args = parser.parse_args()

try:
    client = CmsClient()
    res    = client.dvol_set_snapshot_period(args.DVOL, args.PERIOD)
    if args.wait or args.timeout > 0:
        client.wait_for_job(res.job_id, args.timeout, status_printer)
    else:
        print "Set snapshot-period job #{0}".format(res.job_id)
except (LegacyMessageError, GrpcError) as e:
    die("Failed to set the snapshot period on {0}: {1}".format(args.DVOL, e))
except TimeOutError as e:
    die("Timed out: {}".format(e))
except Exception as e:
    die("Oops: {}".format(e))
