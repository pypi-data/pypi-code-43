#!/usr/bin/python
#
# Unclaim disks from a storage pool on an SRN.
#
import argparse
from dgpy.cms_client import CmsClient
from dgpy.utils      import die
from dgpy.job        import status_printer
from dgpy.errors     import LegacyMessageError, GrpcError, NotFoundError, TimeOutError

parser = argparse.ArgumentParser(description="Un-claim @DISK(s) from the LVM storage @POOL at the SRN @IP")

parser.add_argument('IP',   type=str,            help = 'IP address of the SRN to un-claim disks on')
parser.add_argument('POOL', type=str,            help = 'Storage pool name at @IP')
parser.add_argument('DISK', type=str, nargs='+', help = 'Disk(s) to release from @POOL (format: "/dev/sdd")')

parser.add_argument('-w', '--wait',    action='store_true',   help = 'Wait for the job to complete')
parser.add_argument('-t', '--timeout', type=float, default=0, help = 'Optional timeout for the --wait operation in seconds')

args = parser.parse_args()
try:
    client = CmsClient()
    res    = client.disk_unclaim(args.IP, '+'.join(args.DISK), args.POOL)
    if args.wait or args.timeout > 0:
        client.wait_for_job(res.job_id, args.timeout, status_printer)
    else:
        print "Disk release Job ID: {}".format(res.job_id)
except (LegacyMessageError, GrpcError) as e:
    die("Failed to release {1} on {0}: {2}".format(args.IP, " and ".join(args.DISK), e))
except TimeOutError as e:
    die("Timed out: {}".format(e))
