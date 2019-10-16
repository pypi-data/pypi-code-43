import json

from .expectation import Expectation
from .open_api_schema import OpenAPISchema
from .scenario import Scenario


class Converter(object):

	def __init__(self):
		self.scenarios = ''
		self.spec = {}
		self.swagger = {}
		self.currentPath = None
		self.currentOperation = {}
		self.currentStatusCode = {}
		self.expectations = []
		self.currentMatchingScenarios = []

	def set_scenarios(self, scenarios):
		if scenarios is not None and len(scenarios) > 0:
			self.scenarios = []
			for scenario in json.loads(scenarios)['scenarios']:
				if len(scenario) == 4:
					self.scenarios.append(Scenario(scenario[0], scenario[1], scenario[2], json.loads(scenario[3])))
				else:
					self.scenarios.append(Scenario(scenario[0], scenario[1], scenario[2]))


	def convert_opai(self, oapi):
		self.swagger_object(oapi)

	# https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#swagger-object
	def swagger_object(self, swagger):
		if 'consumes' in swagger:
			self.swagger['consumes'] = swagger['consumes']

		if 'produces' in swagger:
			self.swagger['produces'] = swagger['produces']

		if 'paths' in swagger:
			self.paths_object(swagger['paths'])

	# https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#paths-object
	def paths_object(self, paths):
		for path_key, path_value in paths.items():
			self.currentPath = path_key
			for operation_key, operation_value in path_value.items():
				self.currentOperation = {}
				self.currentStatusCode = {}

				self.currentOperation['operation'] = operation_key
				self.operation_object(operation_value)
				#end of current operation, so create expectation and reset current operation
				self.create_expectation()

	# https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#operation-object
	def operation_object(self, operation):
		if 'consumes' in operation:
			self.currentOperation['consumes'] = operation['consumes']

		if 'provides' in operation:
			self.currentOperation['provides'] = operation['provides']

		#if 'parameters' in operation:
		#	for parameter in operation['parameters']:
		#		if 'in' in parameter and parameter['in'] == 'body' and 'schema' in parameter:
		#			print(parameter['schema'])

		if 'responses' in operation:
			self.responses_object(operation['responses'])

	# https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#responses-object
	def responses_object(self, responses):
		responses = {int(key):value for key, value in responses.items()}
		statusCodes = responses.keys()
		#TODO: warning or error if status code of the scenarios does not exist
		if (len(statusCodes)):
			if len(self.scenarios) > 0:
				# check if the path and operation combination of the current scenario exists in the contract, it is in the matching scenatios if yes
				matching_scenarios = list(filter(lambda scenario: scenario.matches(self.currentPath, self.currentOperation['operation']), self.scenarios))
				# check if a match exists (path & operation match) and check if the status code of the scenario exists in the contract
				# use the first status code if not
				if len(matching_scenarios) == 1 and matching_scenarios[0].get_expected_response()['responseCode'] in statusCodes:
					statusCode = matching_scenarios[0].get_expected_response()['responseCode']
					self.currentMatchingScenarios = matching_scenarios
				else:
					statusCode = 0
			else:
				statusCode = list(statusCodes)[0]
			if statusCode > 0:
				response_value = responses[statusCode]
				self.currentStatusCode['statusCode'] = statusCode
				self.response_object(response_value)

	# https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#response-object
	def response_object(self, response):
		if 'headers' in response:
			self.currentStatusCode['headers'] = response['headers']
			self.example_object(response['headers'])

		if 'examples' in response:
			self.currentStatusCode['examples'] = response['examples']
			self.example_object(response['examples'])

		if 'schema' in response:
			self.currentStatusCode['schema'] = response['schema']

	# https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#headersObject
	def headers_object(self, example):
		return

	# https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#example-object
	def example_object(self, example):
		return

	# https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#schema-object
	def schema_object(self, schema):
		return

	# reshape headers to one dictionary
	def __headers_reshape(self, headers):
		reshapend_headers = {}
		for header_key, header_value in headers.items():
			if 'default' in header_value:
				reshapend_headers[header_key] = header_value['default']
		return reshapend_headers

	def create_expectation(self):
		if self.currentPath is None or 'operation' not in self.currentOperation or 'statusCode' not in self.currentStatusCode:
			return False

		request_content_types = []
		response_content_types = []

		e = Expectation()
		e.set_path(self.currentPath)
		e.set_method(self.currentOperation['operation'])
		e.set_status_code(self.currentStatusCode['statusCode'])

		#if 'schema' in self.currentStatusCode:
		#	e.set_request_schema(self.currentStatusCode['schema'])			

		if 'headers' in self.currentStatusCode:
			e.set_response_headers(self.__headers_reshape(self.currentStatusCode['headers']))
		
		# try take consumes from operations, if not exists: try take consumes from swagger
		if 'consumes' in self.currentOperation:
			request_content_types = self.currentOperation['consumes']
		else:
			if 'consumes' in self.swagger:
				request_content_types = self.swagger['consumes']
		e.set_request_content_types(request_content_types)

		# try take produces from operations, if not exists: try take produces from swagger
		if 'produces' in self.currentOperation:
			response_content_types = self.currentOperation['produces']
		else:
			if 'produces' in self.swagger:
				response_content_types = self.swagger['produces']
		e.set_response_content_types(response_content_types)

		schema = OpenAPISchema()

		if 'schema' in self.currentStatusCode:
			contract_schema = json.dumps(self.currentStatusCode['schema'])
			e.set_response_body(schema.get_example_json(contract_schema))

		if 'examples' in self.currentStatusCode and len(response_content_types) and response_content_types[0] in self.currentStatusCode['examples']:
			example_json = json.dumps(self.currentStatusCode['examples'][response_content_types[0]])
			schema.validate_json(json.dumps(self.currentStatusCode['schema']), example_json)
			e.set_response_body(example_json)

		if len(self.currentMatchingScenarios):
			for matching_scenario in self.currentMatchingScenarios:
				if matching_scenario.get_expected_response()['responseBody']:
					scenario_json = json.dumps(matching_scenario.get_expected_response()['responseBody'])
					schema.validate_json(json.dumps(self.currentStatusCode['schema']), scenario_json)
					e.set_response_body(scenario_json)

		self.expectations.append(e)
		return True
