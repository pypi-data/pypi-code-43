import sys

import boto3
import os
import logging

logger = logging.getLogger(__name__)


PYTEST_EC2_MACHINE_ID = 'i-033061f15ed030e80'


def start_test_instance():
    instance_id = PYTEST_EC2_MACHINE_ID
    client = boto3.client('ec2', region_name='us-east-2')
    print('STARTING: EC2 instance')
    client.start_instances(InstanceIds=[instance_id])
    waiter = client.get_waiter('instance_running')
    print('Waiting for EC2 instance to start')
    waiter.wait(InstanceIds=[instance_id])
    print('EC2 instance started')

    response = client.describe_instances(InstanceIds=[instance_id])
    instance_ip = response['Reservations'][0]['Instances'][0]['PublicIpAddress']
    return instance_ip


def stop_test_instance():
    instance_id = PYTEST_EC2_MACHINE_ID
    client = boto3.client('ec2', region_name='us-east-2')
    print('STOPPING: EC2 instance')
    client.stop_instances(InstanceIds=[instance_id])
    waiter = client.get_waiter('instance_stopped')
    print('Waiting for EC2 instance to stop')
    waiter.wait(InstanceIds=[instance_id])
    print('EC2 instance stopped')


if __name__ == '__main__':
    ec2_status = sys.argv[1].lower()
    try:
        if ec2_status == 'start':
            ec2_ip = start_test_instance()
            os.system('echo {} > /tmp/ec2_instance_ip'.format(ec2_ip))
        elif ec2_status == 'stop':
            stop_test_instance()
        else:
            print('Invalid status for EC2 machine')
    except Exception as e:
        print('Instance is not in correct state')
        exit()
