#!/usr/bin/python
#
# Delete a target VM of a Protection Group.
#
# Usage: $0 <PG-Name> <IQN>, with
#         - @PG-Name: name of the protection group hosting the target
#         - @IQN:     iSCSI IQN of the target to remove
import argparse
from dgpy.cms_client import CmsClient
from dgpy.utils      import die
from dgpy.job        import status_printer
from dgpy.errors     import LegacyMessageError, GrpcError, TimeOutError

parser = argparse.ArgumentParser(description="Delete a target VM of a @DVOL")

parser.add_argument('DVOL',            type=str,              help = 'Name of the Protection Group')
parser.add_argument('IQN',             type=str,              help = 'iSCSI IQN of the target to remove')
parser.add_argument('-w', '--wait',    action='store_true',   help = 'Wait for the job to complete')
parser.add_argument('-t', '--timeout', type=float, default=0, help = 'Optional timeout for the --wait operation in seconds')

args = parser.parse_args()
try:
    client = CmsClient()
    res    = client.dvol_target_delete(args.DVOL, args.IQN)
    if args.wait or args.timeout > 0:
        client.wait_for_job(res.job_id, args.timeout, status_printer)
    else:
        print "Target delete job #{0}".format(res.job_id)
except (LegacyMessageError, GrpcError) as e:
    die("Failed to delete {0} target: {1}".format(args.DVOL, e))
except TimeOutError as e:
    die("Timed out: {}".format(e))
