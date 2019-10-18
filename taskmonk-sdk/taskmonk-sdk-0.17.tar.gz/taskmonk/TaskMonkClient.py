"""
This module allows TaskMonk to integrate the functionality of some functions

This tool accepts comma separated value files (.csv) as well as excel
(.xls, .xlsx) files.

This script requires that `requests` be installed within the Python
environment you are running this script in. Only python3 is supported.

This file can also be imported as a module and contains the following
functions:

    * create_batch - creates a batch for a projest and returns the response
    * upload_tasks -imports tasks from attached file. This is used to upload tasks from a local file
    * create_taxonomy - creates a taxonomy 

"""

from taskmonk.utils import urlConfig, apiCall, argumentlist, utilities
from taskmonk.utils.jsonUtils import json2obj
from datetime import datetime, timedelta
import sys



if sys.version_info.major >= 3:
    try:
        import urlparse
    except ImportError:
        import urllib.parse as urlparse

    from urllib.request import urlretrieve
else: 
    from urlparse import urlparse
    from urllib import urlretrieve

import base64
import gzip
import json
import requests
import logging
import os
import zlib
import urllib
from time import sleep

import ntpath

argsList = argumentlist.argsList
argumentVerifier = utilities.argumentVerifier

class Error(Exception):
   pass

class InvalidArguments(Error):
   pass

class TaskMonkClient:
    """
    A class used to access TaskMonk APIs

    """
    _base_url = urlConfig.BASE_URL
    _client_id = ''
    _client_secret = ''
    _project_id = ''
    _expires_at = None
    _access_token = None
    _refresh_token = None
    _proxy = {}

    def __init__(self, base_url, project_id, client_id = '', client_secret = '', proxy = {}):

        """
        Parameters
        ----------
        base_url : str
            a string that contains the url for the api to connect to
            Testing - preprod.taskmonk.io 
            Production - api.taskmonk.io

        project_id : str
            contains the id of specific project

        client_id : str
            contains the OAuth2 _client_id

        client_secret : str
            contains the OAuth2 _client_secret
        """

        self._base_url = base_url
        self._client_id = client_id
        self._client_secret = client_secret
        self._project_id = project_id
        self._proxy = proxy
    
    def _url_convert(self,url = ''):
        if not urlparse(url).scheme:
            url = "http://"+url
        print(url)
        return url

    
    def _refresh_token(self):
        """
        Gets the Access Token and Refersh Token from client id and client secret
        """
        token_url = self._base_url + '/api/oauth2/token'
        params =  {
            'grant_type': 'client_credentials',
            'client_id': self._client_id,
            'client_secret': self._client_secret
        }
        headers = {'accept': 'application/json'}
        response = requests.post(token_url,proxies = self._proxy,params= params,headers = headers)
        logging.debug(response.text)
        parsed = response.json()
        self._access_token = parsed['access_token']
        self._refresh_token = parsed['refresh_token']
        expires_in = parsed['expires_in']
        ## Keep a buffer of 120 seconds to refresh token before expiry
        self._expires_at = datetime.now() + timedelta(seconds=(expires_in - 120))

        logging.debug('access_token %s expires at %s', self._access_token, self._expires_at)

        return 

    
    def _is_expired(self): 
        """Checks the expiry of the acess token"""
        current_time = datetime.now()
        if (current_time > self._expires_at):
            logging.debug('token expired')
            return True
        else:
            return False

    def _get_token(self):
        """ Gets the refresh token if access token is expired"""
        if self._access_token is None or self._is_expired():
            self._refresh_token()
        return self._access_token


    def create_batch(self, batch_name, priority = 0, comments = '', notifications = []):
        """Create a new batch
        Parameters
        ----------
        batch_name: str
            Contains the name of the batch
        
        priority: Int
            An optional priority for the batch based on which tasks will be executed. 
            Higher priority batches are processed first.
        
        comments: str
            An optional message that is displayed to the analyst as they work on the tasks.
        
        notifications: Array of Notification
            Notifications can be used for the requestors to be notified when milestones for a batch are completed.
        ----------

        Returns
        -------
        str
            batch_id in response
        """

        url = self._base_url + urlConfig.URLS['Project'] + '/' + self._project_id + '/batch'
        batch = {
            "batch_name": batch_name,
            "priority": priority,
            "comments": comments,
            "notifications": [
            ]
        }
        data = json.dumps(batch)
        response = apiCall.post(self._get_token(), url,self._proxy,data, 30)
        logging.debug(response['id'])
        return response['id']
    
    def create_taxonomy(self, taxonomy_name):
        """Create a new taxonomy
        Parameters
        ----------
        taxonomy_name: str
            The name of the taxonomy
        ----------

        Returns
        -------
        str
            taxonomy_id as response
        """
        url = self._base_url + urlConfig.URLS['Project'] + '/' + self._project_id + '/taxonomy'
        data = json.dumps({'name': taxonomy_name})
        response = apiCall.post(self._get_token(), url,self._proxy, data, 30)
        taxonomy_id = response['id']
        return taxonomy_id

    def import_taxonomy(self, taxonomy_id, file_path, file_type = 'Excel'):
        """Import categories into the taxonomy
        Parameters
        ----------
        taxonomy_id: str
            Id for the taxonomy
        
        file_path: str
            Contains the path of the file from where the taxonomy should be imported

        Returns
        -------
        number
            count of categories imported
        """
        url = self._base_url + urlConfig.URLS['Project'] + '/v2/' + self._project_id + '/taxonomy' +   '/import?file_type=' + file_type
        file_name = ntpath.basename(file_path)
        files = {'file': open(file_path, 'rb').read()}
        response = apiCall.file_upload(self._get_token(), url,self._proxy, files, 30)
        return response['count']
    
    def upload_tasks(self, batch_id = None, input_file='', file_type = 'Excel'):
        """Upload tasks from a local CSV or Excel file
        Parameters
        ----------
        batch_id : str
        
        input_file: str
            Contains the path of the local file from which tasks are imported
        
        file_type: str
            Type of the file. Should be one of 'CSV' or 'Excel'
        

        Returns
        -------
        str
            job_id for the upload task
        """
        url = self._base_url + urlConfig.URLS['Project'] + '/v2/' + self._project_id + "/batch/" + batch_id + "/tasks/import?fileType=" + file_type
    
        logging.debug("Inside upload tasks")
        try:   
            if input_file.endswith('.gz'):
                fileContent = open(input_file, 'rb').read()
                encoded = base64.b64encode(fileContent)
            else:
                fileContent = open(input_file, 'rb').read()
                with gzip.open('file.txt.gz', 'wb') as f:
                    f.write(fileContent)
                fileContent = open('file.txt.gz', 'rb').read()
                encoded = base64.b64encode(fileContent)
                os.remove('file.txt.gz')
                response = requests.post(url, encoded, headers = {
                    'Content-Type': 'text/plain',
                    'Authorization': 'Bearer ' + self._get_token()})
                logging.debug("Resposne from upload tasks = %s",response.json())
                parsed = response.json()
                job_id = parsed['job_id']
                logging.debug('job id = %s', job_id)
                return job_id
    
        except Exception as e: print(e)

    
    def import_tasks_url(self,project_id = None, batch_id = None,file_url='', file_type = ''):
        """Upload tasks from a publicly accessible URL
        Parameters
        ----------
        file_url: str
            Contans the public url from which tasks should be imported

        Returns
        -------
        str
            job_id for the import task from url
        """
        url = self._base_url + urlConfig.URLS['Project'] + '/' + self._project_id + '/batch/' + batch_id + '/tasks/import/url'
    
        data = json.dumps({
            "file_url": file_url,
            "file_type": file_type
        })
    
        response = apiCall.post(self._get_token(), url,self._proxy, data, 30)
        logging.debug(response)
        return response.get('jobId')

    def get_job_progress(self, job_id):
        """Get the progress of an upload job
        Parameters
        ----------
        job_id : str
            The job_id from a previous upload call

        Returns
        -------
        Dictionary 
            'percentage', 'completed', 'total'
        """

        url = self._base_url + urlConfig.URLS['Project'] + '/' + self._project_id + '/job/' + job_id + '/status'
        response = apiCall.get(self._get_token(), url,self._proxy, {}, 10)
        logging.debug('response = %s', response)
        return response
    
    def is_job_complete(self, job_id):
        """ Helper method which checks job progress to see if it is complete
        Parameters
        ----------
        job_id: str
            job_id from a previous upload

        Returns
        -------
        boolean
            True - job progress is complete
            False - job progress is incomplete
        """

        job_status = self.get_job_progress(job_id)
        complete = job_status['completed']
        total = job_status['total']
        if (complete == total):
            return True
        else:
            return False

    def get_batch_status(self, batch_id):
        """Get Batch Status
        Parameters
        ----------
        batch_id : str
            
        Returns
        -------
        dictionary
            'not_started', 
            'in_progress', 
            'completed', 
            'total'
        """
    
        url = self._base_url + urlConfig.URLS['Project'] + '/' + self._project_id + '/batch/' + batch_id + '/status'
        response = apiCall.get(self._get_token(), url,self._proxy, {}, 10)
        return response

    def is_batch_complete(self, batch_id):
        """Helper method to check if processing is complete for a batch
        Parameters
        ----------
        batch_id: str
            Contains the batch id of a specific batch

        Returns
        -------
        boolean
            True - batch status is complete
            False - batch status is incomplete
        """

        batch_status = self.get_batch_status(batch_id)
        complete = batch_status['completed']
        total = batch_status['total']
        if (complete == total):
            return True
        else:
            return False

    def get_batch_output(self, batch_id, local_path, output_format = 'CSV', fields = []):
        """
        Parameters
        ----------
        batch_id: str
             Id for the batch

        local_path: str
            Path of the file where the ouput should be stored

        output_format: str
            Format of the output. Should be 'CSV' or 'Excel'
        
        fields: Array of String
            The fields that should be included in the output file. 
            The names should match the project configuration and the headers in the input file that was used for the task upload. 
            Pass an empty string to retrieve all fields

        Returns
        -------
        str
            local_path where the output is saved

        """
        url = self._base_url + urlConfig.URLS['Project'] + '/v2/' + self._project_id + '/batch/' + batch_id + '/output?output_format=' + output_format
        data = json.dumps({'field_names': fields})
        response = apiCall.post(self._get_token(), url,self._proxy, data, 30)
        file_url = response['file_url']
        job_id = response['job_id']
        self._wait_for_job_completion(job_id)
        logging.debug('file_url = %s', file_url)
        urlretrieve(file_url, local_path)
        return local_path
    
    def _get_batch(self):
        """ Retrieves batches for the project"""
        url = self._base_url + urlConfig.URLS['Project'] + '/' + self._project_id + '/batch'
        response = apiCall.get(self._get_token(), url,self._proxy, {}, 10)
        logging.debug(response)
        return response

    def _wait_for_job_completion(self, job_id): 
        """
        Parameters
        ----------
        job_id: str
            The JobId of a speific job
        ----------
        """
        while (not self.is_job_complete(job_id)): 
            logging.debug("waiting for job to complete") 
            sleep(1)
    

    def import_task_from_dictionary(self, batchId = None, dict = [{}]):
        """Imports tasks from dictionary
        Parameters
        ----------
        batchId: str
            Contains the id of the batch to import the tasks
        
        external_id: str
            A specific id mapped with task, used for correlation
        
        dict: Array of Dictionaries containing field name to values
            Dictionary is used to import task by the user
        ----------

        Returns
        -------
        str
            job_id in response
        """
        url = self._base_url + urlConfig.URLS['Project'] + '/' + self._project_id + '/batch/' + batchId + '/tasks/import/dictionary'
        data = json.dumps(dict)
        response = apiCall.post(self._get_token(), url, self._proxy, data, 30)
        print(response)
        return response
    
    def export_task_from_dictionary(self, batchId = None, export_data = {}):
        """Export tasks in dictionary format
        Parameters
        ----------
        batchId: str
            Contains the id of the batch to import the tasks
        ----------

        Returns
        -------
        items: a list of extrenal_id, batch_Id, data(key value pair where both are str)

        total: Integer
            Specifies the total number of tasks
        
        page: Ineteger
            Specifies the number of task on a particular page
        
        page_size: Integer
            Specifies the total number of pages present
        """
        url = self._base_url + urlConfig.URLS['Project'] + '/' + self._project_id + '/batch/' + batchId + '/output/dictionary'
        data = json.dumps(export_data)
        response = apiCall.post(self._get_token(), url,self._proxy, data, 30)
        print(response)
        return response

    def update_batch_status(self, batchId = None, state = ''):
        url = self._base_url + urlConfig.URLS['Project'] + '/' + self._project_id + '/batch/' + batchId + '/state'
        data = json.dumps({
            "state": state
        })
        response = apiCall.put(self._get_token(), url,self._proxy, data, 30)
        print(response)
        return response