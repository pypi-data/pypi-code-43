import requests

class MockserverRequester(object):

	def __init__(self):
		self.mockserver_uri = ''

	def set_mockserver_uri(self, uri):
		self.mockserver_uri = 'http://' + uri

	def request_expectations(self, expectations):
		expectation_uri = self.mockserver_uri + '/mockserver/expectation'
		for expectation in expectations:
			self.__clear_expectation(expectation.get())
			try:
				r = requests.put(expectation_uri, data=expectation.get_json())
			except:
				print(expectation_uri + ' is not a valid uri')

	def request_reset(self):
		reset_uri = self.mockserver_uri + '/mockserver/reset'
		try:
			r = requests.put(reset_uri)
			return r.status_code == requests.codes.ok
		except:
			print(reset_uri + ' is not a valid uri')
		return False

	def __clear_expectation(self, expectation):
		path = expectation['httpRequest']['path']
		method = expectation['httpRequest']['method']

		try:
			r = requests.put(self.mockserver_uri + '/mockserver/retrieve?type=active_expectations')
			active_expectations = r.json()
		except:
			print('Error while fetching active expectations')
			return

		for active_expectation in active_expectations:
			if path == active_expectation['httpRequest']['path'] and method == active_expectation['httpRequest']['method']:
				clear_uri = self.mockserver_uri + '/mockserver/clear'
				try:
					r = requests.put(clear_uri, data='{"path": "%s", "method": "%s"}' % (path, method))
					break
				except:
					print('Error while clearing active expectation')
					return
