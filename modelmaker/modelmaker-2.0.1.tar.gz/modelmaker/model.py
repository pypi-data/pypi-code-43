import time,sys
import os
from datetime import datetime, timedelta
from .client.api import *
from .predictor import *
from .schema import Schema_json
#============================
import json
import logging
from six import with_metaclass
from abc import ABCMeta, abstractmethod
from json import JSONEncoder
from jsonschema import validate
import pdb

logging.basicConfig()
LOGGER = logging.getLogger('modelmaker-sdk/Model')
LOGGER_LEVEL = os.getenv("MODELMAKER_LEVEL", logging.INFO) #cloud
LOGGER.setLevel(int(LOGGER_LEVEL))

ISOTIMEFORMAT = '%m%d-%H%M%S'

MODEL_WAIT_SECOND = 5
MAXIMUM_RETRY_TIMES = 200000


class ModelBase(with_metaclass(ABCMeta, object)):

	def __init__(self,**kwargs):
		#self.model_instance = ModelApiAccountImpl(self.session)
		self.service_id = None
		self.model_id	= None
		self.model_version_id = None
		self.predictor_instance = None

	def create_model(self):
		""" creating model interface
		Args:
			kwargs: Create model body params
		Returns:
			dict: model_id that creating successfully
		"""
		if self.modelmaker_session == None:
			raise ValueError("When create model,the parameter modelmaker_session=XXX is need.")
		data = _Manage_model.create_modelmaker_model(self,self.model_name)
		self.model_id = data['id']
		self.model_version_id = data['versionId']

		return data

	def deploy_predictor(self, **kwargs):
		""" Deploying model predictor interface
			Args:
				kwargs: Deploying predictor body params
			Returns:
				dict: service_id that creating successfully
		"""
		if 'modelmaker_session' not in kwargs.keys():
			kwargs['modelmaker_session']=self.modelmaker_session
		if isinstance(kwargs['predictor_models'],list) and isinstance(kwargs['predictor_models'][0],dict):
			if "modelVersionId" not in kwargs['predictor_models'][0] and self.model_version_id != None:
				kwargs['predictor_models'][0]['modelVersionId'] = self.model_version_id
			else:
				raise ValueError("predictor_models parameter must have modelVersionId or please create model first")
		self.predictor_instance = Predictor(**kwargs)
		self.service_id = self.predictor_instance.deploy_predictor()
		return self.predictor_instance

	def info(self):
		"""
		return model information list of the input model_id or the last created model
		"""
		if self.model_version_id is None:
			raise ValueError("please create model first")
		else:
			model_version_id = self.model_version_id
		result  = _Manage_model.get_model_version_info_instance(self.modelmaker_session,model_version_id)
		result  = json.loads(result.data.decode('utf-8'))
		LOGGER.info(result)
		return result

	def delete_model(self):
		if self.model_version_id is None:
			raise ValueError("please create model first")
		else:
			model_version_id = self.model_version_id
		result  = _Manage_model.delete_model_version_instance(self.modelmaker_session,model_version_id = model_version_id)
		result = json.loads(result.data.decode('utf-8'))
		LOGGER.info(result)
		return result

	def get_model_version_id(self):

		LOGGER.info(self.model_version_id)
		return self.model_version_id

	def get_model_id(self):

		LOGGER.info(self.model_id)
		return self.model_id

	def get_service_id(self):

		LOGGER.info(self.service_id)
		return self.service_id


	@classmethod
	def model_list(cls, session=None, model_id=None):
		"""
		return model information list of the input model_id or the last created model
		"""
		result  = _Manage_model.get_model_info(modelmaker_session=session,model_id=model_id)
		result  = json.loads(result.data.decode('utf-8'))
		LOGGER.info(result)
		return result

	@classmethod
	def model_version_info(cls, session=None, model_version_id=None):
		"""
		return model information list of the input model_id or the last created model
		"""
		result  = _Manage_model.get_model_version_info_global(modelmaker_session=session,model_version_id=model_version_id)
		result  = json.loads(result.data.decode('utf-8'))
		LOGGER.info(result)
		return result

	@classmethod
	def preset_model(cls,session=None):

		result = _Manage_model.get_preset_model(session)
		result  = json.loads(result.data.decode('utf-8'))
		LOGGER.info(result)
		return result

	@classmethod
	def predict_machine(cls,session=None):

		result = _Manage_model.get_predict_instance_types(session)
		result  = json.loads(result.data.decode('utf-8'))
		LOGGER.info(result)
		return result

	@classmethod
	def predict_framework(cls,session=None):

		result = _Manage_model.get_predict_framework_list(session)
		result = json.loads(result.data.decode('utf-8'))
		LOGGER.info(result)
		return result

	@classmethod
	def destory_model(cls, session=None, model_id = None):

		result = _Manage_model.delete_model(session,model_id)
		result = json.loads(result.data.decode('utf-8'))
		LOGGER.info(result)
		return result

	@classmethod
	def destory_model_version(cls, session=None, model_version_id = None):
		
		result  = _Manage_model.delete_model_version(session,model_version_id)
		result = json.loads(result.data.decode('utf-8'))
		LOGGER.info(result)
		return result

class _Manage_model(object):
	""" A ModelMaker Model that can be created model, deployed model service and delete model endpoint. """

	@classmethod
	def s3_user_code_upload(cls,session,path):
		if path is None:
			return path
		elif isinstance(path,str):
			if path.startswith("s3://") == True:
				return path
			else:
				if path[-1] == "/":
					path = path[:-1]
				if session.bucket == None:
					raise Exception("Session(...,bucket=xxx) must be set!")
				if not os.path.exists(path):
					raise Exception("Path " + path + " does not exist!")
				else:
					if hasattr(cls,'s3_path'):
						pass
					else:
						beijing_date = (datetime.now()+ timedelta(hours=8)).strftime(ISOTIMEFORMAT)
						session.create_directory(session.bucket,beijing_date)
						cls.s3_path = os.path.join(session.bucket, beijing_date)
					session.upload_data(cls.s3_path + '/',path)
					if os.path.isdir(path):
						result = "s3://"+ os.path.join(cls.s3_path, path.split('/')[-1]) + "/"
					else:
						result = "s3://"+ cls.s3_path + "/"
					LOGGER.info("Success upload %s to %s!"%(path, result))
					return result
		else:
			raise TypeError("code_dir must be string !!")

	@classmethod
	def check_model_params(cls, model_params):
		""" Checking the model parameters validity from console
		"""
		_config = {}
		Framework_type = ["BASIC_FRAMEWORK","PRESET_MODEL","CUSTOM"]
		if model_params.model_framework_type == None or model_params.model_framework_type not in Framework_type:
				raise ValueError('framework_type is must setted in "BASIC_FRAMEWORK","PRESET_MODEL","CUSTOM" ')
		if model_params.model_framework_type == "BASIC_FRAMEWORK":
			_config['name'] = model_params.model_name
			_config['type'] = model_params.model_framework_type
			_config['version'] = model_params.model_version
			_config['frameworkId'] = model_params.model_framework
			_config['modelPath'] = model_params.model_path
			_config['gitInfo'] = model_params.model_git_info
			_config['startup'] = model_params.model_boot_file
			_config['callSpecs'] = model_params.model_call_specs
			_config['codeUrl'] = model_params.model_code_dir
			validate(instance=_config,schema=Schema_json.Basic_Model)
			result = _Manage_model.get_predict_framework_list(model_params.modelmaker_session)
			result = json.loads(result.data.decode('utf-8'))
			frameworkId_list = [ item['id'] for item in result['frameWorks']]
			if _config['frameworkId'] not in frameworkId_list:
				raise ValueError("model_framwork is not exist, please check it!")
			_config['codeUrl'] = _Manage_model.s3_user_code_upload(model_params.modelmaker_session, model_params.model_code_dir)
		elif model_params.model_framework_type == "PRESET_MODEL":
			_config['name'] = model_params.model_name
			_config['type'] = model_params.model_framework_type
			_config['version'] = model_params.model_version
			_config['presetModelId'] = model_params.model_framework
			_config['modelPath'] = model_params.model_path
			result = _Manage_model.get_preset_model(model_params.modelmaker_session)
			result = json.loads(result.data.decode('utf-8'))
			preset_model_list = [ item['id'] for item in result['presetModels']]
			if _config['presetModelId'] not in preset_model_list:
				raise ValueError("model_framwork is not exist, please check it!")

			self._generate_model_params(model_params=kwargs)
		elif model_params.model_framework_type == "CUSTOM":
			_config['name'] = model_params.model_name
			_config['type'] = model_params.model_framework_type
			_config['version'] = model_params.model_version
			_config['modelPath'] = model_params.model_path
			_config['mirrorUrl'] = model_params.model_mirrorUrl
		LOGGER.debug("=============Model:%s==================="%(_config['type']))
		LOGGER.debug(_config)

		return _config
	
#	def is_reach_maximum_times(self, max_attempt_times):
#		if max_attempt_times > MAXIMUM_RETRY_TIMES:
#			return True
#		else:
#			return False
#
#	def create_modelmaker_model_version(self,model_id):
#		""" Creating model
#			Args:
#				session: Building interactions with Wangsu Cloud service.
#			Returns:
#				The model id that created successfully, will be used in deploying service.
#		"""
#		self.model_id = model_id
#		model_create_resp = self.model_api.create_the_version_model(project_id=self.session.project_id,
#																body=self.create_model_body, model_id=self.model_id)
#		data = json.loads(model_create_resp.data.decode('utf-8'))
#		LOGGER.info("=============%s====================="%('Model Response'))
#		LOGGER.info(data)
#		self.model_version_id = data['versionId']
#
	@classmethod
	def create_modelmaker_model(cls, Model, model_name):
		""" Creating model
			Args:
				session: Building interactions with Wangsu Cloud service.
			Returns:
				The model id that created successfully, will be used in deploying service.
		"""
		_config = _Manage_model.check_model_params(Model)
		body = _config
		print(body)
		#pdb.set_trace()
		project_id = Model.modelmaker_session.project_id
		if Model.modelmaker_session.auth == 'token':
			model_api = ModelApi(Model.modelmaker_session.client)
			model_create_resp = model_api.create_the_model(project_id=project_id, body=body)
			data = json.loads(model_create_resp.data.decode('utf-8'))
			if data.get('errorCode'):
				if data['errorCode'] == 101009:
					result = _Manage_model.get_model_info(Model.modelmaker_session,model_id=None)
					result = json.loads(result.data.decode('utf-8'))
					for item in result['models']:
						if item['name'] == model_name:
							model_id = item['id']
							model_create_resp = model_api.create_the_version_model(project_id=project_id,
														body= body, model_id= model_id)
							data = json.loads(model_create_resp.data.decode('utf-8'))
							if data.get('errorCode'):
								raise Exception("create model  error!")
							LOGGER.info("=============%s==================="%('Model Response'))
							LOGGER.info(data)
							return data
				else:
					raise Exception("create model  error!")
			LOGGER.info("=============%s==================="%('Model Response'))
			LOGGER.info(data)
			return data
		else:
			data = 0
			return data
			#return model_create_resp

	@classmethod
	def get_predict_instance_types(cls,modelmaker_session):
		""" get_preset_model
		"""
		spec_api = SpecApi(modelmaker_session.client)

		body={}
		return spec_api.list_spec(project_id=modelmaker_session.project_id,body=body,env="PREDICT")

	@classmethod
	def get_predict_framework_list(cls,modelmaker_session):
		""" get_preset_model
		"""

		framework_api = FrameworkApi(modelmaker_session.client)
		body={}
		return framework_api.get_framework_id(project_id=modelmaker_session.project_id, body=body, env="PREDICT")

	@classmethod
	def get_preset_model(cls,modelmaker_session):
		""" get_preset_model
		"""
		model_api = ModelApi(modelmaker_session.client)
		body={}
		return model_api.get_preset_model(project_id=modelmaker_session.project_id, body=body)

	@classmethod
	def delete_model(cls, modelmaker_session, model_id = None):
		""" Only delete model endpoint
		"""
		if model_id is None:
			raise ValueError('model_id is need!!!')

		model_api = ModelApi(modelmaker_session.client)
		body={}
		return model_api.delete_model(project_id=modelmaker_session.project_id, body=body, model_id=model_id)

	@classmethod
	def delete_model_version(cls, modelmaker_session, model_version_id = None):
		""" Only delete model endpoint
		"""
		if model_version_id is None:
			raise ValueError('model_version_id is need!!!')

		model_api = ModelApi(modelmaker_session.client)
		body = {}

		return model_api.delete_model_version(project_id=modelmaker_session.project_id, body=body, model_version_id=model_version_id)

	@classmethod
	def delete_model_version_instance(cls, modelmaker_session, model_version_id = None):
		""" Only delete model endpoint
		"""
		if model_version_id is None:
			raise ValueError('model_version_id is need!!!')

		model_api = ModelApi(modelmaker_session.client)
		body = {}

		return model_api.delete_model_version(project_id=modelmaker_session.project_id, body=body, model_version_id=model_version_id)

	@classmethod
	def get_model_info(cls, modelmaker_session, model_id=None):
		"""
		:return model information.
		"""
		#if model_id is None:
		#	raise ValueError('model_id is need!!!')

		model_api = ModelApi(modelmaker_session.client)
		body={}
		return model_api.get_model_info(project_id=modelmaker_session.project_id, model_id=model_id, body=body)

	@classmethod
	def get_model_version_info_global(cls, modelmaker_session,model_version_id=None):
		"""
		:return model information.
		"""
		if model_version_id is None:
			raise ValueError('model_version_id is need!!!')

		model_api = ModelApi(modelmaker_session.client)
		body={}
		return model_api.get_model_version_info(project_id=modelmaker_session.project_id, model_version_id=model_version_id, body=body)


	@classmethod
	def get_model_version_info_instance(cls, modelmaker_session,model_version_id=None):
		"""
		:return model information.
		"""
		model_api = ModelApi(modelmaker_session.client)
		body={}
		return model_api.get_model_version_info(project_id=modelmaker_session.project_id, model_version_id=model_version_id, body=body)

class Model(ModelBase):
	"""
	A ModelMaker Model that can be created model, deployed model service,
	got model info and list, and deleted model and service endpoint.
	"""
	def __init__(self, modelmaker_session=None, model_name=None, model_version=None, model_path=None, model_framework=None, model_framework_type=None,
				 model_code_dir=None, model_boot_file=None, model_call_specs=None, model_description=None, model_mirrorUrl=None,
				 model_git_info=None,**kwargs):
		"""
		Initialize a model, determine the model authorize type.
		param session: Building interactions with Wangsu Cloud service.
		"""
		self.model_name = model_name
		self.model_version = model_version
		self.model_path = model_path
		self.model_framework = model_framework
		self.model_framework_type = model_framework_type
		self.model_code_dir = model_code_dir
		self.model_boot_file = model_boot_file
		self.model_call_specs = model_call_specs
		self.model_description = model_description
		self.model_mirrorUrl = model_mirrorUrl
		self.model_git_info = model_git_info
		self.modelmaker_session = modelmaker_session
		super(Model, self).__init__(**kwargs)

