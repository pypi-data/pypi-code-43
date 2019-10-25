#!/usr/bin/python
#
# (Re)starts the safehaven-service on the given SRN.
#
import argparse
from dgpy.cms_client import CmsClient
from dgpy.utils      import die
from dgpy.job        import status_printer
from dgpy.errors     import LegacyMessageError, TimeOutError

parser = argparse.ArgumentParser(description="(Re)start the safehaven-service on @SRN-IP")

parser.add_argument('SRN_IP', metavar='SRN-IP', type=str,     help = 'Ip address of the SRN node to restart')
parser.add_argument('-w', '--wait',    action='store_true',   help = 'Wait for the job to complete')
parser.add_argument('-t', '--timeout', type=float, default=0, help = 'Optional timeout for the --wait operation in seconds')

args = parser.parse_args()

try:
    client = CmsClient()
    res    = client.service_start(args.SRN_IP)
    if args.wait or args.timeout > 0:
        client.wait_for_job(res.job_id, args.timeout, status_printer)
    else:
        print "Restart SRN {0} safehaven-service job #{1}".format(args.SRN_IP, res.job_id)
except LegacyMessageError as e:
    die("Failed to start the service on {0}: {1}".format(args.SRN_IP, e))
except TimeOutError as e:
    die("Timed out: {}".format(e))
except Exception as e:
    die("Oops: {}".format(e))
