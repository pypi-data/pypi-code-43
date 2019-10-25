#!/usr/bin/python
#
# Add a new peer into the peer list of a given SRN.
#
import argparse
from dgpy.cms_client import CmsClient
from dgpy.utils      import die
from dgpy.job        import status_printer
from dgpy.errors     import LegacyMessageError, GrpcError, NotFoundError, TimeOutError

parser = argparse.ArgumentParser(description="Register replication nodes @IP1 and @IP2 as mutual peers")

parser.add_argument('IP1',   type=str, help = 'IP address of the first SRN to peer')
parser.add_argument('IP2',   type=str, help = 'IP address of the peer of SRN @IP1')
parser.add_argument('PASS1', type=str, help = 'Ssh root password at @IP1')
parser.add_argument('PASS2', type=str, help = 'Ssh root password at @IP2')

parser.add_argument('-w', '--wait',    action='store_true',   help = 'Wait for the job to complete')
parser.add_argument('-t', '--timeout', type=float, default=0, help = 'Optional timeout for the --wait operation in seconds')

args = parser.parse_args()
try:
    client = CmsClient()
    res    = client.peer_add(args.IP1, args.IP2, args.PASS1, args.PASS2)
    if args.wait or args.timeout > 0:
        client.wait_for_job(res.job_id, args.timeout, status_printer)
    else:
        print "Peer registration Job ID: {}".format(res.job_id)
except (LegacyMessageError, GrpcError) as e:
    die("Failed to add {1} into the peer list of {0}: {2}".format(args.IP1, args.IP2, e))
except TimeOutError as e:
    die("Timed out: {}".format(e))
