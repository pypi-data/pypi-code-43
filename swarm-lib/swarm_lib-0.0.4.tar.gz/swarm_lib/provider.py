import logging
import urllib.parse
from functools import wraps
from urllib.parse import urlparse
import sys, signal

from .broker_client import BrokerClient
from .agent import Agent
from .service import find_my_ip, read_description
from .access_control import read_policies, build_access_request

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

class Provider(Agent):
    def __init__(self, **kwargs):
        logging.info("Initializing provider with args: %s" % kwargs)
        super().__init__(**kwargs)
        self.set_exit_trap()
        if "description_file" in kwargs.keys():
            self.description_file = kwargs["description_file"]
            self.description = read_description(self.description_file)
            self.update_ip()

        if "policies_file" in kwargs.keys():
            self.policies_file = kwargs["policies_file"]
            self.policies = read_policies(self.description, self.policies_file)

    def update_ip(self):
        my_ip = find_my_ip()
        self.description["@id"] = self.replace_ip(self.description["@id"], my_ip)
        self.description["broker"] = self.replace_ip(self.description["broker"], my_ip)

    def replace_ip(self, url, ip):
        parsed_url = urlparse(url)
        parsed_url = parsed_url._replace(netloc="%s:%s" % (ip, parsed_url.port))
        return parsed_url.geturl()

    def join_swarm(self):
        return self.register() and self.setup_policies()

    def register(self):
        return BrokerClient.register(self.description)

    def setup_policies(self):
        return BrokerClient.setup_policies(self.description, self.policies)

    def enforce_authorization(self, f):
        @wraps(f)
        def wrap(*args, **kwargs):
            from flask import request, jsonify
            access_request = build_access_request(self.description, request.headers, request.method)
            allowed, error = BrokerClient.authorize(self.description, access_request)
            if allowed:
                return f(*args, **kwargs)
            else:
                return jsonify(error)
        return wrap

    def port(self):
        return urlparse(self.description["@id"]).port

    def handle_exit(self, sig, frame):
        BrokerClient.unregister(self.description)
        sys.exit(0)

    def set_exit_trap(self):
        signal.signal(signal.SIGINT, self.handle_exit)

    def __repr__(self):
        rep = super().__repr__()
        rep["policies"] = list(map(lambda p: p["name"], self.policies))
        return rep
