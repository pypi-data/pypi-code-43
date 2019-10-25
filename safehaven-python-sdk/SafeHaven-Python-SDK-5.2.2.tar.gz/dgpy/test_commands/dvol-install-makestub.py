#!/usr/bin/python
#
# Automated MakeStub.exe installation onto one or more targets of a PG.
#
# Usage: $0 <PG-Name> <VM-Name> <VM-IP> <VM-User> <VM-Pass> <URL> <OS-Type>, with
#         - @PG-Name:  Name of the protection group that contains @VM-Name
#         - @VM-Name:  Name of the target VM to install MakeStub.exe on
#         - @VM-IP:    IP address of @VM-Name on the Production Site
#         - @VM-User:  Administrative user on @VM-Name
#         - @VM-Pass:  Login password for @VM-User
#         - @URL:      MakeStub.exe download URL (http://...)
#         - @OS-Type:  O.S. type common to all VMs in @PG-Name: one of 'WINDOWS' or 'LINUX'
#
# NOTE: Even though the above speaks about a single VM, it is possible to install onto multiple VMs
#       at the same time, by replacing the single `VM-xxx` arguments with ',' separated strings that
#       contain the parameters for each VM in turn.
import argparse
from dgpy.cms_client import CmsClient
from dgpy.utils      import die
from dgpy.job        import status_printer
from dgpy.errors     import LegacyMessageError, GrpcError, TimeOutError

parser = argparse.ArgumentParser(description="Automated MakeStub.exe installation onto one or more targets of @DVOL")

parser.add_argument('DVOL',                   type=str, help = 'Name of the Protection Group containing @VM')
parser.add_argument('VM',                     type=str, help = 'Name of the target VM to install MakeStub.exe on')
parser.add_argument('VM_IP', metavar='VM-IP', type=str, help = 'IP address of @VM on the Production Site')
parser.add_argument('USER',                   type=str, help = 'Administrative user on @VM')
parser.add_argument('PASS',                   type=str, help = 'Login password for @USER')
parser.add_argument('URL',                    type=str, help = 'MakeStub.exe installer download URL (http://...)')
parser.add_argument('OS',                     type=str, help = 'OS type common to all VMs in @DVOL (WINDOWS|LINUX)', choices=['WINDOWS', 'LINUX'])

parser.add_argument('-w', '--wait',    action='store_true',   help = 'Wait for the job to complete')
parser.add_argument('-t', '--timeout', type=float, default=0, help = 'Optional timeout for the --wait operation in seconds')

args = parser.parse_args()
try:
    client = CmsClient()
    res = client.dvol_install_makestub(args.DVOL, args.VM, args.VM_IP, args.USER, args.PASS, args.URL, args.OS)
    if args.wait or args.timeout > 0:
        client.wait_for_job(res.job_id, args.timeout, status_printer)
    else:
        print "Install Makestub job #{0}".format(res.job_id)
except (LegacyMessageError, GrpcError) as e:
    die("Failed to install MakeStub.exe onto {0}: {1}".format(args.VM, e))
except TimeOutError as e:
    die("Timed out: {}".format(e))
