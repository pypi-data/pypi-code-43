from cdp_validator_for_aws import settings


def sg_check_outbound(IpPermissionsList):
    # There are 2 ways the egress rules in a SG can be correct:
    #  - We have the default rule - FromPort & ToPort are not defined in the
    #    JSON & Protocol is -1, CIDR is 0.0.0.0/0
    #  - Create the rule explicitly - 0-65535,  0.0.0.0/0 for TCP and for UDP

    # NOTE: It is possible, in theory to create a bunch of egress rules that
    #  aggregate to All - we are not going to handle that
    # sort of complex situation here (yet)

    # See if the default rule is defined.  If it is, then no need to go any further
    applicable_rules = [d for d in IpPermissionsList
                        if d['IpProtocol'] == '-1' and
                        {'CidrIp': '0.0.0.0/0'} in d['IpRanges'] and
                        not 'FromPort' in d.keys()]

    if (len(applicable_rules) > 0):
        return True

    # else, we have to find 2 rules - 0-65535, TCP, 0.0.0.0/0 and 0-65535, UDP, 0.0.0.0/0
    applicable_rules = [d for d in IpPermissionsList
                        if d['IpProtocol'] == 'tcp' and
                        {'CidrIp': '0.0.0.0/0'} in d['IpRanges'] and
                        d['FromPort'] == 0 and
                        d['ToPort'] == 65535]

    if (len(applicable_rules) == 0):
        return False

    applicable_rules = [d for d in IpPermissionsList
                        if d['IpProtocol'] == 'udp' and
                        {'CidrIp': '0.0.0.0/0'} in d['IpRanges'] and
                        d['FromPort'] == 0 and
                        d['ToPort'] == 65535]

    if (len(applicable_rules) == 0):
        return False

    return True

# We are using different functions for ingress & egress checks on purpose - the
# JSON for egress has some subtle differences (no FromPort & ToPort when default
# rule is used) and it is just easier to treat it as separate than write really
# messy code for the sake of having one function


def sg_grab_cidrs_for_port(IpPermissionsList, port):

    cidrList = []

    fromPort = port
    toPort = port

    # if port is zero then assume we are looking for a rule from 0 to 65535
    # This means IpPermissionList will not have FromPort and ToPort at all

    if (port == 0):
        fromPort = 0
        toPort = 65535

    # filter the list of all rules - only rules with TCP/All protocol &
    # the specified ports are valid the <= and >= logic below is to allow rules
    # that specify a port range (e.g. 8441-8445) to be included in the filter

    # DN: This next kluge is to solve issue 116.  When you create a Security Group
    # through terraform, any rule that covers ports 0-65535 does not have a
    # FromPort or ToPort.  This is not the same when a SG is created from the
    # Management Console.  To fix this, I was faced with two choices:
    #  1. This kluge
    #  2. Have a series of if loops around the filter
    # In the end, I took the path more travelled - I think it makes the code a
    # bit easier to read

    for d in IpPermissionsList:
        if not 'FromPort' in d:
            d['FromPort'] = 0
        if not 'ToPort' in d:
            d['ToPort'] = 65536

    applicable_rules = [d for d in IpPermissionsList
                        if (d['IpProtocol'] == '-1' or d['IpProtocol'] == 'tcp') and
                        d['FromPort'] <= fromPort and d['ToPort'] >= toPort]

    # This is alist of rules, we need all the rule->CIDRs from this list.
    # IpRanges is a list, so we need to iterate over it
    for x in applicable_rules:
        for y in x['IpRanges']:
            cidrList.append(y['CidrIp'])

    return cidrList


###
# Security groups Requirements
# (from: https://docs.cloudera.com/management-console/cloud/environments/topics/mc-environment-aws-security-groups.html)
# SG_Knox:
#   - TCP Port 22 to endpoint CIDR
#   - TCP Port 8443 to endpoint CIDR
#   - TCP Port 9443 to endpoint Cloudera IPs
#   - All ports In-VPC
# SG_Default:
#   - TCP Port 22 to CIDR
#   - All Ports In-VPC

# Function: sgs_are_valid (sg_knox, sg_default)
# Returns:
# Checks:
# 1. Is the group EC2-classic, or are they mapped to a VPC
# 2. Are they mapped to the same VPC
# 4. Do both groups have the same source for port 22
# 5. Does the Knox group have the same source for 22 and 8443
# 6. Does the knox group have a rule that allows 9443 access for Cloudera IP
# 7. Check inter-VPC comms
# NOTE: Nested security groups are ignored

def sgs_are_valid(sg_knox, sg_default, vpc_cidr, issues):
    knox_gn = sg_knox["GroupName"]
    default_gn = sg_default["GroupName"]

    # If this is an EC2-Classic security group, error out - this won't work
    if ('VpcId' not in sg_knox.keys()) or ('VpcId' not in sg_default.keys()):
        issues.append(
            "Security Groups: At least one security group is of type EC2-Classic; this is not supported")
        return

    # Both security groups must be assoicated to the same VPC
    if (sg_knox['VpcId'] != sg_default['VpcId']):
        issues.append(
            "Security Groups: Both security groups should be associated with the same VPC")

    # Check the Egress for both rules has a 0.0.0.0/0 rule
    if not sg_check_outbound(sg_knox['IpPermissionsEgress']):
        issues.append(
            "Security Groups: The Knox security group {} does not have any valid outbound rules".format(knox_gn))

    if not sg_check_outbound(sg_default['IpPermissionsEgress']):
        issues.append(
            "Security Groups: The Default security group {} does not have any valid outbound rules".format(default_gn))

    # we will catch the VPC CIDR as well, so filter that out
    knox22 = sg_grab_cidrs_for_port(sg_knox['IpPermissions'], 22)
    knox22 = list(filter(lambda x: x != vpc_cidr, knox22))

    default22 = sg_grab_cidrs_for_port(sg_default['IpPermissions'], 22)
    default22 = list(filter(lambda x: x != vpc_cidr, default22))

    knox8443 = sg_grab_cidrs_for_port(sg_knox['IpPermissions'], 8443)
    knox8443 = list(filter(lambda x: x != vpc_cidr, knox8443))

    knox9443 = sg_grab_cidrs_for_port(sg_knox['IpPermissions'], 9443)
    knox9443 = list(filter(lambda x: x != vpc_cidr, knox9443))

    knoxAll = sg_grab_cidrs_for_port(sg_knox['IpPermissions'], 0)
    defaultAll = sg_grab_cidrs_for_port(sg_default['IpPermissions'], 0)

    # ACK, we have a problem, we don't know the endpoint CIDR, how can we tell if its in the
    # security group

    # We have to find out if port 22 in the Knox SG is open to a CDIR that isn't the
    if len(knox22) == 0:
        issues.append(
            "Security Groups: The Knox security group {} does not have an inbound rule for Port 22/TCP".format(knox_gn))

    if len(default22) == 0:
        issues.append(
            "Security Groups: The Default security group {} does not have an inbound rule for Port 22/TCP".format(default_gn))

    if len(knox8443) == 0:
        issues.append(
            "Security Groups: The Knox security group {} does not have an inbound rule for Port 8443/TCP".format(knox_gn))

    # With this logic, we are testing for matching 22s even when the Security
    # Group doesn't have a 22 rule In the interest of neater code, I'll just leave this here as is
    if len(set(knox22) & set(default22)) == 0:
        issues.append(
            "Security Groups: Knox and Default Security Groups ({}, {}) don't have a matching rule for port 22".format(knox_gn, default_gn))

    if len(set(knox22) & set(knox8443)) == 0:
        issues.append(
            "Security Groups: The Knox security group {} has different CIDRs for incoming ports 22 and 8443".format(knox_gn))

    if not all(elem in knox9443 for elem in settings.G_ClouderaIPs):
        issues.append(
            "Security Groups: The Knox security group {} does not allow incoming 9443/TCP from the published Cloudera IPs".format(knox_gn))

    if (vpc_cidr not in knoxAll):

        issues.append(
            "Security Groups: Unable to find a rule that allows in-VPC traffic in the Knox security group {}".format(knox_gn))

    if (vpc_cidr not in defaultAll):
        issues.append(
            "Security Groups: Unable to find a rule that allows in-VPC traffic in the Default security group {}".format(default_gn))

    return
