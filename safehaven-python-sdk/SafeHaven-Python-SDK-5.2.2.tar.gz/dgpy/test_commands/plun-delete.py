#!/usr/bin/python
#
# Delete a disk (PLUN) from the target (VM) of a Protection Group (PG).
#
# Usage: $0 <Disk-Name> <PG-Name> <VM-Name>, with
#         - @Disk-Name: name of the disk to remove, e.g. "disk-0"
#         - @PG-Name:   name of the PG to which @Disk-Name belongs
#         - @VM-Name:   name of the VM to which @Disk-Name belongs
import argparse
from dgpy.cms_client import CmsClient
from dgpy.utils      import die
from dgpy.job        import status_printer
from dgpy.errors     import LegacyMessageError, GrpcError, TimeOutError

parser = argparse.ArgumentParser(description="Delete a @DISK from the @VM of a protection group @DVOL")

parser.add_argument('DVOL',            type=str,              help = 'Name of the Protection Group')
parser.add_argument('VM',              type=str,              help = 'Name of the VM to which @DISK belongs')
parser.add_argument('DISK',            type=str,              help = 'Name of the disk to remove (e.g. "disk-0")')

parser.add_argument('-w', '--wait',    action='store_true',   help = 'Wait for the job to complete')
parser.add_argument('-t', '--timeout', type=float, default=0, help = 'Optional timeout for the --wait operation in seconds')

args = parser.parse_args()
try:
    client = CmsClient()
    res    = client.dvol_plun_delete(args.DISK, args.DVOL, args.VM)
    if args.wait or args.timeout > 0:
        client.wait_for_job(res.job_id, args.timeout, status_printer)
    else:
        print "PLUN delete job #{0}".format(res.job_id)
except (LegacyMessageError, GrpcError) as e:
    die("Failed to delete {0} PLUN: {1}".format(args.DISK, e))
except TimeOutError as e:
    die("Timed out: {}".format(e))
