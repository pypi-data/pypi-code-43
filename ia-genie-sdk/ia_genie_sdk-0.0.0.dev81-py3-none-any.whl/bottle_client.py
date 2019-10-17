"""Implements the "Bottle" interface."""
import json

import requests

from ialib.genie_metalanguage import CLEAR_ALL_MEMORY, CLEAR_WM, LEARN
from ialib.genome_info import Genome


class BottleClient:
    """Interface for interacting with bottles."""
    def __init__(self, bottle_info):
        """
        Provide bottle information in a dictionary.

        ex:
        from ialib.BottleClient import BottleClient

        bottle_info = {'api_key': 'ABCD-1234',
                    'name': 'genie-bottle',
                    'domain': 'intelligent-artifacts.com',
                    'secure': False}

        bottle = BottleClient(bottle_info)
        bottle.connect()

        bottle.setIngressNodes(['P1'])
        bottle.setQueryNodes(['P1'])

        """
        self.genome = None
        self.bottle_info = bottle_info
        self.name = bottle_info['name']
        self.domain = bottle_info['domain']
        self.api_key = bottle_info['api_key']
        self.ingress_nodes = []
        self.query_nodes = []
        self.all_nodes = []
        self.failures = []
        self.system_failures = []
        self._connected = False
        self.headers = {'content-type': 'application/json'}
        self.genome = None
        self.genie = None
        if 'secure' not in self.bottle_info or self.bottle_info['secure']:
            self.secure = True
            self.url = 'https://{name}.{domain}/api'.format(**self.bottle_info)
        else:
            self.secure = False
            self.url = 'http://{name}.{domain}/api'.format(**self.bottle_info)

    def __repr__(self):
        return '<{name}.{domain}| secure: %r, connected: %s, genie: %s, \
                  ingress_nodes: %i, query_nodes: %i, failures: %i>'.format(
                      **self.bottle_info) % (
                          self.secure, self._connected, self.genie, len(self.ingress_nodes), len(self.query_nodes), len(self.failures))

    def connect(self):
        """Grabs the bottle's genie's genome for node definitions."""
        response_data = requests.post(self.url, data=json.dumps(
            {"method": "connect", "params": {"api_key": self.api_key}, "jsonrpc": "2.0", "id": 1}),
                                      headers=self.headers).json()
        if 'result' not in response_data:
            self._connected = False
            raise Exception("Connection failed!", response_data)

        result = response_data['result']
        self.genome = Genome(result['genome'])
        self.genie = result['genome']['agent']
        self.all_nodes = [{"name": i['name'], "id": i['id']} for i in self.genome.primitives.values()]
        if result['connection'] == 'okay':
            self._connected = True
        else:
            self._connected = False

        return {'connection': result['connection'], 'genie': result['genie']}

    def set_ingress_nodes(self, nodes=None):
        """Use list of primitive names to define where data will be sent."""
        if nodes is None:
            nodes = []
        self.ingress_nodes = [{'id': self.genome.primitive_map[node], 'name': node} for node in nodes]

    def set_query_nodes(self, nodes=None):
        """Use list of primitive names to define which nodes should return answers."""
        if nodes is None:
            nodes = []
        self.query_nodes = [{'id': self.genome.primitive_map[node], 'name': node} for node in nodes]

    def _query(self, query, data=None):
        """Internal helper function to make an RPC call with the given *query* and *data*."""
        result = []
        for node in self.query_nodes:
            try:
                if data:
                    response = requests.post(self.url, data=json.dumps(
                        {"method": query, "params": {"api_key": self.api_key, "primitive_id": node['id'], 'data': data},
                         "jsonrpc": "2.0", "id": 1}), headers=self.headers).json()['result']
                else:
                    response = requests.post(self.url, data=json.dumps(
                        {"method": query, "params": {"api_key": self.api_key, "primitive_id": node['id']},
                         "jsonrpc": "2.0", "id": 1}), headers=self.headers).json()['result']
                result.append({node['name']: response})
            except Exception as exception:
                self.failures.append({node['name']: exception})
                raise Exception("Query Failure:", {node['name']: exception})
        return result

    def query(self, node, query, data=None):
        """Direct to bottle RPC call with the given *query* and *data*.
        Unlike the other SDK functions, this does not use Genie Data Metalanguage for the calls.
        Each call is sent only to the specific primitive, unless Genie Data Metalanguage is used in the observe."""
        result = []
        try:
            if data:
                response = requests.post(self.url, data=json.dumps(
                    {"method": query, "params": {"api_key": self.api_key, "primitive_id": self.genome.primitive_map[node], 'data': data},
                        "jsonrpc": "2.0", "id": 1}), headers=self.headers).json()['result']
            else:
                response = requests.post(self.url, data=json.dumps(
                    {"method": query, "params": {"api_key": self.api_key, "primitive_id": self.genome.primitive_map[node]},
                        "jsonrpc": "2.0", "id": 1}), headers=self.headers).json()['result']
            result.append({node: response})
        except Exception as exception:
            self.failures.append({node: exception})
            raise Exception("Query Failure:", {node: exception})
        return result

    def observe(self, data=None):
        """Exclusively uses the 'observe' call.  All commands must be provided via Genie Metalanguage data."""
        result = []
        for node in self.ingress_nodes:
            try:
                response = requests.post(self.url, data=json.dumps(
                    {"method": "observe", "params": {"api_key": self.api_key, "primitive_id": node['id'], 'data': data},
                     "jsonrpc": "2.0", "id": 1}), headers=self.headers).json()['result']
                result.append({node['name']: response})
            except Exception as exception:
                self.failures.append({node['name']: exception})
                raise Exception("Observe Failure:", {node['name']: exception})
        return result

    def observe_classification(self, data=None):
        """
        Best practice is to send a classification to all ingress and query nodes as a singular symbol in the last event.
        This function does that for us.
        """
        result = []
        for node in self.query_nodes:
            try:
                response = requests.post(self.url, data=json.dumps(
                    {"method": "observe", "params": {"api_key": self.api_key, "primitive_id": node['id'], 'data': data},
                     "jsonrpc": "2.0", "id": 1}), headers=self.headers).json()['result']
                result.append({node['name']: response})
            except Exception as exception:
                self.failures.append({node['name']: exception})
                raise Exception("Observe Failure:", {node['name']: exception})
        return result

    def show_status(self):
        """Return the current status of the bottle."""
        result = []
        for node in self.all_nodes:
            try:
                response = requests.post(self.url, data=json.dumps(
                    {"method": "showStatus", "params": {"api_key": self.api_key, "primitive_id": node['id']},
                     "jsonrpc": "2.0", "id": 1}), headers=self.headers).json()['result']
                result.append({node['name']: response})
            except Exception as exception:
                self.failures.append({node['name']: exception})
                raise Exception("Query Failure:", {node['name']: exception})
        return result

    def learn(self):
        """Return the learn results."""
        result = []
        for node in self.ingress_nodes:
            try:
                response = requests.post(
                    self.url,
                    data=json.dumps(
                        {
                            "method": "observe",
                            "params": {
                                "api_key": self.api_key,
                                "primitive_id": node['id'],
                                'data': LEARN
                            },
                            "jsonrpc": "2.0",
                            "id": 1
                        }
                    ),
                    headers=self.headers).json()['result']
                result.append({node['name']: response})
            except Exception as exception:
                self.failures.append({node['name']: exception})
                raise Exception("Query Failure:", {node['name']: exception})
        return result

    def get_wm(self):
        """Return information about Working Memory."""
        result = []
        for node in self.all_nodes:
            try:
                response = requests.post(self.url, data=json.dumps(
                    {"method": "getWM", "params": {"api_key": self.api_key, "primitive_id": node['id']},
                     "jsonrpc": "2.0", "id": 1}), headers=self.headers).json()['result']
                result.append({node['name']: response})
            except Exception as exception:
                self.failures.append({node['name']: exception})
                raise Exception("Query Failure:", {node['name']: exception})
        return result

    def get_predictions(self):
        """Return prediction result data."""
        result = []
        for node in self.query_nodes:
            try:
                response = requests.post(self.url, data=json.dumps(
                    {"method": "getPredictions", "params": {"api_key": self.api_key, "primitive_id": node['id']},
                     "jsonrpc": "2.0", "id": 1}), headers=self.headers).json()['result']
                result.append({node['name']: response})
            except Exception as exception:
                self.failures.append({node['name']: exception})
                raise Exception("Query Failure:", {node['name']: exception})
        return result

    def clear_wm(self):
        """Clear the Working Memory of the Genie."""
        result = []
        for node in self.ingress_nodes:
            try:
                response = requests.post(
                    self.url,
                    data=json.dumps(
                        {
                            "method": "observe",
                            "params": {
                                "api_key": self.api_key,
                                "primitive_id": node['id'],
                                'data': CLEAR_WM
                            },
                            "jsonrpc": "2.0",
                            "id": 1
                        }
                    ),
                    headers=self.headers).json()['result']
                result.append({node['name']: response})
            except Exception as exception:
                self.failures.append({node['name']: exception})
                raise Exception("Query Failure:", {node['name']: exception})
        return result

    def clear_all_memory(self):
        """Clear both the Working Memory and persisted memory."""
        result = []
        for node in self.ingress_nodes:
            try:
                response = requests.post(
                    self.url,
                    data=json.dumps(
                        {
                            "method": "observe",
                            "params": {
                                "api_key": self.api_key,
                                "primitive_id": node['id'],
                                'data': CLEAR_ALL_MEMORY
                            },
                            "jsonrpc": "2.0",
                            "id": 1
                        }
                    ),
                    headers=self.headers).json()['result']
                result.append({node['name']: response})
            except Exception as exception:
                self.failures.append({node['name']: exception})
                raise Exception("Query Failure:", {node['name']: exception})
        return result

    def get_percept_data(self):
        """Return percept data."""
        result = []
        for node in self.query_nodes:
            try:
                response = requests.post(self.url, data=json.dumps(
                    {"method": "getPerceptData", "params": {"api_key": self.api_key, "primitive_id": node['id']},
                     "jsonrpc": "2.0", "id": 1}), headers=self.headers).json()['result']
                result.append({node['name']: response})
            except Exception as exception:
                self.failures.append({node['name']: exception})
                raise Exception("Query Failure:", {node['name']: exception})
        return result

    def get_cognition_data(self):
        """Return cognition data."""
        result = []
        for node in self.query_nodes:
            try:
                response = requests.post(self.url, data=json.dumps(
                    {"method": "getCognitionData", "params": {"api_key": self.api_key, "primitive_id": node['id']},
                     "jsonrpc": "2.0", "id": 1}), headers=self.headers).json()['result']
                result.append({node['name']: response})
            except Exception as exception:
                self.failures.append({node['name']: exception})
                raise Exception("Query Failure:", {node['name']: exception})
        return result

    def get_cogitated(self):
        """Return cogitated data."""
        result = []
        for node in self.query_nodes:
            try:
                response = requests.post(self.url, data=json.dumps(
                    {"method": "getCogitated", "params": {"api_key": self.api_key, "primitive_id": node['id']},
                     "jsonrpc": "2.0", "id": 1}), headers=self.headers).json()['result']
                result.append({node['name']: response})
            except Exception as exception:
                self.failures.append({node['name']: exception})
                raise Exception("Query Failure:", {node['name']: exception})
        return result

    def get_decision_table(self):
        """Return a decision table."""
        result = []
        for node in self.query_nodes:
            try:
                response = requests.post(self.url, data=json.dumps(
                    {"method": "getDecisionTable", "params": {"api_key": self.api_key, "primitive_id": node['id']},
                     "jsonrpc": "2.0", "id": 1}), headers=self.headers).json()['result']
                result.append({node['name']: response})
            except Exception as exception:
                self.failures.append({node['name']: exception})
                raise Exception("Query Failure:", {node['name']: exception})
        return result

    def get_action_data(self):
        """Return action data."""
        result = []
        for node in self.query_nodes:
            try:
                response = requests.post(self.url, data=json.dumps(
                    {"method": "getActionData", "params": {"api_key": self.api_key, "primitive_id": node['id']},
                     "jsonrpc": "2.0", "id": 1}), headers=self.headers).json()['result']
                result.append({node['name']: response})
            except Exception as exception:
                self.failures.append({node['name']: exception})
                raise Exception("Query Failure:", {node['name']: exception})
        return result

    def change_genes(self, gene_data):
        """
        Use primitive names.
        This will do live updates to an existing agent, rather than stopping an agent and starting a new one as per 'injectGenome'.
        gene_data of form:

            {node-name: {gene: value}}

        where node-id is the ID of a primitive or manipulative.

        Only works on primitive nodes at this time.
        """
        self.genome.change_genes(gene_data)
        result = []
        for node, updates in gene_data.keys():  ## only primitive nodes at this time.
            for gene, value in updates.items():
                response = requests.post(self.url % (self.genome.primitive_map[node]),
                                         json={'api_key': self.api_key, 'query': 'updateGene',
                                               'data': {gene: value}}).json()
                if 'error' in response or response != 'updated-genes':
                    self.system_failures.append({node: response})
                    print("System Failure:", {node: response})
                result.append({node: response})
        return result
