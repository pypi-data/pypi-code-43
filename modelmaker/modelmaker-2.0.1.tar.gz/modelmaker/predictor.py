import requests
#from .infers_images_api import *
from .client.api import *
from abc import ABCMeta, abstractmethod
from six import with_metaclass
from json import JSONEncoder
import json
import logging
import os
from .schema import Schema_json
from jsonschema import validate


logging.basicConfig()
LOGGER = logging.getLogger('modelmaker-sdk/Predictor')
LOGGER_LEVEL = os.getenv("MODELMAKER_LEVEL", logging.INFO) #cloud
LOGGER.setLevel(int(LOGGER_LEVEL))

class PredictorBase(with_metaclass(ABCMeta, object)):
	"""
	A ModelMaker Predictor that can be predicted, got service information and list,
	changed service state and configuration.
	"""

	def __init__(self):
		"""
		Initialize a Predictor, determine the predictor authorize type.
		param session: Building interactions with Wangsu Cloud service.
		param service_id: The deployed model service id
		"""
		self.service_id = None

	def deploy_predictor(self):
		"""
		Deploying model predictor interface
		Args:
		kwargs: Deploying predictor body params
		Returns:
		dict: service_id that creating successfully
       """
		if self.modelmaker_session == None:
			raise ValueError("When deploy_predictor,the parameter modelmaker_session=XXX is need.")
		service_id = _Service_deploy.deploy_modelmaker_predictor(self)
		self.service_id = service_id
		return service_id

	def update(self,**kwargs):
		""" change a service state.
		Args:
			service_id: service_id
		return: Service update tasks result.
		"""
		if self.service_id is None:
			raise ValueError("please deploy_predictor first")
		for key in kwargs.keys():
			if key in self.__dict__:
				setattr(self,key,kwargs[key])
		service_id = _Service_deploy.update_request(self,service_id=self.service_id)
		self.service_id = service_id
		return service_id

	def info(self, service_id = None):
		""" Get the deployed model service information
		Args:
			service_id: The deployed model service id
		return: The deployed service information,including model service access address.
		"""
		if self.service_id is None:
			raise ValueError("please deploy_predictor first")

		result = _Service_deploy.get_service_info(self.modelmaker_session,service_id=self.service_id)
		LOGGER.info(json.loads(result.data.decode('utf-8')))
		return json.loads(result.data.decode('utf-8'))

	def start(self):
		""" change a service state.
		Args:
			service_id: service_id
		return: Service start tasks result.
		"""
		if self.service_id is None:
			raise ValueError("please deploy_predictor first")
		result = _Service_deploy.change_service_state_instance('start',self.modelmaker_session,service_id=self.service_id)
		LOGGER.info(json.loads(result.data.decode('utf-8')))
		return json.loads(result.data.decode('utf-8'))

	def stop(self):
		""" change a service state.
		Args:
			service_id: service_id
		return: Service stop tasks result.
		"""
		if self.service_id is None:
			raise ValueError("please deploy_predictor first")

		result = _Service_deploy.change_service_state_instance('stop',self.modelmaker_session,service_id=self.service_id)
		LOGGER.info(json.loads(result.data.decode('utf-8')))
		return json.loads(result.data.decode('utf-8'))

	def delete(self):
		""" change a service state.
		Args:
			service_id: service_id
		return: Service delete tasks result.
		"""
		if self.service_id is None:
			raise ValueError("please deploy_predictor first")

		result = _Service_deploy.delete_request(self.modelmaker_session,service_id=self.service_id)
		LOGGER.info(json.loads(result.data.decode('utf-8')))

		self.service_id = None
		return json.loads(result.data.decode('utf-8'))

	@classmethod
	def service_machine(cls,session=None):
		result = _Service_deploy.get_predict_instance_types(session)
		result  = json.loads(result.data.decode('utf-8'))
		LOGGER.info(result)
		return result

	@classmethod
	def START(cls,session=None,service_id=None):
		""" change a service state.
		Args:
			service_id: service_id
		return: Service start tasks result.
		"""
		if service_id is None or session is None:
			raise ValueError("START(session=xxx,service_id=xxx),session and service_id are needed.")
		result = _Service_deploy.change_service_state_instance('start',session,service_id)
		LOGGER.info(json.loads(result.data.decode('utf-8')))
		return json.loads(result.data.decode('utf-8'))

	@classmethod
	def STOP(cls,session=None,service_id=None):
		""" change a service state.
		Args:
			service_id: service_id
		return: Service stop tasks result.
		"""
		if service_id is None or session is None:
			raise ValueError("STOP(session=xxx,service_id=xxx),session and service_id are needed.")

		result = _Service_deploy.change_service_state_instance('stop',session,service_id)
		LOGGER.info(json.loads(result.data.decode('utf-8')))
		return json.loads(result.data.decode('utf-8'))

	@classmethod
	def DELETE(cls,session=None,service_id=None):
		""" change a service state.
		Args:
			service_id: service_id
		return: Service delete tasks result.
		"""
		if service_id is None or session is None:
			raise ValueError("DELETE(session=xxx,service_id=xxx),session and service_id are needed.")

		result = _Service_deploy.delete_request(session,service_id)
		LOGGER.info(json.loads(result.data.decode('utf-8')))

		return json.loads(result.data.decode('utf-8'))

	@classmethod
	def service_info(cls, session=None, service_id = None):
		""" Get the deployed model service information
		Args:
			service_id: The deployed model service id
		return: The deployed service information,including model service access address.
		"""
		if service_id is None or session is None:
			raise ValueError("service_info(session=xxx,service_id=xxx),session and service_id are needed.")

		result = _Service_deploy.get_service_info(session,service_id)
		LOGGER.info(json.loads(result.data.decode('utf-8')))
		return json.loads(result.data.decode('utf-8'))

	@classmethod
	def service_list(cls,session=None):
		"""
		return User service list
		"""
		if session is None:
			raise ValueError("service_list(session=xxx),session are needed.")
		result = _Service_deploy.get_service_list(session)
		LOGGER.info(json.loads(result.data.decode('utf-8')))
		return json.loads(result.data.decode('utf-8'))

class _Service_deploy(object):
	""" Make prediction requests to a ModelMaker model service endpoint
	"""

	@classmethod
	def check_predictor_params(cls,predictor_params):
		_config={}
		_config['name'] = predictor_params.predictor_name
		_config['type'] = predictor_params.predictor_type
		_config['serviceModels'] = predictor_params.predictor_models
		if isinstance(_config['serviceModels'],list) and isinstance(_config['serviceModels'][0],dict):
			if "resourcePoolType" not in _config['serviceModels'][0].keys():
				_config['serviceModels'][0]['resourcePoolType']='PUBLIC_POOL'
		#print(_config['serviceModels'][0])
		validate(instance=_config,schema=Schema_json.Predictor)
		result = _Service_deploy.get_predict_instance_types(predictor_params.modelmaker_session)
		result = json.loads(result.data.decode('utf-8'))
		resourceId_list = [ item['id'] for item in result['resources']]
		if _config['serviceModels'][0]['resourceId'] not in resourceId_list:
			raise ValueError("predictor_models['resourceId'] is not exist, please check it!")
		LOGGER.debug("=============Delopy===================")
		LOGGER.debug(_config)
		return _config

	@classmethod
	def deploy_modelmaker_predictor(cls,Predictor):
		_config = _Service_deploy.check_predictor_params(Predictor)
		body = _config
		#print(body)
		LOGGER.debug(body)
		project_id = Predictor.modelmaker_session.project_id
		if Predictor.modelmaker_session.auth == 'token':
			service_api = ServiceApi(Predictor.modelmaker_session.client)
			service_deploy_resp = service_api.create_service(project_id=project_id,body=body)
			data = str(service_deploy_resp.data, encoding="utf-8")
			data = eval(data)
			LOGGER.info("=============%s==================="%('Service Response'))
			LOGGER.info(data)
			if data.get('errorCode'):
			        raise Exception("create service  error!")
			service_id = data['id']
			return service_id

	@classmethod
	def update_request(cls, Predictor, service_id=None):
		""" change a service state.
		Args:
			service_id: service_id
		return: Service update tasks result.
		"""
		_config = _Service_deploy.check_predictor_params(Predictor)
		body = _config
		#print(body)
		LOGGER.debug(body)
		project_id = Predictor.modelmaker_session.project_id
		if Predictor.modelmaker_session.auth == 'token':
			service_api = ServiceApi(Predictor.modelmaker_session.client)
			service_deploy_resp = service_api.update_micro_service(project_id=project_id, body=body, service_id=service_id)
			data = str(service_deploy_resp.data, encoding="utf-8")
			data = eval(data)
			LOGGER.info("=============%s==================="%('Service Response'))
			LOGGER.info(data)
			if data.get('errorCode'):
			        raise Exception("create service  error!")
			service_id = data['id']
			return service_id

	@classmethod
	def get_predict_instance_types(cls,modelmaker_session):
		""" get_preset_machine
		"""
		spec_api = SpecApi(modelmaker_session.client)

		body={}
		return spec_api.list_spec(project_id=modelmaker_session.project_id,body=body,env="PREDICT")

	@classmethod
	def get_service_info(cls, modelmaker_session, service_id):
		""" Get the deployed model service information
		"""

		service_api = ServiceApi(modelmaker_session.client)
		body={}
		return service_api.get_service_info(modelmaker_session.project_id, body=body, service_id=service_id)

	@classmethod
	def get_service_list(cls,modelmaker_session):
		"""
		return User service list
		"""
		service_api = ServiceApi(modelmaker_session.client)
		body={}
		return service_api.get_service_info(modelmaker_session.project_id, body=body, service_id=None)

	@classmethod
	def delete_request(cls, modelmaker_session, service_id=None):
		""" change a service state.
		Args:
			service_id: service_id
		return: Service delete tasks result.
		"""
		service_api = ServiceApi(modelmaker_session.client)
		body = {}
		return	service_api.delete_micro_service(modelmaker_session.project_id, body=body, service_id=service_id)

	@classmethod
	def change_service_state_instance(cls, action_body, modelmaker_session, service_id=None):
		""" change a service state.
		Args:
			service_id: service_id
			action_body: Operate type, {start, stop}
		return: Service stop or start tasks result.
		"""

		service_api = ServiceApi(modelmaker_session.client)
		body = {}
		return service_api.operate_a_service(modelmaker_session.project_id, body, service_id, action_body)

class Predictor(PredictorBase):
	"""
	A ModelMaker Predictor that can be deployed model service,
	got predictor info and list, and deleted service endpoint.
	"""
	def __init__(self, modelmaker_session=None, predictor_name=None, predictor_type=None, predictor_models=None,**kwargs):
		"""
		Initialize a model, determine the model authorize type.
		param session: Building interactions with Wangsu Cloud service.
		"""
		self.predictor_name = predictor_name
		self.predictor_type = predictor_type
		self.predictor_models = predictor_models
		self.modelmaker_session = modelmaker_session
		super(Predictor, self).__init__(**kwargs)

