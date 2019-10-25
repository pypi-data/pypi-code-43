#!/usr/bin/python
#
# Print the list of all registered CMS users.
#
from dgpy.cms_client import CmsClient

print "Registered CMS users:"
for i, user in enumerate(CmsClient().user_list()):
    print "#%d: %s" % (i, user)
