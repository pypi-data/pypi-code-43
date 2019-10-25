#!/usr/bin/python
#
# Print the two-element list of active/standby CMS.
# We have not been using a Standby CMS for years,
# hence the output of the 'Standby' field is "<none>".
#
from dgpy.cms_client import CmsClient

print "Active CMS:  {}\nStandby CMS: {}".format(*CmsClient().cms_list())
