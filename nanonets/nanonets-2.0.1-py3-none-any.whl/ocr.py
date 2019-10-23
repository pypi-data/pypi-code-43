import os
import json
import requests
from tqdm import tqdm
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from nanonets.model import Model
from nanonets.utils import *


class OCR(Model):

	def __init__(self, api_key, categories, model_id=None):
		super().__init__(api_key=api_key, model_type='ObjectDetection')
		if not model_id:
			self.create_model(categories)
		else:
			self.api_key = api_key
			self.categories = categories
			self.model_id = model_id
	
	def create_model(self, categories):
		"""
		function to create model given the categories and model type

		Parameters
		----------
		categories: List[str]
		    List of categories for our model

		Returns
		-------
		server response for the request for to create model
		"""

		url = self.host + self.model_type + '/Model/' 
		payload = json.dumps({"categories": categories, 
							  "model_type": "ocr"})
		headers = {'Content-Type': "application/json"}
		response =  requests.request("POST",
					     url, 
					     headers=headers, 
					     data=payload,
					     auth=requests.auth.HTTPBasicAuth(self.api_key, ''))
		self.model_id = response.json()["model_id"]
		print("Your Model ID is: ", self.model_id)

	def upload_image_file(self, img_path, annotation_path):
		"""
		function to upload a single file and it's annotation for training 

		Parameters
		----------
		img_path: str
		    path to the image we want to upload

		annotation_path: str
			path to the annotations for the same image

		Returns
		-------
		server response for the request for uploading image file and its annotation
		"""
		processed = [process_annotations(annotation_path)]
		annotation = json.dumps(processed)
		return self._upload_image_file(img_path, annotation)

	def upload_image_files(self, training_dict, batch_size=20):
		"""
		function to upload multiple files and their annotations 

		Parameters
		----------
		training_dict: Dict[str: str]
		    Dict with keys as image file paths and values as the corresponding annotation 
		    paths. Annotations can be XML or JSON

		batch_size (optional): int
			number of images to be uploaded per API request

		Returns
		-------
		a list of responses for each batch if images uploaded
		"""

		url = self.host + self.model_type + '/Model/' + self.model_id + '/UploadFile/'
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
				batch_data.append(process_annotations(img_name, training_dict[file]))
				batch_files.append(('file', (img_name, open(file, 'rb'), 'image/jpeg')))
			batch_files.append(('data', ('', json.dumps(batch_data))))
			response = requests.post(url, 
						 auth= requests.auth.HTTPBasicAuth(self.api_key, ''), 
						 files=batch_files)
			responses.append(response)
			batch_nb+=1
		return responses

	### UPLOAD IMAGES AND ANNOTATE THEM ON THE PLATFORM.
	def upload_image_url(self, image_url, annotation_path):
		pass

	### UPLOAD IMAGES AND ANNOTATE THEM ON THE PLATFORM.
	def upload_image_urls(self, training_dict):
		pass

	### FIGURE OUT ADDING URLS
	def train(self, training_dict, batch_size=20):
		"""
		function to upload a image files and annotations and initialize the training 

		Parameters
		----------
		training_dict: Dict[str: str]
		    Dict with keys as image file paths and values as the corresponding annotation 
		    paths. Annotations can be XML or JSON

		batch_size (optional): int
			number of images to be uploaded per API request

		Returns
		-------
		server response for the request for uploading files and annotation and initializing training
		"""

		print("Uploading images ...")
		self.upload_image_files(training_dict, batch_size=batch_size)
		print("Starting training ...")
		return self._train()

	def predict_for_file(self, file_path):
		"""
		function to get prediction for a single image file

		Parameters
		----------
		file_path: str 
			path of the image you want to get predictions for

		Returns
		-------
		JSON repsonse of the prediction 
		"""

		url = self.host + 'OCR/Model/' + self.model_id + '/LabelFile/'
		params = {'file': open(file_path, 'rb')}
		response = requests.post(url,
					auth=requests.auth.HTTPBasicAuth(self.api_key, ''),
					files=params) 
		result = read_prediction_response([response], 'OCR')
		return result

	def predict_for_url(self, image_url):
		"""
		function to get prediction for a single image url

		Parameters
		----------
		image_url: str
			url of the image you want to get predictions for

		Returns
		-------
		JSON repsonse of the prediction 
		"""

		response = self._predict_urls([image_url])
		result = read_prediction_response([response], 'OCR')
		return result

	def predict_for_files(self, files, batch_size=20):
		"""
		function to get predictions for multiple files 

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

		url = self.host + 'OCR/Model/' + self.model_id + '/LabelFile/'
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
				batch_files.append(('file', (img_name, open(file, 'rb'), 'image/jpeg')))
			batch_files.append(('data', ('', json.dumps(batch_data))))
			response = session.post(url, 
						auth=requests.auth.HTTPBasicAuth(self.api_key, ''), 
						files=batch_files)
			responses.append(response)
			batch_nb+=1
		result = read_prediction_response(responses, 'OCR')
		return result

	def predict_for_urls(self, urls):
		"""
		function to get prediction for several images using their urls 

		Parameters
		----------
		urls: List[str]
			list of urls of the images you want to get predictions for
		Returns
		-------
		JSON repsonse of the predictions
		"""

		response = self._predict_urls(urls)
		result = read_prediction_response([response], 'OCR')
		return result			
