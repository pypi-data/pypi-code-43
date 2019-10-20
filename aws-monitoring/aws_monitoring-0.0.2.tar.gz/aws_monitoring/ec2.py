"""Amazing module."""

import boto3
import pprint


def print_ec2_info():
    """Amazing function."""
    ec2 = boto3.client('ec2')

    # Retrieves all regions/endpoints that work with EC2
    response = ec2.describe_regions()
    printer = pprint.PrettyPrinter(indent=2)
    printer.pprint(response['Regions'])

    # Retrieves availability zones only for region of the ec2 object
    response = ec2.describe_availability_zones()
    printer.pprint(response['AvailabilityZones'])


if __name__ == "__main__":
    print_ec2_info()
