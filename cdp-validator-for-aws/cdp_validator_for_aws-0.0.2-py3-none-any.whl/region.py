import botocore
from botocore.exceptions import ClientError

# Parse the bucketname -and do a boto call to see if the bucket exists
# verify that bucket is in the same region as VPC

def validate_region(eksclient, issues):
    try:
        eksclient.list_clusters()
    except botocore.exceptions.ClientError:
        issues.append("Region: This Region does not support EKS")
    return 
