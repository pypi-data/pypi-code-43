from ..exception.s3_exception import S3Exception,S3UploadException,S3DownloadException
import sys
import boto3
from boto3.session import Session
import logging
import os
import shutil
import hashlib
import random

logging.basicConfig()
LOGGER = logging.getLogger('s3')
LOGGER.setLevel(logging.DEBUG)

class ProgressPercentage(object):
	def __init__(self,file_size,filename):
		self._filename = filename
		self._file_size = int(file_size)
		self._seen_so_far = 0
	def __call__(self, bytes_amount):
		# To simplify, assume this is hooked up to a single filename
		self._seen_so_far += bytes_amount
		percentage = (self._seen_so_far / self._file_size) * 100
		sys.stdout.write("\r%s  %s / %s  (%.2f%%)" % (self._filename, self._seen_so_far, self._file_size,percentage))
		sys.stdout.flush()

class WCS():
	"""
		WSS3 SDK Operation using temporary AK/SK
	"""
	def __init__(self, endpoint_url=None, ak=None, sk=None, region=None, security_token=None, is_secure=True, path_style=True,method="http"):
		"""AK SK and security_token comes from IAM's temporary AK/SK API
		"""
		if ak is None or sk is None or endpoint_url is None:
			raise Exception("Parameter is illegal!")

		self.endpoint_url = endpoint_url
		self.ak = ak
		self.sk = sk
		self.region = region
		self.session = Session(aws_access_key_id=self.ak,aws_secret_access_key=self.sk, region_name=self.region)
		if method == "http" and self.endpoint_url.startswith("http://") == False and self.endpoint_url.startswith("https://") == False:
			self.endpoint_url = "http://"+self.endpoint_url	
		if method == "https" and self.endpoint_url.startswith("https://") == False and self.endpoint_url.startswith("http://") == False:
			self.endpoint_url = "https://"+self.endpoint_url
		self.s3 = self.session.resource('s3', endpoint_url=self.endpoint_url)
		self.client = self.session.client('s3', endpoint_url=self.endpoint_url)

	def check_bucket_path(self, bucket_path):
		if bucket_path.startswith('/'):
			bucket_path = bucket_path[1:]
		if bucket_path.endswith('/') == False:
			raise ValueError("bucket_path is must end of '/'")
		bucket, key = bucket_path.split('/',1)

		return bucket, key

	def upload_object( self, bucket, key, bucket_path, local_file_path):
		"""put local file to s3
			if the bucket_name does not exist in S3, then it will throw 404 exception
			if the bucket path does not exist in the bucket Name, then it will be created
			if S3 has existed the file in the specified path, then it will be overwritten
		"""
		try:
			if not os.path.exists(local_file_path):
				raise Exception("File " + local_file_path + " does not exist!")
			file_name = os.path.split(local_file_path)[-1]

			cloud_path = os.path.join(key,file_name)
			resp = self.client.upload_file(Bucket=bucket, Key=cloud_path, Filename=local_file_path, Callback=ProgressPercentage(os.path.getsize(local_file_path),cloud_path))
			print("")
			LOGGER.info("Successfully upload file %s to S3 %s" % (local_file_path, bucket_path))
#		except S3UploadException:
#			raise S3Exception(code=resp.errorCode, message=resp.errorMessage)
		except Exception as e:
			raise Exception("Upload file to S3 failed! ", e)

	def put_object( self, bucket, key, bucket_path, local_file_path):
		"""put local file to s3
			if the bucket_name does not exist in S3, then it will throw 404 exception
			if the bucket path does not exist in the bucket Name, then it will be created
			if S3 has existed the file in the specified path, then it will be overwritten
		"""
		try:
			if not os.path.exists(local_file_path):
				raise Exception("File " + local_file_path + " does not exist!")
			file_name = os.path.split(local_file_path)[-1]

			cloud_path = os.path.join(key,file_name)
			resp = self.client.put_object(Bucket=bucket, Key=cloud_path, Body=open(local_file_path, 'rb'))

			LOGGER.info("Successfully upload file %s to S3 %s" % (local_file_path, bucket_path))
#		except S3UploadException:
#			raise S3Exception(code=resp.errorCode, message=resp.errorMessage)
		except Exception as e:
			raise Exception("Upload file to S3 failed! ", e)

	def upload_directory(self, bucket, key, bucket_path, local_directory):
		"""put multi local files to S3
			if the bucket_name does not exist in S3, then it will throw 404 exception
			if the bucket path does not exist in the bucket Name, then it will be created
			if S3 has existed the file in the specified path, then it will be overwritten
		"""
		#print(bucket,key,bucket_path)
		if not os.path.exists(local_directory):
			raise Exception("Directory " + local_directory + " does not exist!")
		dir_name = os.path.split(local_directory)[-1] #获取顶级目录名
		dir_list=[]
		file_list=[]
		g_dir_file = os.walk(local_directory)
		for path, dirs, files in g_dir_file:
				tmp_path = path
				sub_dir = tmp_path.split(local_directory)
				create_dir_name = dir_name + sub_dir[1] #顶级目录名+子目录
				dir_list.append(create_dir_name)
				for file_name in files:
						file_list.append((create_dir_name,os.path.join(path, file_name)))
		#print(dir_list)
		#print(file_list)
		for item in dir_list:
			try:
				self.create_directory(bucket, key, item)
			except Exception as e:
				raise Exception("create_directory to S3 failed! ", e)
		for key_sub, directory in file_list:
			try:
				cloud_path = os.path.join(key, key_sub)
				self.upload_object(bucket, cloud_path, os.path.join(bucket_path,key_sub), directory)
			except Exception as e:
				raise Exception("Upload file to S3 failed! ", e)

	def put_multi_objects(self, bucket, key, bucket_path, local_file_paths):
		"""put local directory to S3, splitted using ','
			if the bucket_name does not exist in S3, then it will throw 404 exception
			if the bucket path does not exist in the bucket Name, then it will be created
			if S3 has existed the file in the specified path, then it will be overwritten
		"""
		for local_file_path in local_file_paths:
			try:
				if not os.path.exists(local_file_path):
					raise Exception("File " + local_file_path + " does not exist!")
				if os.path.isdir(local_file_path):
					self.upload_directory(bucket, key, bucket_path, local_file_path)
				else:
					self.upload_object(bucket, key, bucket_path, local_file_path)
			except Exception as e:
				raise Exception("Upload multi files to S3 failed! ", e)

	def calculate_local_md5(self,file_path):
		with open(file_path, 'rb') as f:
			d = f.read()
		h = hashlib.md5()
		h.update(d)
		result = h.hexdigest()
		return result

	def calculate_local_md5_content(self,content):
		h = hashlib.md5()
		h.update(content)
		result = h.hexdigest()
		return result

	def download_object_v2(self, bucket_path, local_file_name):
		"""download s3 file to your local file
			if local path has existed the file, then it will be overwritten
		"""
		try:
			bucket_path_split = bucket_path.split('/',1)
			bucket_name = bucket_path_split[0]
			object_name = bucket_path_split[1]
			remote_object = self.s3.Object(bucket_name,object_name)
			remote_etag = eval(remote_object.e_tag)
			remote_size = remote_object.content_length
			#print(bucket_name,object_name,local_file_name)
			if os.path.exists(local_file_name):
				file_size = os.path.getsize(local_file_name)
				local_md5 = self.calculate_local_md5(local_file_name)
				#print(local_file_name,file_size,remote_size)
				if file_size < remote_size:
					range_str="bytes=%s-%s"%(str(file_size),str(remote_size))
					remote_req = self.client.get_object(Bucket=bucket_name,Key=object_name,Range=range_str)
					remote_content = remote_req['Body'].read()
					with open(local_file_name, 'rb') as file_obj:
						local_content = file_obj.read()
					final_content = local_content + remote_content
					local_etag = self.calculate_local_md5_content(final_content)
					if local_etag == remote_etag:
						with open(local_file_name, 'ab') as file_obj:
							file_obj.write(remote_content)
					else:
						LOGGER.info("Loal file is different remote file, cannot resume from break-point")
			else:
				self.client.download_file(Bucket=bucket_name, Key=object_name, Filename=local_file_name,Callback=ProgressPercentage(remote_object.content_length,local_file_name))
		except Exception as e:
			raise Exception("Download file from S3 failed! ", e)

	def download_object(self, bucket_path, local_file_path):
		"""download S3 file to your local file
			if local path has existed the file, then it will be overwritten
		"""
		try:
			bucket_path_split = bucket_path.split('/',1)
			bucket_name = bucket_path_split[0]
			object_name = bucket_path_split[1]
			file_name = object_name.split('/')[-1]
			local_file_path = os.path.join(local_file_path, file_name)
			remote_object = self.s3.Object(bucket_name,object_name)
			remote_etag = eval(remote_object.e_tag)
			if os.path.exists(local_file_path):
				local_md5 = self.calculate_local_md5(local_file_path)
				if local_md5 == remote_etag:
					LOGGER.info("The %s is not modified, md5sum = %s, so don't neet to download %s"%(local_file_path,local_md5,object_name))
				else:
					resp = self.client.download_file(Bucket=bucket_name, Key=object_name, Filename=local_file_path,Callback=ProgressPercentage(remote_object.content_length,local_file_path))
					print("")
					LOGGER.info('download_file:'+ os.path.join(bucket_name, object_name) + ' to ' + local_file_path)
			else:
				resp = self.client.download_file(Bucket=bucket_name, Key=object_name, Filename=local_file_path,Callback=ProgressPercentage(remote_object.content_length,local_file_path))
				print("")
				LOGGER.info('download_file:'+ os.path.join(bucket_name, object_name) + ' to ' + local_file_path)
		except Exception as e:
			raise Exception("Download file from S3 failed! ", e)

	def mkdir_file(self,file_path):

		path, file_name  = os.path.split(file_path)
		folder = os.path.exists(path)
		if not folder:                   #判断是否存在文件夹如果不存在则创建为文件夹
		    os.makedirs(path)            #makedirs 创建文件时如果路径不存在会创建这个路径
#		file1 = open(file_path,'w')
#		file1.close()
#		return path

	def download_directory(self, bucket, key, bucket_path, local_storage_path):
		"""download S3 directory to your local path
			if local path has existed the file, then it will be overwritten
		"""
		dir_name = bucket_path.split('/')[-2]
		try:
			resp = self.client.list_objects(Bucket=bucket, Prefix=key)
			if resp.get('Contents'):
				for obj in resp['Contents']:
					combine_path = os.path.join(dir_name, obj['Key'].split(key)[1])
					local_file_path = os.path.join(local_storage_path, combine_path)
					if os.path.exists(local_file_path):
						local_md5 = self.calculate_local_md5(local_file_path)
						remote_object = self.s3.Object(bucket,obj['Key'])
						remote_etag = eval(remote_object.e_tag)
						#print(type(local_md5),local_md5,len(local_md5),type(remote_etag),remote_etag,len(remote_etag))
						if local_md5 == remote_etag:
							LOGGER.info("The %s is not modified, md5sum = %s, so don't neet to download %s"%(local_file_path,local_md5,obj['Key']))
						else:
							self.mkdir_file(local_file_path)
							resp = self.client.download_file(Bucket=bucket, Key=obj['Key'], Filename=local_file_path, Callback=ProgressPercentage(obj['Size'],local_file_path))
							print("")
							LOGGER.info('download_dir:'+ os.path.join(bucket, obj['Key']) + ' to ' + local_file_path)
					else:
						self.mkdir_file(local_file_path)
						resp = self.client.download_file(Bucket=bucket, Key=obj['Key'], Filename=local_file_path, Callback=ProgressPercentage(obj['Size'],local_file_path))
						print("")
						LOGGER.info('download_dir:'+ os.path.join(bucket, obj['Key']) + ' to ' + local_file_path)
			else:
				LOGGER.error('download_dir:'+ bucket_path+ " is NULL!")
		except Exception as e:
			raise Exception("Download directory from S3 failed! ", e)

	def create_directory(self, bucket, key, directory):
		"""
		Create a directory in bucket.
		"""

		if directory[-1] != "/":
			directory = directory + "/"
		
		if directory[0]  == "/":
			directory = directory[1:]
		cloud_directory = os.path.join(key, directory)
		try:
			create_dir_resp = self.client.put_object(Bucket=bucket, Key=cloud_directory)
		except Exception as e:
			raise Exception("create_dir directory to S3 failed! ", e)
		LOGGER.info('create_dir:'+ os.path.join(bucket,cloud_directory))

	def delete_directory(self, bucket, key, directory):
		"""
		Delete a directory in bucket.
		"""
		if directory[-1] != "/":
			directory = directory + "/"
		
		if directory[0]  == "/":
			directory = directory[1:]
		cloud_directory = os.path.join(key, directory)
		try:
			resp = self.client.list_objects(Bucket=bucket, Prefix=cloud_directory)
			if resp.get('Contents'):
				for obj in resp['Contents']:
					delete_dir_resp = self.client.delete_object(Bucket=bucket, Key=obj['Key'])
			else:
				delete_dir_resp = self.client.delete_object(Bucket=bucket, Key=cloud_directory)
		except Exception as e:
			raise Exception("delete_dir directory to S3 failed! ", e)
		LOGGER.info('delete_dir:'+ os.path.join(bucket,cloud_directory))


