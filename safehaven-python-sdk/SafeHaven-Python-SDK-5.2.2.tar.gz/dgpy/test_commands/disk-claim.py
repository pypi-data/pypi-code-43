#!/usr/bin/python
#
# Claim disks to create or add a storage pool on an SRN.
#
import argparse
from dgpy.cms_client import CmsClient
from dgpy.utils      import die
from dgpy.job        import status_printer
from dgpy.errors     import LegacyMessageError, GrpcError, NotFoundError, TimeOutError

parser = argparse.ArgumentParser(description="Add @DISK to LVM storage @POOL on SRN @IP")

parser.add_argument('IP',   type=str, help = 'IP address of the SRN to claim disk on')
parser.add_argument('POOL', type=str, help = 'Storage pool name at @IP')
parser.add_argument('DISK', type=str, help = 'Disk to add to @POOL (format: "/dev/sde")')

parser.add_argument('-w', '--wait',    action='store_true',   help = 'Wait for the job to complete')
parser.add_argument('-t', '--timeout', type=float, default=0, help = 'Optional timeout for the --wait operation in seconds')

args = parser.parse_args()
try:
    client = CmsClient()
    res    = client.disk_claim(args.IP, args.DISK, args.POOL)
    if args.wait or args.timeout > 0:
        client.wait_for_job(res.job_id, args.timeout, status_printer)
    else:
        print "Disk claim Job ID: {}".format(res.job_id)
except (LegacyMessageError, GrpcError) as e:
    die("Failed to claim {1} on {0}: {2}".format(args.IP, args.DISK, e))
except TimeOutError as e:
    die("Timed out: {}".format(e))
