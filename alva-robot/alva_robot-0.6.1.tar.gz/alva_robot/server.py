# coding=utf8

__author__ = 'Alexander.Li'

import random
import uuid
import json
import pollworker
import logging
import base64
from secp256k1py import secp256k1
from errorbuster import formatError
from .functions import Aws

rd_num = random.randint(1000000, 9999999)

def load_config():
    with open('.broker_config', 'r') as f:
        return json.loads(f.read())


class Server(object):
    def __init__(self):
        self.config = load_config()
        self.aws = Aws(self.config)

    def poll(self):
        messages = self.aws.recv(self.config.get('ID'))
        if messages.get('Messages'):
            return {'messages': messages.get('Messages'), 'config': self.config}
        else:
            #logging.info('got no message')
            pass


class Command(object):
    def __init__(self, commandDict):
        self.data = commandDict

    @property
    def unique_id(self):
        return self.data.get('unique_id')

    @property
    def name(self):
        return self.data.get('name')

    @property
    def params(self):
        return self.data.get('params')


class Message(object):
    def __init__(self, messageDict):
        self.data = messageDict

    @property
    def unique_id(self):
        return self.data.get('unique_id')

    @property
    def content_type(self):
        return self.data.get('content-type')

    @property
    def action(self):
        return self.data.get('action')

    @property
    def text(self):
        if self.content_type == "text":
            return self.data.get('body').get('content')
        return ''

    def __repr__(self):
        return "mid:%s txt:%s" % (self.unique_id, self.text)


class Sender(object):
    def __init__(self, senderDict):
        self.data = senderDict

    @property
    def host_id(self):
        return self.data.get('host_id')

    @property
    def user_id(self):
        return self.data.get('user_id')

    @property
    def nick_name(self):
        return self.data.get('nick_name')

    @property
    def avatar(self):
        return self.data.get('avatar')

    @property
    def public_key(self):
        return self.data.get('public_key')

    @property
    def endpoint(self):
        return self.data.get('endpoint')

    @property
    def arn(self):
        return self.data.get('arn')

    @property
    def info(self):
        return self.data.get('info')

    @property
    def location(self):
        return self.data.get('location')


class MRequest(object):
    def __init__(self, raw_message, new_version=False, enc_raw=None):
        self.data = json.loads(raw_message)
        self.new_version = new_version
        self.sender = Sender(self.data.get('sender'))
        self.dispatch = False
        self.enc_data = enc_raw
        if "zid" in self.data:
            logging.info('zone messsage:%s' % self.data.get('zid'))
            self.dispatch = True
            self.zone_id = self.data.get('zid')
        else:
            logging.info('normal messsage:%s' % self.data.get('zid'))
            self.dispatch = False
            self.zone_id = ''
        if "content" in self.data:
            self.message = Message(self.data.get('content'))
        else:
            self.message = None
        if "command" in self.data:
            self.command = Command(self.data.get('command'))
        else:
            self.command = None

    def __repr__(self):
        return "req user:%s msg:%s" % (self.sender.user_id, self.message)

    def dispatch_response(self, target):
        return CastResponse(self.data, target)


def send_command_to(config, aws, endpoint, response):
    resp = response.make_response(config, aws)
    logging.info(aws.send_msg(endpoint, resp))
    logging.info('command %s sended', response.data)
    if isinstance(response, MessageResponse) or isinstance(response, CastResponse):
        # 如果是Message消息就发APNS推送
        # msg = response.data.get('content').get('body').get('content')[:72]
        resp2 = aws.send_sns_to(response.arn, 'You have a new message')
        logging.info('push notification sended:%s with arn:%s', resp2, response.arn)


class Response(object):
    def __init__(self, basic_dict, tartget):
        self.data = basic_dict
        self.new_version = False
        self.pubkey = tartget['pubkey']
        self.endpoint = tartget['endpoint']
        self.arn = tartget['arn']

    def set_pair(self, pubkey, endpoint):
        self.pubkey = pubkey
        self.endpoint = endpoint
        return self

    def bin_resp(self, data, pk):
        data_arr = bytearray(pk.encode())
        data_arr.extend(data)
        return base64.urlsafe_b64encode(data_arr).decode('utf8')

    def make_response(self, config, aws):
        self.data.update(
            {
                'sender': {
                    'host_id': 'miaomi',
                    'user_id': config.get('ID'),
                    'nick_name': config.get('NICK'),
                    'info': config.get('INFO'),
                    'up_version': "%s" % rd_num
                }
            }
        )
        keypair = secp256k1.make_keypair()
        targetPublicKey = secp256k1.PublicKey.restore(self.pubkey)
        enced = targetPublicKey.encrypt(keypair.privateKey, json.dumps(self.data).encode(), raw=True)
        return self.bin_resp(enced['enc'], str(keypair.publicKey))


class CastResponse(Response):
    def __init__(self, message, target):
        super(CastResponse, self).__init__(message, target)


class MessageResponse(Response):
    def __init__(self, text, target):
        message = {
            'content': {
                'unique_id': uuid.uuid4().hex,
                'content-type': 'text',
                'action': 'new',
                'body': {
                    'content': text
                }
            }
        }
        super(MessageResponse, self).__init__(message, target)

    def with_command(self, name, *params):
        # 加入命令
        self.data.update({
            'command': {
                'name': name,
                'params': params
            }
        })

    def with_multi_command(self, *commands):
        self.data.update({
            'pipe': [
                {
                    'name': cmd[0],
                    'params': cmd[1:]
                }
                for cmd in commands
            ]
        })


class BroadCastResponse(Response):
    def __init__(self, text, sender_id, target):
        message = {
            'content': {
                'unique_id': uuid.uuid4().hex,
                'content-type': 'broadcast',
                'action': 'new',
                'body': {
                    'sender_id': sender_id,
                    'content': text
                }
            }
        }
        super(BroadCastResponse, self).__init__(message, target)

class CommandResponse(Response):
    def __init__(self, name, *params, target=None):
        command = {
            'command': {
                'name': name,
                'params': params
            }
        }
        super(CommandResponse, self).__init__(command, target)

class MultiCommandResponse(Response):
    def __init__(self, *commands, target=None):
        command = {
            'pipe': [
                {
                    'name': cmd[0],
                    'params': cmd[1:]
                }
                for cmd in commands
            ]
        }
        super(MultiCommandResponse, self).__init__(command, target)


class ContackResponse(Response):
    def __init__(self, users, target):
        message = {
            'content': {
                'unique_id': uuid.uuid4().hex,
                'content-type': 'contacts',
                'action': 'new',
                'body': {
                    'contacts': [
                        {
                            'id': user.get('user_id'),
                            'nick_name': user.get('nick_name'),
                            'cover_type': user.get('cover_type')
                        }
                        for user in users
                    ]
                }
            }
        }
        super(ContackResponse, self).__init__(message, target)


executors = {}


MESSAGE_HANDLER = 'MESSAGE_HANDLER'


def api(cmd_name):
    def decorator(f):
        executors[cmd_name] = f
        return f
    return decorator


def process_message(config, message):
    req = None
    privateKey = secp256k1.PrivateKey.restore(config.get('BROKER_PRIVATE'))
    if isinstance(message, dict):
        body = message
        publicKey = secp256k1.PublicKey.restore(body.get('public_key'))
        iv = body.get('iv')
        enc = body.get('encoded')
        try:
            raw = privateKey.decrypt(publicKey, enc, iv)
            req = MRequest(raw)
        except Exception as e:
            logging.error(formatError(e))
    else:
        #logging.info(f"get b64:{message.encode()}")
        raw_message = base64.decodebytes(message.encode())
        pk = raw_message[:66]
        #logging.info(f'key is {pk}, len:{len(pk)}')
        bytes_data = raw_message[66:]
        #logging.info(f'data length is:{len(bytes_data)}')
        publicKey = secp256k1.PublicKey.restore(pk.decode())
        try:
            raw = privateKey.decrypt(publicKey, bytes(bytes_data), None)
            logging.info(f"get message:${raw[:100]}")
            req = MRequest(raw, new_version=True, enc_raw=message)
        except Exception as e:
            logging.error(formatError(e))
    return req


def worker(pid, message):
    messages = message.get('messages')
    config = message.get('config')
    aws = Aws(config)
    for msg in messages:
        body = json.loads(msg.get('Body'))
        req = process_message(config, body)
        aws.rm_msg(config.get('ID'), msg.get('ReceiptHandle'))
        resp = None
        try:
            if req.command:
                if req.command.name in executors:
                    resp = executors[req.command.name](config, aws, req)
            if req.message:
                if req.message.action == "new":
                    if MESSAGE_HANDLER in executors:
                        resp = executors[MESSAGE_HANDLER](config, aws, req)
            if req.dispatch:
                if MESSAGE_HANDLER in executors:
                    resp = executors[MESSAGE_HANDLER](config, aws, req)
        except Exception as e:
            logging.error(e)
        if resp:
            response_text = resp.make_response(config, aws)
            aws.send_msg(resp.endpoint, response_text)
            logging.info(f'response:{resp.data}')
            logging.info('message: sended!')


def start(workers=0):
    pollworker.regist_worker(worker)
    pollworker.regist_poller(Server())
    if workers:
        pollworker.start(workers)
    else:
        pollworker.start()
