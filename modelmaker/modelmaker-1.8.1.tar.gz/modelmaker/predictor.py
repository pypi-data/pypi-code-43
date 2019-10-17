import requests
#from .infers_images_api import *
from .client.api import *
from abc import ABCMeta, abstractmethod
from six import with_metaclass
from json import JSONEncoder
import json
import logging
import os

logging.basicConfig()
LOGGER = logging.getLogger('modelmaker-sdk/Predictor')
LOGGER_LEVEL = os.getenv("MODELMAKER_LEVEL", logging.INFO) #cloud
LOGGER.setLevel(int(LOGGER_LEVEL))

class Predictor(object):
	"""
	A ModelMaker Predictor that can be predicted, got service information and list,
	changed service state and configuration.
	"""

	def __init__(self, session, service_id=None):
		"""
		Initialize a Predictor, determine the predictor authorize type.
		param session: Building interactions with Wangsu Cloud service.
		param service_id: The deployed model service id
		"""
		self.session = session
		if service_id is not None and isinstance(service_id,int) == False:
			raise TypeError("service_id type is int!")
		self.service_id = service_id
		self.predictor_instance = PredictorApiAccountImpl(self.session, service_id)

	def info(self, service_id = None):
		""" Get the deployed model service information
		Args:
			service_id: The deployed model service id
		return: The deployed service information,including model service access address.
		"""
		result = self.predictor_instance.get_service_info(service_id)
		LOGGER.info(json.loads(result.data.decode('utf-8')))
		return json.loads(result.data.decode('utf-8'))

	def info_list(self):
		"""
		return User service list
		"""
		result = self.predictor_instance.get_service_list()
		LOGGER.info(json.loads(result.data.decode('utf-8')))
		return json.loads(result.data.decode('utf-8'))

	def start(self, service_id=None):
		""" change a service state.
		Args:
			service_id: service_id
		return: Service start tasks result.
		"""
		result = self.predictor_instance.change_service_state('start', service_id=service_id)
		LOGGER.info(json.loads(result.data.decode('utf-8')))
		return json.loads(result.data.decode('utf-8'))

	def stop(self, service_id=None):
		""" change a service state.
		Args:
			service_id: service_id
		return: Service stop tasks result.
		"""
		result = self.predictor_instance.change_service_state('stop', service_id=service_id)
		LOGGER.info(json.loads(result.data.decode('utf-8')))
		return json.loads(result.data.decode('utf-8'))

	def update(self, service_id=None):
		""" change a service state.
		Args:
			service_id: service_id
		return: Service update tasks result.
		"""
		result = self.predictor_instance.update_request(service_id=service_id)
		LOGGER.info(json.loads(result.data.decode('utf-8')))
		return json.loads(result.data.decode('utf-8'))

	def delete(self, service_id=None):
		""" change a service state.
		Args:
			service_id: service_id
		return: Service delete tasks result.
		"""
		result = self.predictor_instance.delete_request(service_id=service_id)
		LOGGER.info(json.loads(result.data.decode('utf-8')))
		return json.loads(result.data.decode('utf-8'))

#	def update_service_config(self, service_id=None, **config_body):
#		""" update a service configuration
#		Args:
#			service_id: service id
#			config_body: service configuration parameters
#		:return: Service update configuration tasks result.
#		"""
#		return self.predictor_instance.update_service_config(service_id=service_id, **config_body)
#
#	 def get_service_monitor(self, service_id=None):
#
#		 """ service monitor information
#			 Args: service_id:
#			 return: monitor information
#		 """
#		 return self.predictor_instance.get_service_monitor(service_id=service_id)
#
#	 def get_service_logs(self, service_id=None):
#		 """ service logs
#			 Args: service_id:
#			 return: monitor information
#		 """
#		 return self.predictor_instance.get_service_logs(service_id=service_id)


class PredictorApiBase(with_metaclass(ABCMeta, object)):
	""" Make prediction requests to a ModelMaker model service endpoint
		"""

	def __init__(self):
		""" Initialize Predictor
			service_id: The deployed model service id
		"""

#	 @abstractmethod
#	 def get_service_info(self):
#		 """ Get the deployed model service information
#		 return: The deployed service information,including model service access address.
#		 """
#		 pass
#
#	 @abstractmethod
#	 def predict(self, data, data_type):
#		 """
#		 data(object):	Input data for which you want the model to provide inference.
#		 data_type: {files, images}
#		 """
#		 pass
#
#	 @abstractmethod
#	 def get_service_list(self):
#		 """
#		 return User service list
#		 """
#		 pass
#
#	 @abstractmethod
#	 def change_service_state(self, node_id, action_body, service_id=None):
#		 """ change a service state.
#		 Args:
#			 node_id: node id
#			 action_body: Operate type, {stop, run}
#		 return: Service stop or start tasks result.
#		 """
#		 pass
#
#	 @abstractmethod
#	 def update_service_config(self, service_id=None, **config_body):
#		 """ update a service configuration
#		 Args:
#			 service_id: service id
#			 config_body: service configuration parameters
#		 :return: Service update configuration tasks result.
#		 """
#		 pass
#
#	 @abstractmethod
#	 def get_service_monitor(self, service_id=None):
#		 """ service monitor information
#			 Args: service_id:
#			 return: monitor information
#		 """
#		 pass
#
#	 @abstractmethod
#	 def get_service_logs(self, service_id=None):
#		 """ service logs
#			 Args: service_id:
#			 return: monitor information
#		 """
#		 pass



class PredictorApiAccountImpl(PredictorApiBase):
	""" Make prediction requests to a ModelMaker model service endpoint
	"""

	def __init__(self, session, service_id):

		""" Initialize Predictor
		Args:
			session: Building interactions with Wangsu Cloud Service, including project id.
			service_id: The deployed model service id

		"""
		self.session = session
		if service_id is not None and isinstance(service_id,int) == False:
			raise TypeError("service_id type is int!")
		self.service_id = service_id
		self.service_api = ServiceApi(session.client)

	def get_service_info(self, service_id=None):
		""" Get the deployed model service information
		"""
		if service_id is None and self.service_id:
			service_id = self.service_id
		elif service_id and self.service_id and service_id !=self.service_id:
			print("Current service_id is %s, but it will replace by service_id %s"%(str(self.service_id),str(service_id)))
		elif service_id is None and self.service_id is None:
			raise ValueError("service_id is need")

		body={}
		return self.service_api.get_service_info(self.session.project_id, body=body, service_id=service_id)

	def get_service_list(self):
		"""
		return User service list
		"""
		body={}
		return self.service_api.get_service_info(self.session.project_id, body=body, service_id=None)

	def info(self, service_id = None):
		""" Get the deployed model service information
		Args:
			service_id: The deployed model service id
		return: The deployed service information,including model service access address.
		"""
		result = self.get_service_info(service_id)
		LOGGER.info(json.loads(result.data.decode('utf-8')))
		return json.loads(result.data.decode('utf-8'))

	def info_list(self):
		"""
		return User service list
		"""
		result = self.get_service_list()
		LOGGER.info(json.loads(result.data.decode('utf-8')))
		return json.loads(result.data.decode('utf-8'))

	def start(self, service_id=None):
		result = self.change_service_state('start', service_id=None)	
		LOGGER.info(json.loads(result.data.decode('utf-8')))
		return json.loads(result.data.decode('utf-8'))

	def stop(self, service_id=None):
		result = self.change_service_state('stop', service_id=None)	
		LOGGER.info(json.loads(result.data.decode('utf-8')))
		return json.loads(result.data.decode('utf-8'))

	def change_service_state(self, action_body, service_id=None):
		""" change a service state.
		Args:
			service_id: service_id
			action_body: Operate type, {start, stop}
		return: Service stop or start tasks result.
		"""
		if service_id is None and self.service_id:
			service_id = self.service_id
		elif service_id and self.service_id and service_id != self.service_id:
			print("Current service_id is %s, but it will replace by service_id %s"%(str(self.service_id),str(service_id)))
		elif service_id is None and self.service_id is None:
			raise ValueError("service_id is need")
		body = {}
		return self.service_api.operate_a_service(self.session.project_id, body, service_id, action_body)

	def update_request(self, service_id=None):
		""" change a service state.
		Args:
			service_id: service_id
		return: Service update tasks result.
		"""
		if service_id is None:
			service_id = self.service_id
		body = {}
		return	self.service_api.update_micro_service(project_id=self.session.project_id, body=body, service_id=service_id)

	def update(self, service_id=None):
		result = self.update_request(service_id=service_id)
		LOGGER.info(json.loads(result.data.decode('utf-8')))
		return json.loads(result.data.decode('utf-8'))

	def delete_request(self, service_id=None):
		""" change a service state.
		Args:
			service_id: service_id
		return: Service delete tasks result.
		"""
		if service_id is None:
			service_id = self.service_id
		body = {}
		return	self.service_api.delete_micro_service(project_id=self.session.project_id, body=body, service_id=service_id)

	def delete(self, service_id=None):
		""" change a service state.
		Args:
			service_id: service_id
		return: Service delete tasks result.
		"""
		result = self.delete_request(service_id=service_id)
		LOGGER.info(json.loads(result.data.decode('utf-8')))
		return json.loads(result.data.decode('utf-8'))


#	def update_service_config(self, service_id=None, **config_body):
#		""" update a service configuration
#		Args:
#			service_id: service id
#			config_body: service configuration parameters
#		:return: Service update configuration tasks result.
#		"""
#		service_config_body = config_body
#
#		if 'config' in config_body:
#			service_config_body['config'] = super(PredictorApiAccountImpl,self).convert_config_format(config_body['config'])
#
#		if service_id is None:
#			service_id = self.service_id
#
#		return self.service_api.update_service_config(self.session.project_id, service_id, service_config_body)
#
#	 def get_service_monitor(self, service_id=None):
#
#		 """ service monitor information
#			 Args: service_id:
#			 return: monitor information
#		 """
#		 if service_id is None:
#			 service_id = self.service_id
#
#		 return self.service_api.get_service_monitor(self.session.project_id, service_id)
#
#	 def get_service_logs(self, service_id=None):
#		 """ service logs
#			 Args: service_id:
#			 return: monitor information
#		 """
#		 if service_id is None:
#			 service_id = self.service_id
#
#		 return self.service_api.get_service_logs(self.session.project_id, service_id)



