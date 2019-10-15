import os
import re
import sys
import copy
import time
import datetime
import traceback
from pathlib import Path
from urllib.parse import urlparse

import json
import zipfile
import logging
import threading

import requests

from gradefast.exceptions import *
from gradefast import utils

class Spinner:
    busy = False
    delay = 0.1

    @staticmethod
    def spinning_cursor():
        while 1: 
            for cursor in '|/-\\': yield cursor

    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay): self.delay = delay

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()

    def start(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def stop(self):
        self.busy = False
        time.sleep(self.delay)


class Filter:
    '''A class for filtering team ids that are to be downloaded'''
    def __init__(self, list_of_teams=[], range_team_id=[]):
        self.list_of_teams = list_of_teams
        self.range_team_id = range_team_id

    def filter_by_range(self, key):
        if key.team_id >= self.left and key.team_id <= self.right:
            return True
        else: 
            return False

    def filter_by_collection(self, key):
        if key.team_id in self.list_of_teams:
            return True
        else: 
            return False
        
    def __call__(self, submissions, list_of_teams=[], range_team_id=[]):
        '''
        :type submission : Submission object
        :param submission : Submission object containing team ids, urls and id_tags dictionary.
        '''
        
        flag = 0 # 0: specific teams 1: range
        
        self.submissions = submissions
        if list_of_teams != None and len(list_of_teams) > 0:
            self.list_of_teams = list_of_teams
        
        if range_team_id != None and len(range_team_id) > 0:
            self.range_team_id = range_team_id

        if self.list_of_teams != None and len(self.list_of_teams) != 0:
            return list(filter(self.filter_by_collection, self.submissions))
        elif self.range_team_id != None and  len(self.range_team_id) != 0: 
            if self.range_team_id[0] > self.range_team_id[1] or len(self.range_team_id) != 1:
                self.left = range_team_id[0]
                self.right = range_team_id[1]

                return list(filter(self.filter_by_range, self.submissions))
            else:
                raise RangeError()
        else:
            raise FilterException()


def setup_logger(name, log_file, level=logging.INFO):
    '''Function setup as many loggers as you want'''

    formatter = logging.Formatter('%(asctime)s %(message)s')
    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    
    return logger


# TODO (manjrekarom):
# 1. Retry feature not implemented
class Download:
    ''' A utility class to download data from portal '''
    def __init__(self, cookie, storage_location = './', extract=False, 
                 keep_original=True, retry=True, retry_times=2):
        '''
        :type cookie : string
        :param cookie : Cookie
        
        :type storage_location : string
        :param storage_location : The location where the data is to be downloaded
        
        :type extract : Boolean
        :param extract : 

        :type keep_original : Boolean
        :param keep_original : 

        :type retry : Boolean
        :param retry : 

        :type retry_times : int
        :param retry_times : 

        '''
        self.cookie = cookie
        self.storage_location = storage_location
        self.extract = extract
        self.keep_original = keep_original
        self.retry = retry
        self.retry_times = retry_times


    @staticmethod
    def get_extension(url):
        o = urlparse(url)
        pattern = re.compile("\.([\w_]*)$")
        matches = pattern.search(o.path)
        return matches[1]


    @staticmethod
    def parent_folder_name(task_name, theme_name):
        directory_name = "{}_{}_{}".format(theme_name, task_name, datetime.datetime.now().strftime("%Y_%m_%d-%H_%M"))
        return directory_name


    @staticmethod
    def create_storage_directory(dir_path):
        if not os.path.isdir(dir_path):
            # file permission
            os.makedirs(dir_path, 0o755)
        return True


    @staticmethod
    def create_team_folder(team_id, dir_path):
        if type(team_id) == int:
            team_id = str(team_id)

        if not os.path.isdir(os.path.join(dir_path, team_id)):
            os.mkdir(os.path.join(dir_path, team_id))        

        return True


    @staticmethod
    def download_file(url, cookie, file_name, submission, storage_location):
        team_id = submission.team_id
        
        if type(team_id) == int:
            team_id = str(team_id)

        response = requests.get(url = url, allow_redirects=True, cookies=cookie)        
        file_extension = Download.get_extension(response.url)

        download_file_path = os.path.join(storage_location, team_id, '{}_{}.{}'.format(team_id, file_name, file_extension))
        
        with open(download_file_path, 'wb') as file:
            file.write(response.content)

        return download_file_path


    def __call__(self, submissions):
        '''
        :type submission : Submission object
        :param submission : Submission object containing required information like url,team_id,etc
        '''
        final_submissions = copy.deepcopy(submissions)

        # First make a parent folder
        parent_folder_name = Download.parent_folder_name(submissions.theme_name, submissions.task_name)
        dir_path = os.path.join(self.storage_location, parent_folder_name)
        
        if not Download.create_storage_directory(dir_path):
            raise Exception('Cannot create storage directory')
        self.storage_location = dir_path

        # Setting up download success and failure loggers
        self.logger1 = setup_logger('download_success', os.path.join(self.storage_location,'download_success.log'),level = logging.INFO)
        self.logger2 = setup_logger('download_failed', os.path.join(self.storage_location,'download_failed.log'),level = logging.INFO)

        cookie = {self.cookie['name']: self.cookie['value']}
        print('Download {} files:'.format(len(submissions)))
        spinner = Spinner()
        
        for submission in submissions:
            try:
                Download.create_team_folder(submission.team_id, dir_path)
                for file_name, meta in submission.items.items():
                    # download and save file
                    save_path = Download.download_file(meta['url'], cookie, file_name, submission, self.storage_location)
                    
                    sys.stdout.write('\b Success!\n')
                    self.logger1.info(str(submission.team_id) + ' ' + file_name + ' successfully downloaded.')

                    # add more meta information in newly created final submissions object
                    final_submissions[str(submission.team_id)].items[file_name]['downloaded'] = True            
                    final_submissions[str(submission.team_id)].items[file_name]['path'] = save_path

                    if Path(save_path).suffix == '.zip' and self.extract == True:
                        # unzip and store it
                        print('Extract')
                        extracted_path = Extract.extract(save_path)
                        unzipped_name = file_name.replace('zip', 'unzipped')
                        final_submissions[str(submission.team_id)].items[unzipped_name] = {}
                        final_submissions[str(submission.team_id)].items[unzipped_name]['path'] = extracted_path
                        final_submissions[str(submission.team_id)].items[file_name]['extracted'] = True
                        
                spinner.stop()

            except Exception as e:
                spinner.stop()
                print(traceback.print_exc())
                sys.stdout.write('\bFailed.. Trying next file\n')
                self.logger2.error("{}'s {} failed to download.".format(str(submission.team_id), file_name))
            
        # write a json to create a submissions object from
        # utils.Persist.to_json(submissions, save_location=path)
        return final_submissions, dir_path


class Extract:
    '''A class for extracting zips downloaded from the portals '''
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)
    
    @staticmethod
    def default_unzip_name(zip_path):
        zip_name = os.path.basename(zip_path)
        unzip_name = zip_name.replace('zip', 'unzipped', 1)
        unzip_name = unzip_name.replace('.zip', '', -1)
        unzip_path = os.path.join(os.path.dirname(zip_path), unzip_name)
        return unzip_path

    @staticmethod
    def extract(zip_path, extract_path=''):
        try:
            zip_ref = zipfile.ZipFile(zip_path, 'r')
            if extract_path == '' or extract_path == None:
                extract_path = Extract.default_unzip_name(zip_path)
            zip_ref.extractall(extract_path)
            zip_ref.close()
        except Exception as e:
            print(e)
            return False
        return extract_path
    
    def __call__(self, submissions):
        '''
        :type name_of_zip: string
        :param name_of_zip : The name of zip to be extrated

        :type extract_path: string
        :param extract_path: The location where the zip is to be extracted
        '''
        try:
            for submission in submissions:
                for file_name, meta in submission.items.items():
                    if file_name.startswith('zip'):
                        Extract.extract(submission.items[file_name]['path'])
        except Exception as e:
            print(e)
            return False
        return True


class Persist:
    # @staticmethod
    # def from_json(path_to_submission_json_file):
    #     # convert submissions array to json array
    #     submissions = []
    #     with open(path_to_submission_json_file, 'r') as f:
    #         submissions_dict_arr = json.loads(json.load(f))
    #         # print(len((submissions_dict_arr)[0]))
    #         for submission_dict in submissions_dict_arr:
    #             submissions.append(Submission(**submission_dict))
    #         return submissions

    @staticmethod
    def submission_group_to_json(submissions, name='submission.json', save_location='./'):
        # convert submissions array to json array
        json_list = []
        for i in submissions:
            json_list.append(i.__dict__)
        json_data = json.dumps(json_list)

        with open(os.path.join(save_location, name), 'w') as outfile:
            json.dump(json_data, outfile)
    
    @staticmethod
    def result_group_to_csv(result_group, name='result', save_location='./'):
        pass

    @staticmethod
    def to_database():
        pass


class Plagiarism:
    @staticmethod
    def check():
        pass


def findById(submissions, team_id):
    return Filter()(submissions, list_of_teams=[team_id])[0]

def subtract_dict(A, B):
    a_copy = A.copy()
    b_copy = B.copy()
    all(map(a_copy.pop, b_copy))
    return a_copy
    
def is_string_number(name):
    # check if the name of the folder is a number
    try:
        int(name)
        return True
    except ValueError:
        return False 
