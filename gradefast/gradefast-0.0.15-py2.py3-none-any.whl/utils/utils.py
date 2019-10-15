import os
import sys
import time
import datetime

import zipfile
import threading
import logging

import requests


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
    def __call__(self, submission):
        '''
        :type submission : Submission object
        :param submission : Submission object containing team ids, urls and id_tags dictionary.
        '''
        temp_team_ids = submission.getTeamids()
        
        team_ids = []
        id_tags = {}
        
        option = input('1. Display list of teams \n2. Download all')
        if option == '1' :
            temp_team_ids = [int(x) for x in temp_team_ids]
            temp_team_ids = sorted(temp_team_ids)
            for i in temp_team_ids:
                print(i)
            option1 = input('1. range \n2. specific teams')
            if option1 == 'range' or option1 =="1":
                value_from = int(input("Value from:"))
                value_to = int(input("Value to:"))
                value_from_index = temp_team_ids.index(value_from)
                value_to_index = temp_team_ids.index(value_to) + 1
                for i in range(value_from_index, value_to_index):
                    team_ids.append(str(temp_team_ids[i]))
                    id_tags[str(temp_team_ids[i])] = submission.id_tags[str(temp_team_ids[i])]
            
            if option1 == 'specific team' or option1 == '2':
                while True:
                    value = input('Enter team id')
                    team_ids.append(value)
                    id_tags[str(temp_team_ids[i])] = submission.id_tags[str(temp_team_ids[i])]
            
                    option2 = input('Do you want to continue?')
                    if option2=='No' or option2=='no':
                        break
        else:
            team_ids = []
            for i in range(0,len(temp_team_ids)):
                    team_ids.append(temp_team_ids[i])
                    id_tags[str(temp_team_ids[i])] = submission.id_tags[str(temp_team_ids[i])]
        
        submission.team_id = team_ids
        submission.id_tags = id_tags
        urls = []
        urls = list(id_tags.values())
        
        submission.urls = urls
        
        return submission


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
    def __init__(self, cookie, storage_location = '.', extract=False, 
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
        

    def __call__(self, submission):
        '''
        :type submission : Submission object
        :param submission : Submission object containing required information like url,team_id,etc

        '''
        # First make a parent folder
        directory_name = "{}_{}".format(submission.task, datetime.datetime.now().strftime("%Y_%m_%d-%H_%M"))
        path = os.path.join(self.storage_location, directory_name)
        if not os.path.isdir(path):
            os.makedirs(path, 0o755)
        self.storage_location = path

        # Setting up download success and failure loggers
        self.logger1 = setup_logger('download_success', os.path.join(self.storage_location,'download_success.log'),level = logging.INFO)
        self.logger2 = setup_logger('download_failed', os.path.join(self.storage_location,'download_failed.log'),level = logging.INFO)

        # Create a folder for every team and download every file inside the folder
        # TODO (manjrekarom): Paste a submissions log csv file with submissions downloaded 
        # marked as downloaded = True
        # This file should be kept in storage_location which will later be used to do `from_fs`
        # count = len(submission.team_id)

        cookie = {'eyrc_2018_session': self.cookie}
        print('Download {} files:'.format(len(submission.team_id)))
        spinner = Spinner()
        
        list_of_data = []
        team_ids = submission.team_id

        for i in range(0, len(team_ids)):
            idx = i
            url = submission.id_tags[team_ids[i]]
            sys.stdout.write('Downloading for Team-id: {}: '.format(team_ids[idx]))
            spinner.start()
            if not os.path.isdir(os.path.join(self.storage_location, team_ids[idx])):
                os.mkdir(os.path.join(self.storage_location, team_ids[idx]))        
        
            try:
                for u in url:
                    # print(u)
                    r = requests.get(url = u['href'], allow_redirects=True, cookies=cookie)
        
                    with open(os.path.join(self.storage_location, team_ids[idx], team_ids[idx] + '.' + u.get_text()), 'wb') as file:
                        file.write(r.content)
                        list_of_data.append(team_ids[idx]+ '.' + u.get_text())

                    sys.stdout.write('\b Success!\n')
                    self.logger1.info(team_ids[idx] + ' ' + u.get_text() + ' successfully downloaded.')
                spinner.stop()
                    
            except Exception as e:
                spinner.stop()
                sys.stdout.write('\bFailed.. Trying next file\n')
                self.logger2.info(team_ids[idx] + ' ' + u.get_text() + ' failed to download. ' + str(e))
                # self.errors.append([team_ids[idx],e])

        return list_of_data,self.storage_location


class Extract:
    '''A class for extracting zips downloaded from the portals '''
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)
    
    
    def __call__(name_of_zip, location_of_zips,target_path):
        '''
        :type name_of_zip: string
        :param name_of_zip : The name of zip to be extrated
        
        :type location_of_zips: string
        :param location_of_zips : The location where the zip is located
        
        :type target_path: string
        :param target_path: The location where the zip is to be extracted
        
        '''
        path_to_zip_file = location_of_zips + '\\' + name_of_zip
        directory_to_extract_to = target_path
        
        zip_ref = zipfile.ZipFile(path_to_zip_file, 'r')
        zip_ref.extractall(directory_to_extract_to)
        zip_ref.close()


class Persist:
    def to_csv():
        pass
    
    def to_database():
        pass
