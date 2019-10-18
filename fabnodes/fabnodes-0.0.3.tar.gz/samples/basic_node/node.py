import os
import json

import boto3

from fabnodes import lib as fablib


@fablib.S3Distribution('jlh-dev-lambda-functions')
@fablib.Inputs([
    {'name': 'Router', 'source': 'snsRouterTopicId'},
    {'name': 'ExternalInput', 'type': 'arn', 'source': 'sns_arn'}])
@fablib.S3Access('someS3BucketARN', role='someRoleARN')
@fablib.Outputs([
    {'name': 'Alpha'}])
@fablib.BasicNode('aBasicNode', 'comRoaetFabnodeSample', 'Sample Node')
def lambda_handler(events, context):
    client = boto3.client('sns')
    sns_target_arn = os.environ['Alpha']
    body_content = json.dumps(events)
    response = client.publish(
        TargetArn=sns_target_arn,
        Message=json.dumps({'default': body_content}),
        MessageStructure='json'
    )
    print(response)


if __name__ == '__main__':
    print(fablib.generator().generate_all(__name__))
