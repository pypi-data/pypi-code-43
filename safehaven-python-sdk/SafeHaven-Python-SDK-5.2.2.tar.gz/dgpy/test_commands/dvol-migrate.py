#!/usr/bin/python
#
# Migrate a Protection Group (swap master/remote site).
#
# Usage: $0 <PG-Name>  <PrePowerOff: y|n>  <PostPowerOn: y|n>, with
#         - @PG-Name:     name of the PG to migrate
#         - @PrePowerOff: whether to power off the master site before migration
#         - @PostPowerOn: whether to power on the remote site after migration
import argparse
from dgpy.cms_client import CmsClient
from dgpy.utils      import die
from dgpy.job        import status_printer
from dgpy.errors     import LegacyMessageError, GrpcError, TimeOutError

parser = argparse.ArgumentParser(description="Migrate the legacy protection group @DVOL")

parser.add_argument('DVOL',    type=str, help = 'Name of the Protection Group')
parser.add_argument('PRE_OFF', type=bool, help = 'Whether to power off the master site before migration', choices=['yes','no'])
parser.add_argument('POST_ON', type=bool, help = 'Whether to power on the remote site after migration',   choices=['yes','no'])

parser.add_argument('-w', '--wait',    action='store_true',   help = 'Wait for the job to complete')
parser.add_argument('-t', '--timeout', type=float, default=0, help = 'Optional timeout for the --wait operation in seconds')

args = parser.parse_args()
try:
    client = CmsClient()
    res    = client.dvol_migrate(args.DVOL, args.PRE_OFF == 'yes', args.POST_ON == 'yes')
    if args.wait or args.timeout > 0:
        client.wait_for_job(res.job_id, args.timeout, status_printer)
    else:
        print "Migration job #{0}".format(res.job_id)
except (LegacyMessageError, GrpcError) as e:
    die("Failed to migrate {0}: {1}".format(args.DVOL, e))
except TimeOutError as e:
    die("Timed out: {}".format(e))
