import os
import json
import requests
from tqdm import tqdm
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from nanonets.model import Model
from nanonets.utils import *

class MultilabelClassification(Model):

	def __init__(self, api_key, categories, model_id=None):
		super().__init__(api_key=api_key, model_type='MultiLabelClassification')
		if not model_id:
			self._create_model(categories)
		else:
			self.api_key = api_key
			self.categories = categories
			self.model_id = model_id
	
	def upload_image_file(self, img_path, label_list):

		"""
		function to upload a single file and its labels for training to a model that 
		has been created.

		Parameters
		----------
		img_path: str
		    path to the image we want to upload

		label_list: List[str]
			list of all labels associated with the image

		Returns
		-------
		server response for the request for uploading urls. You can find response information
		from response.text
		"""

		return self._upload_image_file(self, img_path, label_list)

	def upload_image_files(self, training_dict, batch_size=20):		

		"""
		function to upload multiple files and their labels to a model that has been 
		created.

		Parameters
		----------
		training_dict: Dict[str: List[str]]
		    Dict with keys as image file paths and values as the corresponding list of 
		    labels

		batch_size (optional): int
			number of images to be uploaded per API request

		Returns
		-------
		a list of responses for each batch if images uploaded
		"""

		url = self.host + self.model_type + '/Model/' + self.model_id + '/UploadFiles/'
		files = list(training_dict.keys())
		batch_nb = 1
		if len(files)%batch_size == 0:
			total_batches = int(len(files)/batch_size)
		else:
			total_batches = int(int(len(files)/batch_size) + 1)
		responses = []
		while len(files) > 0:
			batch_files = []
			batch_data = []
			batch, files = files[:batch_size], files[batch_size:]
			print('Batch {}/{} of images'.format(batch_nb, total_batches))				
			for file in tqdm(batch):
				img_name = file.split('/')[-1]
				batch_data.append({'filename': img_name, 'categories': training_dict[file]})
				batch_files.append(('files', (img_name, open(file, 'rb'), 'image/jpeg')))
			batch_files.append(('data', ('', json.dumps(batch_data))))
			response = requests.post(url, 
						 auth=requests.auth.HTTPBasicAuth(self.api_key, ''), 
						 files=batch_files)
			responses.append(response)
			batch_nb+=1
		return responses

	def upload_image_url(self, image_url, label_list):

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
		server response for the request for uploading url. You can find response 
		information from response.text
		"""

		url = self.host + self.model_type + '/UploadUrls/'
		data = {'urls': [image_url],
			'modelId': self.model_id,
			'categories': label_list}
		headers = { 'accept': 'application/x-www-form-urlencoded'}
		response = requests.post(url,
					 headers=headers,
					 auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
					 data=data)
		return response

	def upload_image_urls(self, training_dict):

		"""function to upload images given by their urls to a model that has been created.
		The advantage of using URLs is that you can upload multiple images at the same time.

		Parameters
		----------
		training_dict: Dict[str: str]
		    Dict with keys as image file urls and values as the corresponding labels. 

		Returns
		-------
		server response for the request for uploading urls for each category. 
		You can find response information from response.text
		"""

		url = self.host + self.model_type + '/UploadUrls/'
		data = {'urls': list(training_dict.keys()),
			'modelId': self.model_id,
			'categories': list(training_dict.values())}
		headers = { 'accept': 'application/x-www-form-urlencoded'}
		response = requests.post(url,
					 headers=headers,
					 auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
					 data=data)
		return response

	def train(self, training_dict, data_path_type='files', batch_size=20):

		"""
		function to upload image files/urls with their labels and initialise model training 

		Parameters
		----------
		training_dict: Dict[str: List[str]]
		    Dict with keys as image file urls/paths and values as the corresponding list of 
		    labels.

		data_path_type: str
			Can take values 'files' or 'urls'

		Returns
		-------
		server response for the request for uploading urls. You can find response information
		from response.text
		"""
		if data_path_type == 'files':		
			self.upload_image_files(training_dict, batch_size=batch_size)
		elif data_path_type == 'urls':
			self.upload_image_urls(training_dict)
		return self._train()

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
		url = self.host + self.model_type + '/Model/' + self.model_id + '/LabelFiles/'
		params = {'files': open(file_path, 'rb'), 'modelId': ('', self.model_id)}
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

		response = self._predict_urls([image_url])
		result = read_prediction_response([response], self.model_type)
		return result

	def predict_for_files(self, files, batch_size=20):

		"""
		function to get predictions for multiple files 

		Parameters
		----------
		files: List[str]
		    List of image file paths/urls

		batch_size (optional): int
			number of images to be uploaded per API request

		Returns
		-------
		Dict with file names as keys and the predictions as values
		"""

		url = self.host + self.model_type + '/Model/' + self.model_id + '/LabelFiles/'
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
			batch, files = files[:batch_size], files[batch_size:]
			batch_files = []
			batch_data = []
			print('Batch {}/{} of images'.format(batch_nb, total_batches))				
			for file in tqdm(batch):
				img_name = file.split('/')[-1]
				batch_data.append({'filename': img_name})
				batch_files.append(('files', (img_name, open(file, 'rb'), 'image/jpeg')))
			batch_files.append(('data', ('', json.dumps(batch_data))))
			response = session.post(url, 
						auth=requests.auth.HTTPBasicAuth(self.api_key, ''), 
						files=batch_files)
			responses.append(response)
			batch_nb+=1
		result = read_prediction_response(responses, self.model_type)
		return result

	def predict_for_urls(self, urls):

		"""
		function to get prediction for a single image file from a trained model

		Parameters
		----------
		file_path: List[str]
			list of urls of the images you want to get predictions for
		Returns
		-------
		JSON repsonse of the prediction 
		"""
		response = self._predict_urls(urls)
		result = read_prediction_response([response], self.model_type)
		return result

		
