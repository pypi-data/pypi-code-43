#!/usr/bin/python
#
# Install a new Cluster License Key on the CMS.
#
import argparse
from dgpy.cms_client import CmsClient
from dgpy.utils      import die
from dgpy.job        import status_printer
from dgpy.errors     import LegacyMessageError, TimeOutError

parser = argparse.ArgumentParser(description="Add or replace the Cluster Licence @KEY")

parser.add_argument('KEY', type=str,                          help = 'Licence key to add or replace')
parser.add_argument('-w', '--wait',    action='store_true',   help = 'Wait for the job to complete')
parser.add_argument('-t', '--timeout', type=float, default=0, help = 'Optional timeout for the --wait operation in seconds')

args = parser.parse_args()

try:
    client = CmsClient()
    res    = client.license_add(args.KEY)
    if args.wait or args.timeout > 0:
        client.wait_for_job(res.job_id, args.timeout, status_printer)
    else:
        print "Add licence-key job #{0}".format(res.job_id)
except LegacyMessageError as e:
    die("Failed to add licence key: {0}".format(e))
except TimeOutError as e:
    die("Timed out: {}".format(e))
except Exception as e:
    die("Oops: {}".format(e))
