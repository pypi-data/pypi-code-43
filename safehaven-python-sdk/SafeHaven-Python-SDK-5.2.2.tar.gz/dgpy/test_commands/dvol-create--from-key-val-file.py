#!/usr/bin/python
#
# Variation
#
# The file contains each of the individual CREATE_DVOL parameters.
# If a parameter contains spaces, it must be enclosed in quotes.
# The file can optionally contain 'dvol-create' as first parameter.
#
# See below and the 'example_configurations' folder for examples.
import os
import argparse
from dgpy.dvol       import DvolCreate
from dgpy.conf_file  import ConfFile
from dgpy.cms_client import CmsClient
from dgpy.utils      import die, fatal
from dgpy.job        import status_printer
from dgpy.errors     import LegacyMessageError, GrpcError, TimeOutError

parser = argparse.ArgumentParser(description="Create a legacy DVOL from a key-value file @FILE")

parser.add_argument('FILE', type=argparse.FileType('r'),      help = 'Path to the key-value file')
parser.add_argument('-w', '--wait',    action='store_true',   help = 'Wait for the job to complete')
parser.add_argument('-t', '--timeout', type=float, default=0, help = 'Optional timeout for the --wait operation in seconds')

args = parser.parse_args()
try:
    conf   = ConfFile(args.FILE.name)
    client = CmsClient()
    res    = client.dvol_create(DvolCreate.from_ConfHash(conf))
    if args.wait or args.timeout > 0:
        client.wait_for_job(res.job_id, args.timeout, status_printer)
    else:
        print "Create-DVOL job #{0}".format(res.job_id)
except (LegacyMessageError, GrpcError) as e:
    die("Failed to create PG: {0}".format(e))
except TimeOutError as e:
    die("Timed out: {}".format(e))

#
#  APPENDIX: sample '.conf' file contents (same file contents as the one
#            found in the dvol-create.py '.console' example):
#
#  name            = CA2GRRTAWS-RH02-PG
#  type            = COW
#  lv_size         = 17.0G
#  sync_threshold  = 1048576
#  ms_snap_size    = 4352.0M
#  rs_snap_size    = 4352.0M
#  snapshot_period = 0
#  ms_ip           = 10.55.220.131
#  ms_storage_ip   = 10.55.220.131
#  ms_data_pool    = pool
#  ms_snap_pool    = pool
#  rs_ip           = 10.55.220.229
#  rs_storage_ip   = 10.55.220.229
#  rs_data_pool    = pool
#  rs_snap_pool    = pool
#  pg_prim_type    = CLC
#  pg_sec_type     = CLC
#  pg_prim_stubs   = false
#  pg_sec_stubs    = false
#  pg_prim_name    = <none>
#  pg_sec_name     = <none>
#  plun_params     = <none>|<none>|CA2GRRTAWS-RH02|LINUX|Red Hat Enterprise Linux 6 (64-bit)|<none>|<none>|RSYNC|disk-0,18253611008,CA2GRRTAWS-RH02
#  make_stubs      = false
#  group_uuid      =
#  location        =
#  group_name      =
#  name_seeds      =
#  stub_templates  =
#  num_cpu         =
#  memory_gb       =
#  network_name    =
#  stub_password   = Trlabs1!
#  descriptions    =
#  target_names    =
#  makestub_url    =
#  stub_os_type    =
#  prim_rec_plan   = CA2GRRTAWS-RH02,0,POWER_ON,30,0,SHUTDOWN,0,RHEL 6 guest VM,10.55.220.122,<none>,<none>,CA2GRRTAWS-RH02
#  prim_vapp_name  = <none>
#  sec_rec_plan    = CA2GRRTAWS-RH02,0,POWER_ON,30,0,SHUTDOWN,0,RHEL 6 guest VM,10.55.220.122,<none>,<none>,CA2GRRTAWS-RH02
#  sec_vapp_name   = <none>
#  Successfully created PG '?'
