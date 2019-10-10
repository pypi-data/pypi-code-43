#!/usr/bin/env python3
import argparse
import sys
import boto3
import botocore.exceptions
import json
import pprint
from urllib import parse

from cdp_validator_for_aws import security_groups as sg
from cdp_validator_for_aws import networking as n
from cdp_validator_for_aws import policy_manager as pm
from cdp_validator_for_aws import role as role
from cdp_validator_for_aws import region as region
from cdp_validator_for_aws import s3 as s3
from cdp_validator_for_aws import settings


# Using logging as per
# https://powerfulpython.com/blog/nifty-python-logging-trick/
# and
# https://docs.python.org/3/howto/logging.html
# and
# https://docs.python.org/3/library/logging.html

import logging
import os

# Set the logger up, defaulting to WARNING level no matter how
# misconfigured things are
LOGLEVEL = getattr(logging, os.environ.get(
    'LOGLEVEL', 'WARNING').upper(), 'WARNING')
if not isinstance(LOGLEVEL, int):
    LOGLEVEL = getattr(logging, 'WARNING')
logging.basicConfig(level=LOGLEVEL)
logger = logging.getLogger('cdp_driver')


# no input validation code, since the data comes from the GUI,  safe
# to assume its sanitized


# Default them globals here for clarity
# 1. G_CDPCredentials - String
# 2. G_EndpointCIDR
# 3. G_AWSEnvironment - Dictionary

G_CDPCredentials = ""
G_EndpointCIDR = ''
G_PrettyPrinter = pprint.PrettyPrinter(indent=4)


G_AWSEnvironment = {
    'Region': {'AWSResourceID': '', 'Issues': []},
    'VPC': {'AWSResourceID': '', 'Issues': []},
    'Subnets': [],
    'SG_Knox': {'AWSResourceID': '', 'Issues': []},
    'SG_Default': {'AWSResourceID': '', 'Issues': []},
    'S3_Logs': {'AWSResourceID': '', 'Issues': []},
    'S3_Data': {'AWSResourceID': '', 'Issues': []},
    'IP_Logs': {'AWSResourceID': '', 'Issues': []},
    'IP_Data': {'AWSResourceID': '', 'Issues': []},
    'IP_IDBroker': {'AWSResourceID': '', 'Issues': []},
    'Role_Baseline': {'AWSResourceID': '', 'Issues': []},
    'Role_DataAccess': {'AWSResourceID': '', 'Issues': []},
    'DynamoDB_S3Guard': {'AWSResourceID': '', 'Issues': []},
    'storageLocationBase': '',
    'idBrokerInstanceProfileArn': ''
}


# Utility Function: Is this VPC autocreated?

def network_is_autocreated():
    global G_AWSEnvironment
    if G_AWSEnvironment['VPC']['AWSResourceID'] == "AutoCreate":
        logger.info("Network is autocreated")
        return True
    return False

# Utility Function: Are the Security Groups going to be AutoCreated?


def sgs_are_autocreated():
    global G_EndpointCIDR
    if G_EndpointCIDR != '':
        logger.info("Security Groups are auto created")
        return True
    return False

# Utility Function: Return CidrBlock for this VPC ID


def getCIDRForVPC(vpcid):
    if network_is_autocreated():
        return ''

    ec2 = boto3.client(
        'ec2', region_name=G_AWSEnvironment['Region']['AWSResourceID'])
    vpc = ec2.describe_vpcs(
        Filters=[
            {
                'Name': 'vpc-id',
                'Values': [vpcid]
            },
        ]
    )
    cidrblock = vpc["Vpcs"][0]["CidrBlock"]
    logger.info("VPC ID: " + vpcid + "CIDR Block: " + cidrblock)

    return cidrblock

# utility function - make sure bucket name starts with s3a://


def is_instance_profile_arn(string):
    ''' Return whether the given string represents an instance profile.

    Raise argparse.ArgumentTypeError if not
    '''
    # instance profile arn format defined: https://docs.aws.amazon.com/IAM/latest/UserGuide/list_identityandaccessmanagement.html#identityandaccessmanagement-resources-for-iam-policies
    value = string
    if ":instance-profile/" in value:
        return value
    else:
        msg = '''
Expected instance profile arn to contain ':instance-profile'
# identityandaccessmanagement-resources-for-iam-policies.
as per https://docs.aws.amazon.com/IAM/latest/UserGuide/list_identityandaccessmanagement.html
Got '{}'
'''.strip().format(value)
        raise argparse.ArgumentTypeError(msg)
# utility function - parse ARN and grab the role name from it


def get_role_name_from_arn(arn):
    parts = arn.split('/')
    return parts[-1]

# populateGlobals - read the input JSON and populate a global variable
# which is a dictionary of the various elements
#
# Why create a new dictionary when we already have one from the input JSON?
# 0. The input JSON isn't complete - at least 2 inputs are missing from it (IDBroker
#    Instance Profile S3 Bucket for data)
# 1. We know the JSON file format is changing at some
#   point. This way we will adjust the code in only one function
#   (populateGlobals) rather than all over the code
# 2. We want keep moving through the validaton process and keep
#    appending problems instead of erroring out when we run into an
#    error, having all variables in one place makes it a bit cleaner to look at


def populateGlobals(cdpEnv, awsEnv):
    global G_CDPCredentials
    global G_EndpointCIDR

    G_CDPCredentials = cdpEnv['authentication']['publicKeyId']

    awsEnv['Region']['AWSResourceID'] = cdpEnv['location']['name']
    logger.info('Region' + awsEnv['Region']['AWSResourceID'])

    if 'aws' not in cdpEnv['network']:
        awsEnv['VPC']['AWSResourceID'] = "AutoCreate"
        logger.info('VPC: AutoCreate')
    else:
        awsEnv['VPC']['AWSResourceID'] = cdpEnv['network']['aws']['vpcId']
        logger.info('VPC:' + awsEnv['VPC']['AWSResourceID'])
        for subnetId in cdpEnv['network']['subnetIds']:
            awsSubnet = {'AWSResourceId': str(subnetId), 'Issues': []}
            awsEnv['Subnets'].append(awsSubnet)

    if 'cidr' in cdpEnv['securityAccess']:
        G_EndpointCIDR = cdpEnv['securityAccess']['cidr']
    else:
        awsEnv['SG_Knox']['AWSResourceID'] = cdpEnv['securityAccess']['securityGroupIdForKnox']
        awsEnv['SG_Default']['AWSResourceID'] = cdpEnv['securityAccess']['defaultSecurityGroupId']
        logger.info('SGs:' + awsEnv['SG_Knox']['AWSResourceID'] +
                    awsEnv['SG_Default']['AWSResourceID'])

    awsEnv['S3_Logs']['AWSResourceID'] = cdpEnv['telemetry']['logging']['storageLocation']
    logger.info('S3 Log: ' + awsEnv['S3_Logs']['AWSResourceID'])

    if "storageLocationBase" not in cdpEnv.keys():
        raise ValueError(
            "No storage location base was given. Neither on the command line nor in the json file")

    awsEnv['S3_Data']['AWSResourceID'] = cdpEnv["storageLocationBase"]
    awsEnv["storageLocationBase"] = cdpEnv["storageLocationBase"]
    logger.info('S3 Data: ' + awsEnv['S3_Data']['AWSResourceID'])

    awsEnv['IP_Logs']['AWSResourceID'] = cdpEnv['telemetry']['logging']['s3']['instanceProfile']
    logger.info('IP Logs: ' + awsEnv['IP_Logs']['AWSResourceID'])

    awsEnv['IP_Data']['AWSResourceID'] = 'NOTGIVEN'
    logger.info('IP Logs: ' + awsEnv['IP_Data']['AWSResourceID'])

    awsEnv['Role_DataAccess']['AWSResourceID'] = cdpEnv['idBrokerMappings']['dataAccessRole']
    logger.info('Data Access Role: ' +
                awsEnv['Role_DataAccess']['AWSResourceID'])

    awsEnv['Role_Baseline']['AWSResourceID'] = cdpEnv['idBrokerMappings']['baselineRole']
    logger.info('Baseline Role: ' + awsEnv['Role_Baseline']['AWSResourceID'])

    awsEnv['DynamoDB_S3Guard']['AWSResourceID'] = cdpEnv['aws']['s3guard']['dynamoDbTableName']
    logger.info('S3Guard Table: ' +
                awsEnv['DynamoDB_S3Guard']['AWSResourceID'])

    awsEnv['idBrokerInstanceProfileArn'] = cdpEnv['idBrokerInstanceProfileArn']
    awsEnv['storageLocationBase'] = cdpEnv['storageLocationBase']

    return


###
# Validation Functions Go Here
###
def validateRegion(issues, boto3_session):
    eksclient = boto3_session.client(
        'eks', region_name=G_AWSEnvironment['Region']['AWSResourceID'])
    region.validate_region(eksclient, issues)


def validateVPC(issues, ec2):
    if network_is_autocreated():
        logger.info("Network: Autocreated networks are automatically validated")
        return

    vpcid = G_AWSEnvironment['VPC']['AWSResourceID']
    n.vpc_is_valid(ec2, vpcid, issues)


def validateNetwork(issues, ec2):
    if network_is_autocreated():
        logger.info("Network: Autocreated networks are automatically validated")
        return

    vpcid = G_AWSEnvironment['VPC']['AWSResourceID']

    # Next, look at subnets
    subnetids = [subnet["AWSResourceId"]
                 for subnet in G_AWSEnvironment["Subnets"]]
    try:
        subnets = ec2.describe_subnets(Filters=[
            {
                'Name': 'vpc-id',
                'Values': [
                    vpcid
                ]
            }
        ],
            SubnetIds=subnetids
        )
        route_tables = ec2.describe_route_tables(
            Filters=[
                {
                    'Name': 'vpc-id',
                    'Values': [
                        vpcid
                    ]
                },
            ]
        )
        n.subnets_are_valid(subnets, route_tables, issues)
    except botocore.exceptions.ClientError as ce:
        logging.getLogger(__name__).warning(
            "Skipping Subnet and RouteTable checks because this error occurred: "+str(ce))


def validateSG(issues, ec2):
    global G_AWSEnvironment

    if sgs_are_autocreated():
        logger.info("SG: Autocreated SGs are automatically validated")
        return

    try:
        sg_idbroker = ec2.describe_security_groups(
            Filters=[
                {
                    'Name': 'group-id',
                    'Values': [
                        G_AWSEnvironment['SG_Knox']['AWSResourceID'],
                    ]
                },
            ]
        )["SecurityGroups"][0]

        sg_master = ec2.describe_security_groups(
            Filters=[
                {
                    'Name': 'group-id',
                    'Values': [
                        G_AWSEnvironment['SG_Default']['AWSResourceID'],
                    ]
                },
            ]
        )["SecurityGroups"][0]

        vpc_cidr = getCIDRForVPC(G_AWSEnvironment['VPC']['AWSResourceID'])
        sg.sgs_are_valid(sg_idbroker, sg_master, vpc_cidr, issues)
    except botocore.exceptions.ClientError as ce:
        logging.getLogger(__name__).warning(
            "Skipping security group checks because this error occurred: "+str(ce))


def validateS3(issues, boto3_session):

    global G_AWSEnvironment

    databucket = G_AWSEnvironment["S3_Data"]["AWSResourceID"]
    logbucket = G_AWSEnvironment["S3_Logs"]["AWSResourceID"]
    region = G_AWSEnvironment["Region"]["AWSResourceID"]

    # if data bucket specified via command line, use it

    s3.s3_buckets_are_valid(logbucket, databucket,
                            region, boto3_session, issues)
    return


def validate_roles(issues, iam_client):
    try:
        # Get the names as understood by the role system
        log_instance_profile_arn = G_AWSEnvironment["IP_Logs"]["AWSResourceID"]
        ranger_instance_profile_arn = G_AWSEnvironment["Role_DataAccess"]["AWSResourceID"]
        admin_instance_profile_arn = G_AWSEnvironment["Role_Baseline"]["AWSResourceID"]
        log_location_base = strip_urlscheme(
            G_AWSEnvironment["S3_Logs"]["AWSResourceID"])
        dynamodb_table_name = G_AWSEnvironment["DynamoDB_S3Guard"]["AWSResourceID"]
        storage_location_base = strip_urlscheme(
            G_AWSEnvironment["storageLocationBase"])
        idbroker_instance_profile_arn = G_AWSEnvironment["idBrokerInstanceProfileArn"]
        rb = role.BotoRoleBuilder(admin_instance_profile_arn,
                                  idbroker_instance_profile_arn,
                                  log_instance_profile_arn,
                                  ranger_instance_profile_arn,
                                  pm.create_substitutes(log_location_base,
                                                        storage_location_base,
                                                        dynamodb_table_name),
                                  iam_client)
        rb.validate_roles(issues)
    except (botocore.exceptions.ClientError, botocore.exceptions.ParamValidationError) as e:
        print(e)
        logger.warning(
            "Botocore exceptions raised. No role validation performed")


# Usage: cdp_driver.py [Required Arguments] [Optional Arguments]
# Required Arguments:
# -i | --idbroker_instance_profile_arn arn:aws:iam....
# -s | --storage_location_base s3a://bucketname
# Optional Arguments:
# -c | --cdp_file filename.json --> if not given, defaults to waiting on stdin
# --region  - validate only the region
# --vpc - validate only vpc & subnet
# --sg  - validate only security groups
# --iam - validate only roles & policies
# --s3  - validate only s3
#
# The default is to validate all components - Region, VPC, SG, IAM and S3
# Enabling any specific validation (--region, --vpc, --sg, --iam, --s3)
# overrides the default - i.e. only those validations specified on the command
# line will work.

def strip_urlscheme(s3url):
    ''' Returns bucket and path stripped from the s3a urllib

    Throw ValueError if this is not an s3a urllib
    '''
    parseresult = parse.urlsplit(s3url)
    if parseresult.scheme not in ("", 's3a'):
        msg = "Expected an url like 's3a://{}'  - got '{}'".format(
            parseresult.netloc, s3url)
        raise ValueError(msg)
    return parseresult.netloc+parseresult.path


def is_s3a_bucket(string):
    try:
        return strip_urlscheme(string)
    except ValueError as ve:
        raise argparse.ArgumentTypeError(str(ve))


def main():
    settings.init()
    parser = argparse.ArgumentParser(prog="cdp_validator_for_aws")
    parser.add_argument("-i", "--idbroker_instance_profile_arn",
                        help="idbroker instance profile arn",
                        required=False,
                        type=is_instance_profile_arn)
    parser.add_argument("-s", "--storage_location_base",
                        required=False, type=is_s3a_bucket)
    parser.add_argument("-c", "--cdp_file",
                        help="Json file describing cdp build",
                        required=False,
                        type=argparse.FileType('r'))
    parser.add_argument("--profile", help="aws profile name to be used")
    parser.add_argument("--region",
                        help="only validate the region",
                        action="store_true")
    parser.add_argument("--vpc",
                        help="only validate vpc, subnets",
                        required=False,
                        action="store_true")
    parser.add_argument("--sg",
                        help="only validate security groups",
                        required=False,
                        action="store_true")
    parser.add_argument("--s3",
                        help="only validate the s3 buckets",
                        required=False,
                        action="store_true")
    parser.add_argument("--iam",
                        help="only validate the roles",
                        required=False,
                        action="store_true")

    args = parser.parse_args()

    do_all_validations = True

    if any([args.region, args.vpc, args.sg, args.iam, args.s3]):
        logger.info("Only requested validations will be done")
        do_all_validations = False

    if not args.cdp_file:
        print('Enter JSON below, terminate input with EOF\n')
        jsoninput = sys.stdin
    else:
        jsoninput = args.cdp_file
    inputdict = json.load(jsoninput)
    if args.storage_location_base:
        inputdict["storageLocationBase"] = args.storage_location_base
    populateGlobals(inputdict, G_AWSEnvironment)
    logger.info(G_PrettyPrinter.pformat(G_AWSEnvironment))

    boto3_session = boto3.session.Session(profile_name=args.profile,
                                          region_name=G_AWSEnvironment["Region"]['AWSResourceID'])

    issues = []

    if do_all_validations or args.region:
        validateRegion(issues, boto3_session)

    if do_all_validations or args.vpc:
        validateVPC(issues, boto3_session.client('ec2'))
        validateNetwork(issues, boto3_session.client('ec2'))

    if do_all_validations or args.sg:
        validateSG(issues, boto3_session.client('ec2'))

    if do_all_validations or args.iam:
        validate_roles(issues, boto3_session.client('iam'))

    if do_all_validations or args.s3:
        validateS3(issues, boto3_session.client("s3"))

    if len(issues) == 0:
        print("Validation complete - no issues found")
        sys.exit(0)
    else:
        print("Issues found: ")
        for issue in issues:
            print(issue)
        sys.exit(1)
