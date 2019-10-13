# -*- coding: utf-8 -*-

import requests
import json
import logging
import time
from threading import Timer
from functools import wraps
import urllib.parse
import re

from .files import *
from .economy import *

from .service import read_description, find_my_ip
from .access_control import read_policies, build_access_request, operations_to_restful_methods

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

class BrokerClient():

    # provider functions

    def register(service_desc, retries=0, max_retries=3):
        registry_url = service_desc["broker"] + "/api/v2/registry"
        logging.info("Will register service %s at %s" % (service_desc["@id"], registry_url))
        try:
            response = requests.post(registry_url, json=service_desc)
            if response.status_code == 200:
                logging.info("Registered service %s" % (service_desc["@type"]))
                return True
        except Exception as e:
            if retries < max_retries:
                retries += 1
                sleep_time = 2 ** retries
                logging.error("Registry failed: no broker found. Will retry (%s) in %s seconds" % (retries, sleep_time))
                time.sleep(retries)
                return BrokerClient.register(service_desc, retries)
            else:
                logging.error("No available broker at %s to register at" % registry_url)
                return False

    def setup_policies(service_desc, policies):
        policies_url = service_desc["broker"] + "/api/v2/security/policies"
        try:
            response = requests.post(policies_url, json=policies)
            policy_names = list(map(lambda p: p["name"], policies))
            if response.status_code == 200:
                logging.info("Added policies %s" % (policy_names))
                return True
            else:
                logging.error("Error adding policies %s. Status = %d" % (policy_names, response.status_code))
                return False
        except Exception as e:
            logging.debug(e)
            logging.error("No available broker at %s to add policies" % policies_url)
            return False

    def authorize(service_desc, access_request):
        pdp_url = service_desc["broker"] + "/api/v2/security/authorizations"
        try:
            result = requests.post(pdp_url, json=access_request)
            if result.status_code == 200:
                logging.debug("Request was authorized: %s" % access_request)
                return True, None
            else:
                logging.debug("Request was denied: %s" % access_request)
                return False, {"error": "access denied", "user_attrs": access_request["user_attrs"]}
        except Exception as e:
            logging.error(e)
            return False, {"error": str(e), "user_attrs": access_request["user_attrs"]}

    # provider and consumer functions

    def discover(service_desc, query={"@type": "*"}):
        discovery_url = service_desc["broker"] + "/api/v2/discovery-requests"
        try:
            logging.info("Discovery query %s" % query)
            response = requests.post(discovery_url, json=query)
            response_json = response.json()
            logging.info("Discovered services are %s" % list(map(lambda c: c["description"]["@id"], response_json["candidates"])))
            return list(map(lambda c: c["description"], response_json["candidates"]))
        except Exception as e:
            logging.debug("The discovery request at %s did not work" % discovery_url)
            logging.debug(e)
            return []

    def contract(service_desc, data={"query": {"@type": "*"}}):
        contract_url = service_desc["broker"] + "/api/v2/contracts"
        try:
            logging.info("Running contract for %s" % data)
            response = requests.post(contract_url, json=data)
            location = response.headers['location']
            contract = response.json()
            logging.info("State dict created is %s '\n' And the transaction signed\
                         must be sent to location %s" % (json.dumps(contract),location))
            return (contract, location)
        except Exception as e:
            logging.debug("The contract request at %s did not work" % contract_url)
            return None

    def sign_and_send_tx(service_desc, keys, contract, location):
        signed_tx = sign_tx(contract['tx'], keys)
        logging.debug("Signed tx: %s" % (signed_tx))
        url = service_desc["broker"] + location
        if signed_tx and location:
            try:
                response = requests.put(url, json={"tx": signed_tx})
                if response.status_code == 200:
                    contract = BrokerClient.wait_sla_establishment(url)
                    logging.info("The negotiation is complete")
                    return contract
            except Exception as e:
                logging.debug(e)
                logging.info("Sending the signed transaction did not work")
                return None
        else:
            logging.error("signed_tx: %s\nlocation: %s" % (signed_tx, location))
            return None

    def wait_sla_establishment(url):
        status, max_retries, retries = 0, 3, 0
        block_period = 3
        while status != 200 and retries < max_retries:
            response = requests.get(url)
            status = response.status_code
            retries += 1
            if status != 200:
                time.sleep(block_period)
        if retries <= max_retries:
            return response.json()
        else:
            return None

    def smart_use(contract, method=None, data=None, token=None):
        provider_id = contract["sla"][0]["provider_id"]
        provider_description = contract["sla"][0]["provider"]
        entry = provider_description["operations"][0]["entry"]

        operations = contract["tx"]["content"]["operations"]
        if "delegate" not in operations:
            method = operations_to_restful_methods()[operations]

        user_attrs = {"swarm:Id": contract["tx"]["content"]["consumer_id"]}

        if method:
            return BrokerClient.use(method, provider_id + entry, data, token, user_attrs)
        else:
            raise "Could not infer method (%s)" % (method)

    def use(method, url, data=None, token=None, user_attrs={}):
        if token:
            user_attrs["swarm:Token"] = token
        headers = {'x-user-attrs': urllib.parse.urlencode(user_attrs)}

        logging.debug([method, url, headers, data])
        response = requests.request(method, url, headers=headers, json=data)
        logging.debug("Request to %s is %s" % (url, response.status_code))
        return response

    def send_reputation(service_desc, reputation_tx, location):
        if not location:
            logging.error("Location cannot be empty")
            return False

        url = service_desc["broker"] + location + "/reputation"
        logging.debug("Will send reputation_tx %s to %s" % (reputation_tx, url))

        try:
            response = requests.post(url, json={"reputation_tx": reputation_tx})
            if response.status_code == 200:
                logging.info("The reputation_tx was sent")
                return response.json()
        except Exception as e:
            logging.debug(e)
            logging.info("Sending reputation_tx did not work")
            return None

    def unregister(service_desc):
        quoted_id = urllib.parse.quote(service_desc["@id"], safe="")
        registry_url = service_desc["broker"] + "/api/v2/registry/" + quoted_id
        response = requests.delete(registry_url)
        if response.status_code == 200:
            logging.info("De-registered service %s" % (service_desc["@id"]))
