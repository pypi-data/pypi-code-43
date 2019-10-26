# coding=utf8

__author__ = 'Alexander.Li'

import logging
import os
import boto3
import oss2
import json
from secp256k1py import secp256k1


class Aws(object):
    def __init__(self, config):
        self.config = config
        self.sqs = boto3.resource('sqs',
                                  aws_access_key_id=config.get('AWS_KEY'),
                                  aws_secret_access_key=config.get('AWS_SECRET'),
                                  region_name=config.get('AWS_REGION'))
        self.client = boto3.client(
            'sqs',
            aws_access_key_id=config.get('AWS_KEY'),
            aws_secret_access_key=config.get('AWS_SECRET'),
            region_name=config.get('AWS_REGION'))

        self.sns = boto3.resource(
            'sns',
            aws_access_key_id=config.get('AWS_KEY'),
            aws_secret_access_key=config.get('AWS_SECRET'),
            region_name=config.get('AWS_REGION')
        )
        self.sns_client = boto3.client('sns',
                                        aws_access_key_id=config.get('AWS_KEY'),
                                        aws_secret_access_key=config.get('AWS_SECRET'),
                                        region_name=config.get('AWS_REGION')
                                       )

    def create_queue(self, name):
        """
        Create a sqs queue
        :param name:
        :return:
        """
        try:
            queue = self.sqs.get_queue_by_name(QueueName=name)
        except Exception:
            queue = self.sqs.create_queue(QueueName=name, Attributes={
                'DelaySeconds': '0',
                'MessageRetentionPeriod': '1209600',
                'MaximumMessageSize': '262144',
                'ReceiveMessageWaitTimeSeconds': '20',
            })
        return self.format_queue_url(queue)


    def delete_queue(self, name):
        queue = self.sqs.get_queue_by_name(QueueName=name)
        logging.info(self.sqs.delete_queue(self.format_queue_url(queue)))


    def with_url(self, name):
        queue = self.sqs.get_queue_by_name(QueueName=name)
        return self.format_queue_url(queue)

    def recv(self, name):
        queue = self.sqs.get_queue_by_name(QueueName=name)
        return self.client.receive_message(QueueUrl=self.format_queue_url(queue), WaitTimeSeconds=20, MaxNumberOfMessages=10)

    def rm_msg(self, name, handle):
        queue = self.sqs.get_queue_by_name(QueueName=name)
        self.client.delete_message(QueueUrl=self.format_queue_url(queue), ReceiptHandle=handle)

    def send_msg(self, url, body):
        logging.info('sento queue:%s', url)
        return self.client.send_message(
            QueueUrl=url,
            MessageBody=body
        )

    def format_queue_url(self, queue):
        seqs = queue.url.split('/')
        seqs[2] = 'sqs.%s.amazonaws.com' % self.config.get('AWS_REGION')
        return "/".join(seqs)

    def send_sns_to(self, arn, message):
        """
        final apns_dict = {
        'aps': {'alert': message, 'badge': 1, 'sound': 'apns_sound.caf'}
        };
        final apns_string = jsonEncode(apns_dict);
        final gcm_dict = {
        'notification': {'title': 'New message', 'body': message}
        };
        final gcm_string = jsonEncode(gcm_dict);
        final payload = {'default': message, 'APNS_SANDBOX': apns_string, 'APNS': apns_string, 'GCM': gcm_string};
        final payloadJson = jsonEncode(payload);
        """
        apns_dict = {
            'aps': {'alert': message, 'badge': 1, 'sound': 'apns_sound.caf'}
        }
        apns_string = json.dumps(apns_dict)
        gcm_dict = {
            'notification': {'title': 'New message', 'body': message}
        }
        gcm_string = json.dumps(gcm_dict)
        payload = {'default': message, 'APNS_SANDBOX': apns_string, 'APNS': apns_string, 'GCM': gcm_string}
        payloadJson = json.dumps(payload)

        try:
            platform_endpoint = self.sns.PlatformEndpoint(arn)
            platform_endpoint.publish(
                Message=payloadJson,
                MessageStructure='json',
                Subject='New Broadcast',
            )
        except Exception as e:
            logging.error(e)

    def delete_arn(self, arn):
        """
        删除arn
        :param arn:
        :return:
        """
        logging.info(self.sns_client.delete_endpoint(
            EndpointArn=arn
        ))


class Oss(object):
    def __init__(self, config, bucket):
        """
        # cn-hongkong
        :param config:
        :param bucket:
        """
        self.config = config
        auth = oss2.Auth(config.get('OSS_KEY'), config.get('OSS_SECRET'))
        self.bucket = oss2.Bucket(auth, 'http://oss-%s.aliyuncs.com' % config.get('OSS_REGION'), bucket)
        self.bucket_name = bucket

    def upload(self, file_name, file_content):
        self.bucket.put_object(file_name, file_content)
        return "https://%s.oss-%s.aliyuncs.com/%s" % (self.bucket_name, self.config.get('OSS_REGION'), file_name)


def keypair():
    """
    生成密钥对
    :return:
    """
    return secp256k1.make_keypair()


def generator_impl(name):
    base_public = input('Input Base Public Key:')
    aws_key = input('Input AWS ACCESS KEY:')
    aws_secret = input('Input AWS ACCESS SECREST:')
    aws_region = input('Input AWS REGION:')
    oss_key = input('Input OSS ACCESS KEY:')
    oss_secret = input('Input OSS ACCESS SECRET:')
    oss_region = input('Input OSS REGION:')
    nick_name = input('Input bot name:')
    avatar = input('Input avatar url:')
    keypair = secp256k1.make_keypair()
    local_config = {
        "AWS_KEY": aws_key,
        'AWS_SECRET': aws_secret,
        'AWS_REGION': aws_region,
        'OSS_KEY': oss_key,
        'OSS_SECRET': oss_secret,
        'OSS_REGION': oss_region,
        'BROKER_PRIVATE': str(keypair.privateKey),
        'BROKER_PUBLIC': str(keypair.publicKey),
        'NICK': nick_name,
        'AVATAR': avatar,
        'ID': name
    }
    aws = Aws(local_config)
    public_config = {
        'BROKER_PUBLIC': "%s" % keypair.publicKey,
        'ENDPOINT_URL': aws.create_queue(name),
        "AWS_KEY": aws_key,
        'AWS_SECRET': aws_secret,
        'AWS_REGION': aws_region,
        'OSS_KEY': oss_key,
        'OSS_SECRET': oss_secret,
        'OSS_REGION': oss_region,
        'NICK': nick_name,
        'AVATAR': avatar,
        'BID': name
    }
    publicKey = secp256k1.PublicKey.restore(base_public)

    sec = keypair.privateKey.generate_secret(publicKey)

    enc = publicKey.encrypt(keypair.privateKey, json.dumps(public_config).encode())
    oss = Oss(local_config, 'messenger')
    enc.update({'pk': "%s" % keypair.publicKey})
    file_key = 'config/%s.json' % name
    config_url = oss.upload(file_key, json.dumps(enc))
    local_path = os.path.join(os.getcwd(), '.broker_config')
    with open(local_path, 'w') as f:
        f.write(json.dumps(local_config, indent=' '))
        f.close()
    return config_url
