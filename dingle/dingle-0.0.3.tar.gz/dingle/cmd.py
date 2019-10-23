# -*- coding: utf-8 -*-
'''
Command line interface for testing dingtalk.
'''
import json
import pprint
import logging
import argparse
import importlib
import inspect
from .util.conf import get_config, load_config
from .util.log import json_log
from .util.api import client
from .core.token import TokenManager


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-A", "--access-token", default="",
                        help="Overwrite dingtalk access token.")
    parser.add_argument("-C", "--conf", default="dingtalk.json",
                        help="Specify the configuration file.")
    parser.add_argument("-v", "--verbose", action='store_true',
                        help="Use verbose output.")
    parser.add_argument("-vv", "--verbose2", action='store_true',
                        help="Use verbose2 output.")
    parser.add_argument("--api", action="store_true",
                        help="Call an api")
    parser.add_argument("--top-api", action="store_true",
                        help="Call an top api")
    parser.add_argument("--call-func", action="store_true",
                        help="Call a function in dingtalk module. ")
    parser.add_argument("options", default=[], nargs="*")
    return parser.parse_args()


def api_call(method, path, data=None):
    kwargs = {}
    if method == 'GET':
        if data:
            kwargs['params'] = json.loads(data)
        else:
            kwargs['params'] = {}
    resp = client.call(method, path, **kwargs)
    print(resp.content)
    return resp


def top_api_call(method, data=None):
    kwargs = {}
    if data:
        kwargs.update(json.loads(data))
    resp = client.top_call(method, **kwargs)
    print(resp.content)
    return resp


def dingtalk_func_call(module, method, *args):
    module_name = 'dingle.dingtalk.%s' % module
    imported = importlib.import_module(module_name)
    func = getattr(imported, method)
    spec = inspect.getfullargspec(func)
    args_count = len(spec.args) - len(spec.defaults or [])
    if len(args) > args_count:
        kwargs = json.loads(args[args_count])
    else:
        kwargs = {}
    print(json.dumps(func(*args[:args_count], **kwargs),
                     indent=4,
                     ensure_ascii=False))


def main():
    logging.basicConfig(level=logging.INFO)
    args = vars(parse_args())
    options = args.get("options")
    config = load_config(config_file=args.get('conf'))
    if args.get('verbose'):
        config['verbose'] = True
    if args.get('verbose2'):
        config['verbose2'] = True
    json_log(args, 'args')
    manager = TokenManager(app_key=config.get('app_key'),
                           app_secret=config.get('app_secret'),
                           corp_id=config.get('corp_id'),
                           corp_secret=config.get('corp_secret'))
    client.set_manager(manager)
    if args.get('access_token'):
        manager.set_access_token(args['access_token'])
    if args.get('api'):
        api_call(*options)
    if args.get('top_api'):
        top_api_call(*options)
    if args.get('call_func'):
        dingtalk_func_call(*options)


if __name__ == '__main__':
    main()
