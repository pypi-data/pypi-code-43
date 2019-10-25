#!/usr/bin/python
#
# Create a temporary test-failover recovery image from a checkpoint.
#
# Usage: $0 <PG-Name> <SnapId> <TempSize> <PowerOn> <IsolateNet>, with
#         - @PG-Name:    protection group to perform test-failover on
#         - @SnapId:     hex snapshot ID to generate temporary TFO image from
#         - @TempSize:   temporary write-space size (multiple of 512 with units, e.g. 1G; use 0 for automatic calculation)
#         - @PowerOn:    whether to power on the remote site after creating the image
#         - @IsolateNet: whether to isolate the DR network on start-up
import argparse
import math
from dgpy.cms_client import CmsClient
from dgpy.utils      import die
from dgpy.job        import status_printer
from dgpy.utils      import fatal, lvm_size, to_lvm_size
from dgpy.errors     import LegacyMessageError, GrpcError, TimeOutError

def _calculate_snap_size(client, dvolName, snapId):
    """Retrieve the size of the @dvolName snapshot with ID @snapId and add margin for use in TFO.
    @client:   authenticated CMS client
    @dvolName: name of the DVOL
    @snapId:   hex snapshot ID
    """
    try:
        for s in client.dvol_list_snapshots(dvolName, remote=True):
            if s['id'] == snapId:
                # Add at least 5GB of extra scratch space: Win08 (updates) can take 5..10GB
                return to_lvm_size(math.ceil(lvm_size(s['size']) + (5 <<30)))
        fatal("No such {0} snapshot '{1}' on the remote site".format(dvolName, snapId))
    except LegacyMessageError as e:
        fatal("Failed to list {0} snapshots: {1}".format(dvolName, e))

# SCRIPT PROPER
parser = argparse.ArgumentParser(description="Create a temporary test-failover recovery image of @DVOL")

parser.add_argument('DVOL',                       type=str, help = 'Name of the Protection Group')
parser.add_argument('SNAP_ID', metavar='SNAP-ID', type=str, help = 'Snapshot ID to use for the test-failover')
parser.add_argument('-s', '--size',               type=int, help = 'Size of the temporary write space (leave blank or 0 for automatic calculation')
parser.add_argument('-o', '--power-on', action='store_true', help = 'Whether to power on the remote site after creating the image')
parser.add_argument('-i', '--isolate',  action='store_true', help = 'Whether to isolate the DR network on start-up')

parser.add_argument('-w', '--wait',    action='store_true',   help = 'Wait for the job to complete')
parser.add_argument('-t', '--timeout', type=float, default=0, help = 'Optional timeout for the --wait operation in seconds')

args = parser.parse_args()
try:
    client = CmsClient()
    temp_size = args.size
    if not args.size:
        temp_size = _calculate_snap_size(client, args.DVOL, args.SNAP_ID)
    res = client.dvol_test_failover(args.DVOL, args.SNAP_ID, temp_size, args.power_on, args.isolate)
    if args.wait or args.timeout > 0:
        client.wait_for_job(res.job_id, args.timeout, status_printer)
    else:
        print "Dvol test-failover job #{0}".format(res.job_id)
except (LegacyMessageError, GrpcError) as e:
    die("Failed to set up {0} test-failover: {1}".format(args.DVOL, e))
except TimeOutError as e:
    die("Timed out: {}".format(e))
