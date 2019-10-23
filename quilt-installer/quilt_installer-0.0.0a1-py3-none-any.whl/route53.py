import boto3

def get_route53_client():
    return boto3.client('route53')


def add_route53_cname_record(hosted_zone_id, source, target):
    try:
        response = get_route53_client().change_resource_record_sets(
                HostedZoneId=hosted_zone_id,
                ChangeBatch={
                    'Comment': f'Quilt install, {source} -> {target}',
                    'Changes': [
                        {
                            'Action': 'UPSERT',
                            'ResourceRecordSet': {
                                'Name': source,
                                'Type': 'CNAME',
                                'TTL': 300,
                                'ResourceRecords': [{'Value': target}]
                            }
                        }]
                })
    except Exception as e:
        print(e)


def find_route53_hosted_zone(domain_name_to_find):
    paginator = get_route53_client().get_paginator('list_hosted_zones')
    for resp in paginator.paginate():

        for hz in resp["HostedZones"]:
            domain_name = hz["Name"]
            hz_id = hz["Id"]
            if domain_name.endswith("."):
                domain_name = domain_name[:-1]
                if domain_name.endswith(domain_name_to_find):
                    return hz_id

    return None



