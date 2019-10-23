import os
import json
import requests
from tqdm import tqdm
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from nanonets.model import Model
from nanonets.utils import *

class ImageClassification(Model):

	def __init__(self, api_key, categories, model_id=None):
		super().__init__(api_key=api_key, model_type='ImageCategorization')
		if not model_id:
			self._create_model(categories)
		else:
			self.api_key = api_key
			self.categories = categories
			self.model_id = model_id

	def train_dict_to_category_dict(self, training_dict):
		"""
		function to split the training_dict into separate dicts for each category

		Parameters
		----------
		training_dict: Dict[str: str]
		    Dict with keys as image file paths and values as the corresponding labels. 

		Returns
		-------
		Dict with keys as categories of the model and values as List[str] of image paths 
		"""

		train_dicts = {}
		for category in self.categories:
			train_dicts[category] = []
		for file in training_dict:
			category = training_dict[file]
			train_dicts[category].append(file)
		return train_dicts

	def upload_image_file(self, img_path, label):
		"""
		function to upload a single file and it's annotation for training 

		Parameters
		----------
		img_path: str
		    path to the image we want to upload

		label: str
			label for the same image

		Returns
		-------
		server response for the request for uploading urls. 
		"""

		url = self.host + self.model_type + '/Model/' + self.model_id + '/UploadFile/'
		params = {'file': open(img_path, 'rb'),
				  'modelId': ('', self.model_id),
				  'category': ('', label)}
		response = requests.post(url,
					files=params, 
					auth=requests.auth.HTTPBasicAuth(self.api_key, ''))
		return response

	def upload_image_files(self, training_dict, batch_size=20):
		"""
		function to upload multiple files and their annotations 

		Parameters
		----------
		training_dict: Dict[str: str]
		    Dict with keys as image file paths and values as the corresponding labels 

		batch_size (optional): int
			number of images to be uploaded per API request

		Returns
		-------
		a list of responses for each batch of images uploaded
		"""

		train_dicts = self.train_dict_to_category_dict(training_dict)
		responses = []
		for category in self.categories:
			print('Uploading for category: ', category)
			batch_nb = 1
			files = train_dicts[category]
			if len(files)%batch_size == 0:
				total_batches = int(len(files)/batch_size)
			else:
				total_batches = int(int(len(files)/batch_size) + 1)
			url = self.host + self.model_type + '/UploadFile/?modelId=%s&category=%s'%(self.model_id, category)		
			while len(train_dicts[category]) > 0:
				multiple_files = []
				batch_images, train_dicts[category] = train_dicts[category][:batch_size], train_dicts[category][batch_size:]
				print('Batch {}/{} of images'.format(batch_nb, total_batches))				
				for image in tqdm(batch_images):
					image_name = image.split('/')[-1]
					multiple_files.append(('file', (image_name, open(image, 'rb'), 'image/jpeg')))
				response = requests.post(url, 
							 auth=requests.auth.HTTPBasicAuth(self.api_key, ''), 
							 files=multiple_files)
				responses.append(response)
				batch_nb+=1
		return responses

	def upload_image_url(self, image_url, label):
		"""
		function to upload image given by their url to a model that has been created

		Parameters
		----------
		image_url: str
		    path to the image we want to upload

		label: str
			label for the same image

		Returns
		-------
		server response for the request for uploading url
		"""

		url = self.host + self.model_type + '/UploadUrls/'
		data = {'urls': [image_url],
			'modelId': self.model_id,
			'category': label}
		headers = { 'accept': 'application/x-www-form-urlencoded'}
		response = requests.post(url,
								 headers=headers,
								 auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
								 data=data)
		return response

	def upload_image_urls(self, training_dict):
		"""
		function to upload images given by their urls to a model that has been created

		Parameters
		----------
		training_dict: Dict[str: str]
		    Dict with keys as image file urls and values as the corresponding labels 

		Returns
		-------
		list of server responses for the request for uploading urls for each category
		"""

		url = self.host + self.model_type + '/UploadUrls/'
		train_dicts = self.train_dict_to_category_dict(training_dict)
		responses = []
		for category in self.categories:
			data = {'urls': train_dicts[category],
				'modelId': self.model_id,
				'category': category}
			headers = { 'accept': 'application/x-www-form-urlencoded'}
			response = requests.post(url,
						 headers=headers,
						 auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
						 data=data)
			responses.append(response)
		return responses

	def train(self, training_dict, data_path_type='files', batch_size=20):
		"""
		function to upload a single file and it's labels and initiate the training. 

		Parameters
		----------
		training_dict: Dict[str: str]
		    Dict with keys as image file urls/paths and values as the corresponding labels

		data_path_type: str
			Can take values 'files' or 'urls'

		Returns
		-------
		server response for the request for intialising training
		"""
		if data_path_type == 'files':		
			self.upload_image_files(training_dict, batch_size=batch_size)
		elif data_path_type == 'urls':
			self.upload_image_urls(training_dict)
		url = self.host + self.model_type + '/Train/'
		params = {'modelId': self.model_id}
		response = requests.request("POST", url,
					    params=params,
					    auth=requests.auth.HTTPBasicAuth(self.api_key, ''))
		return response

	def predict_for_file(self, file_path):
		"""
		function to get prediction for a single image file

		Parameters
		----------
		file_path: 
			path of the image you want to get predictions for

		Returns
		-------
		JSON repsonse of the prediction 
		"""

		url = self.host + self.model_type + '/LabelFile/?modelId=%s'%(self.model_id)
		params = {'file': open(file_path, 'rb')}
		response = requests.post(url,
					 auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
					 files=params) 
		result = read_prediction_response([response], self.model_type)
		return result

	def predict_for_url(self, image_url):
		"""
		function to get prediction for a single image file

		Parameters
		----------
		image_url: 
			url of the image you want to get predictions for

		Returns
		-------
		JSON repsonse of the prediction 
		"""

		url = self.host + self.model_type + '/LabelUrls/'
		headers = {'accept': 'application/x-www-form-urlencoded'}
		params = {'modelId': self.model_id, 'urls': [image_url]}
		response = requests.post(url,
					headers=headers,
					auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
					data=params) 
		result = read_prediction_response([response], self.model_type)
		return result

	def predict_for_files(self, files, batch_size=20):
		"""
		function to get predictions for multiple image files 

		Parameters
		----------
		files: List[str]
		    List of image file paths

		batch_size (optional): int
			number of images to be uploaded per API request

		Returns
		-------
		Dict with file names as keys and the predictions as values
		"""

		url = self.host + self.model_type + '/LabelFile/?modelId=%s'%(self.model_id)
		retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
		adapter = HTTPAdapter(max_retries=retries)

		session = requests.Session()
		session.mount(url, adapter)

		responses = []
		batch_nb = 1
		if len(files)%batch_size == 0:
			total_batches = int(len(files)/batch_size)
		else:
			total_batches = int(int(len(files)/batch_size) + 1)
		while len(files) > 0:
			print('Batch {}/{} of images'.format(batch_nb, total_batches))				
			batch, files = files[:batch_size], files[batch_size:]
			multiple_files = []
			for image in tqdm(batch):
				image_name = image.split('/')[-1]
				multiple_files.append(('file', (image_name, open(image, 'rb'), 'image/jpeg')))
			response = session.post(url, 
						auth= requests.auth.HTTPBasicAuth(self.api_key, ''), 	
						files=multiple_files)
			responses.append(response)
			batch_nb+=1
		result = read_prediction_response(responses, self.model_type)
		return result

	def predict_for_urls(self, urls):
		"""
		function to get prediction for several images using their urls

		Parameters
		----------
		urls: List[str]
			list of urls of the images 

		Returns
		-------
		JSON repsonse of the predictions
		"""

		url = self.host + self.model_type + '/LabelUrls/'
		headers = {'accept': 'application/x-www-form-urlencoded'}
		params = {'modelId': self.model_id, 'urls': urls}
		response = requests.post(url,
					headers=headers,
					auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
					data=params) 
		result = read_prediction_response([response], self.model_type)
		return result
