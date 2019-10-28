import requests
import logging
import time
import urllib.parse
import json

class Client:

	server_url = None
	xsrf_token = None
	logger = logging.getLogger("airbornerf.Client")

	def __init__(self, server_url):
		self.server_url = server_url
		self.session = requests.Session()
		self.logger.setLevel(logging.DEBUG)

	def _response_check(self, response):

		if response.status_code != requests.codes.ok:
			self.logger.error("Request failed: HTTP " + str(response.status_code))
			self.logger.error(response.text)
			raise RuntimeError("API request failed: HTTP " + str(response.status_code))

	def _response_check_json(self, response):

		self._response_check(response)
		jesponse = response.json()
		if jesponse['success'] != True:
			self.logger.error("Request failed: success is False")
			self.logger.error(jesponse)
			raise RuntimeError("API request failed: {} ({})".format(jesponse['errorMessage'], jesponse['errorCode']))
		return jesponse

	def wait_for_ganot_task(self, ganot_task_id, timeout=60):

		while True:
			gt = self.ganottask_get(ganot_task_id)
			if gt['state'] == 'succeeded':
				return gt
			elif gt['state'] == 'failed':
				self.logger.error("Ganot task {} failed!".format(ganot_task_id))
				self.logger.error(gt)
				raise RuntimeError("Ganot task {} failed!".format(ganot_task_id))
			time.sleep(3)
			timeout -= 3
			if timeout <= 0:
				raise RuntimeError("Timeout exceeded!")

	def renew_xsrf_token(self):

		payload = ""
		headers = {
			'cache-control': "no-cache",
		}

		response = self.session.request("GET", self.server_url + "/session/csrf", data=payload, headers=headers).json()
		self.xsrf_token = response['token']

	def login(self, username, password):

		self.renew_xsrf_token()
		headers = {
			'Content-Type': "application/x-www-form-urlencoded",
			'X-XSRF-TOKEN': self.xsrf_token,
			'cache-control': "no-cache"
		}
		payload = urllib.parse.urlencode({
			'username': username,
			'password': password,
			'platform': 'webapp',
			'platformVersion': '1.0',
			'apiLevel': '1'
		})
		response = self.session.request("POST", self.server_url + "/login", data=payload, headers=headers)
		self._response_check(response)
		self.renew_xsrf_token()

	def logout(self):
		headers = {
			'Content-Type': "application/x-www-form-urlencoded",
			'X-XSRF-TOKEN': self.xsrf_token,
			'cache-control': "no-cache"
		}
		self.session.request("POST", self.server_url + "/logout", headers=headers)

	def get_session_user(self):

		payload = ""
		headers = {
			'cache-control': "no-cache",
		}
		response = self.session.request("GET", self.server_url + "/session/user", data=payload, headers=headers)
		self._response_check(response)
		return response.json()

	def measurement_upload(self, format, name, filename):

		files = {'files': open(filename, 'rb') }
		headers = {
			'X-XSRF-TOKEN': self.xsrf_token,
			'cache-control': "no-cache"
		}
		response = self.session.request("POST", self.server_url + "/measurement/upload/{}/{}".format(format, urllib.parse.quote(name)), files=files, headers=headers)
		jesponse = self._response_check_json(response)
		return jesponse['taskId']

	def measurement_activate(self, measurement_id):

		headers = {
			'X-XSRF-TOKEN': self.xsrf_token,
			'cache-control': "no-cache",
			'Content-Type': "application/json"
		}
		response = self.session.request("POST", self.server_url + "/measurement/activate/" + str(measurement_id), headers=headers)
		jesponse = self._response_check_json(response)
		return jesponse['taskId']

	def measurement_statistics_for_measurement(self, measurement_id):

		headers = {
			'X-XSRF-TOKEN': self.xsrf_token,
			'cache-control': "no-cache",
			'Content-Type': "application/json"
		}
		response = self.session.request("POST", self.server_url + "/measurement/statisticsForMeasurement/" + str(measurement_id), headers=headers)
		jesponse = self._response_check_json(response)
		return jesponse['taskId']

	def measurement_update(self, measurement_id, attributes):

		headers = {
			'X-XSRF-TOKEN': self.xsrf_token,
			'cache-control': "no-cache",
			'Content-Type': "application/json"
		}
		# attributes can have the properties: name (String) and preview (Bool).
		# Both are optional.
		payload = json.dumps(attributes)
		response = self.session.request("PATCH", self.server_url + "/measurement/" + str(measurement_id), data=payload, headers=headers)
		self._response_check(response)
		return response.json()

	def radiospace_get(self):

		payload = ""
		headers = {
			'cache-control': "no-cache",
		}
		response = self.session.request("GET", self.server_url + "/radiospace/get", data=payload, headers=headers)
		self._response_check(response)
		return response.json()

	def radiospace_statistics_for_file(self, format, radiospace_id, filename):

		files = {'files': open(filename, 'rb') }
		headers = {
			'X-XSRF-TOKEN': self.xsrf_token,
			'cache-control': "no-cache"
		}
		response = self.session.request("POST", self.server_url + "/radiospace/statisticsForFile/{}/{}".format(format, radiospace_id), files=files, headers=headers)
		jesponse = self._response_check_json(response)
		return jesponse['taskId']

	def customflight_persist(self, ganot_task_id, name):

		headers = {
			'X-XSRF-TOKEN': self.xsrf_token,
			'cache-control': "no-cache",
			'Content-Type': "application/json"
		}
		response = self.session.request("POST", self.server_url + "/custom-flight/ganotTaskId/{}/name/{}/preview/false".format(ganot_task_id, urllib.parse.quote(name)), headers=headers)
		self._response_check(response)
		return response.json()

	def ganottask_get(self, ganot_task_id):

		payload = ""
		headers = {
			'cache-control': "no-cache",
		}
		response = self.session.request("GET", self.server_url + "/ganottask/get/" + str(ganot_task_id), data=payload, headers=headers)
		self._response_check(response)
		return response.json()
