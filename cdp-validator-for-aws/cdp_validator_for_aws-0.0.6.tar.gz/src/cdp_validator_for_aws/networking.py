import botocore.exceptions
import logging


def subnet_provides_public_ip_mapping(subnet):
    "True iff subnet will map public ips on launch"
    return subnet['MapPublicIpOnLaunch']


def subnet_routes_to_internet(subnetId, tables):
    "True iff subnetId is associated with a route in routeTables that has internet access"
    # First we look to see if theres an explicit association with a suitable route table
    for rtb in tables['RouteTables']:
        assocs = [a for a in rtb["Associations"]
                  if 'SubnetId' in a and a["SubnetId"] == subnetId]
        routes = [r for r in rtb["Routes"] if is_route_valid(r)]
        # If this route table has both an explicit association with
        # the given subnetid and a valid route then this subnet can
        # reach the internet. We can return.
        if len(assocs) > 0:
            return len(routes) > 0

    # We've searched all the route tables for an explicit association
    # and none have been found. Try again, using the implicit
    # associations (I think there's only 1, but am not certain)

    for rtb in tables['RouteTables']:
        assocs = [a for a in rtb["Associations"] if a["Main"]]
        routes = [r for r in rtb["Routes"] if is_route_valid(r)]
        # If this route table has both an implicit association and a
        # valid route then this subnet can reach the internet. We can
        # return.
        if len(assocs) > 0 and len(routes) > 0:
            return True

    # Got here because the subnet was neither explicitly nor
    # implicitly associated with valid route
    return False


def is_route_valid(r):
    '''True if argument r is a valid route.

    A route is valid iff
    - it has an cidr of 0.0.0.0/0
    - its state is active
    - it has a gateway or nat id
    '''
    return (r['DestinationCidrBlock'] == "0.0.0.0/0" and
            r["State"] == "active" and
            (('GatewayId' in r and r['GatewayId'].startswith("igw-"))
             or ('NatGatewayId' in r
                 and r['NatGatewayId'].startswith("nat-"))))


def vpc_is_valid(ec2, vpcid, issues):
    ''' Return true if VPC supports DNS Names '''
    try:
        resp = ec2.describe_vpc_attribute(Attribute='enableDnsSupport',
                                          VpcId=vpcid,
                                          DryRun=False)
        if resp['EnableDnsSupport']['Value'] == False:
            issues.append(
                "VPC: The DNS Resolution attribute is disabled for VPC {}".format(vpcid))

        resp = ec2.describe_vpc_attribute(Attribute='enableDnsHostnames',
                                          VpcId=vpcid,
                                          DryRun=False)
        if resp['EnableDnsHostnames']['Value'] == False:
            issues.append(
                "VPC: The DNS Hostnames attribute is disabled for VPC {}".format(vpcid))
    except botocore.exceptions.ClientError as e:
        logging.getLogger(__name__).warning(
            "Skipping VPC checks because this error occurred: "+str(e))


def subnets_are_valid(subnets, routetables, issues):
    '''Valid means: each subnet routes to the internet, provides public IP addresses
    subnets - json containing one or more subnets, filtered to the vpc
    in question

    routetables - json containing all routetables filtered to the vpc
    in question

    '''

    num_subnets = len(subnets["Subnets"])
    if num_subnets < 2:
        issues.append(
            "Subnet: Insufficient subnets. Only {} supplied. Need at least 2".format(num_subnets))

    availability_zones = {}

    for sn in subnets["Subnets"]:
        snid = sn["SubnetId"]
        if not subnet_routes_to_internet(sn, routetables):
            issues.append(
                "Subnet: {} cannot route to the internet. Check the route tables".format(snid))
        if not subnet_provides_public_ip_mapping(sn):
            issues.append(
                "Subnet: {} does not provide public IP addresses".format(snid))

        az = sn["AvailabilityZoneId"]
        if az in availability_zones.keys():
            availability_zones[az].append(snid)
        else:
            availability_zones[az] = [snid]

    if num_subnets != len(availability_zones):
        for az in availability_zones:
            if len(az) > 1:
                issues.append(
                    "Subnet: Availability Zone {} has multiple subnets: {}".format(az, availability_zones[az]))
