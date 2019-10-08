import os
import json

import boto3

from fabnodes import lib as fablib


@fablib.Distribution('jlh-dev-lambda-functions')
@fablib.Inputs([
    {'name': 'Router', 'source': 'snsRouterTopicId'}])
@fablib.Outputs([
    {'name': 'Alpha'}])
@fablib.Node('BasicNode', 'comRoaetFabnodeSample', 'Basic Node')
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
    fablib.generate(lambda_handler)
