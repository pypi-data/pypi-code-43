#!/usr/bin/python
#
# Add a new Safehaven Replication Node to a given site.
#
import argparse
from dgpy.cms_client import CmsClient
from dgpy.utils      import die
from dgpy.job        import status_printer
from dgpy.errors     import LegacyMessageError, GrpcError, NotFoundError, TimeOutError

parser = argparse.ArgumentParser(description="Add a new SafeHaven Replication @NODE to a given @SITE")

parser.add_argument('NAME',      type=str,                      help = 'Name to use for the node')
parser.add_argument('SITE',      type=str,                      help = 'Site to add @NAME to')
parser.add_argument('IP',        type=str,                      help = 'Service IP of the node @NAME')
parser.add_argument('ST_IP',     type=str, metavar='ST-IP',     help = 'Storage IP of the node @NAME')
parser.add_argument('LOC_ST_IP', type=str, metavar='LOC-ST-IP', help = 'Local (iSCSI) storage IP of the node @NAME')
parser.add_argument('PORT',      type=int,                      help = 'Port number of the safehaven-service at @IP')
parser.add_argument('PASS',      type=str,                      help = 'Ssh root password at @IP')

parser.add_argument('-w', '--wait',    action='store_true',   help = 'Wait for the job to complete')
parser.add_argument('-t', '--timeout', type=float, default=0, help = 'Optional timeout for the --wait operation in seconds')

args = parser.parse_args()
try:
    client = CmsClient()
    res    = client.node_add(args.NAME, args.SITE, args.IP, args.ST_IP, args.LOC_ST_IP, args.PORT, args.PASS)
    if args.wait or args.timeout > 0:
        client.wait_for_job(res.job_id, args.timeout, status_printer)
    else:
        print "Node registration Job ID: {}".format(res.job_id)
except NotFoundError as e:
    die("No such node: '{0}'".format(args.NODE))
except (LegacyMessageError, GrpcError) as e:
    die("Failed to add '{0}' to site {1}: {2}".format(args.NAME, args.SITE, e))
except TimeOutError as e:
    die("Timed out: {}".format(e))
