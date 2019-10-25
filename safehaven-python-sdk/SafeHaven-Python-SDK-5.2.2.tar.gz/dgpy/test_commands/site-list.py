#!/usr/bin/python
#
# Print list of all registered sites.
#
from dgpy.cms_client           import CmsClient
from dgpy.safehaven.api.types  import types_enums_pb2

cols = ("Site Name", "Site Type")
print "| {0:^10} | {1:^10} |".format(*cols)
print "| {0:^10} | {1:^10} |".format(*('-' * len(c) for c in cols))

for site in CmsClient().site_list():
    # The SiteType is an enum determining the API of the SRNs that are registerd
    # with that site. Examples are VMWARE, AZURE, CLC, AWS.
    # A SiteType of 'MANUAL' means that no specific APIs are registered.
    print "| {0:<10} | {1:<10} |".format(site.name, types_enums_pb2.SiteType.Name(site.type))
