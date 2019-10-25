#!/usr/bin/python
#
# Automated LRA installation onto one or more targets of a PG.
#
# Usage: $0 <PG-Name> <VM-Name> <VM-IP> <VM-Remote-IP> <VM-User> <VM-Pass> <URL>, with
#         - @PG-Name:      Name of the protection group that contains @VM-Name
#         - @VM-Name:      Name of the target VM to install the Replication Agent on
#         - @VM-IP:        IP address of @VM-Name on the Production Site
#         - @VM-Remote-IP: IP address of the stub corresponding to @VM-Name on the Remote Site (DR)
#         - @VM-User:      Administrative user on @VM-Name
#         - @VM-Pass:      Login password for @VM-User
#         - @URL:          Replication agent installer download URL (http://...)
#
# NOTE: Even though the above speaks about a single VM, it is possible to install onto multiple VMs
#       at the same time, by replacing the single `VM-xxx` arguments with ',' separated strings that
#       contain the parameters for each VM in turn.
import argparse
from dgpy.cms_client import CmsClient
from dgpy.utils      import die
from dgpy.job        import status_printer
from dgpy.errors     import LegacyMessageError, GrpcError, TimeOutError

parser = argparse.ArgumentParser(description="Automated LRA installation onto one or more targets of @DVOL")

parser.add_argument('DVOL',                         type=str, help = 'Name of the Protection Group')
parser.add_argument('VM',                           type=str, help = 'Name of the target VM to install the Replication Agent on')
parser.add_argument('VM_PR_IP', metavar='VM-PR-IP', type=str, help = 'IP address of @VM on the Production Site')
parser.add_argument('VM_DR_IP', metavar='VM-DR-IP', type=str, help = 'IP address of the stub corresponding to @VM on the Remote Site (DR)')
parser.add_argument('USER',                         type=str, help = 'Administrative user on @VM')
parser.add_argument('PASS',                         type=str, help = 'Login password for @USER')
parser.add_argument('URL',                          type=str, help = 'Replication agent installer download URL (http://...)')

parser.add_argument('-w', '--wait',    action='store_true',   help = 'Wait for the job to complete')
parser.add_argument('-t', '--timeout', type=float, default=0, help = 'Optional timeout for the --wait operation in seconds')

args = parser.parse_args()
try:
    client = CmsClient()
    res = client.dvol_install_lra(args.DVOL, args.VM, args.VM_PR_IP, args.VM_DR_IP, args.USER, args.PASS, args.URL)
    if args.wait or args.timeout > 0:
        client.wait_for_job(res.job_id, args.timeout, status_printer)
    else:
        print "Install LRA job #{0}".format(res.job_id)
except (LegacyMessageError, GrpcError) as e:
    die("Failed to install LRA onto {0}: {1}".format(args.VM, e))
except TimeOutError as e:
    die("Timed out: {}".format(e))
