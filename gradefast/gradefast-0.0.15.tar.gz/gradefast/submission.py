"""
Contains :class:`Submission` and :class:`SubmissionGroup` classes that represent `submission` 
of a single `team` (or student) and `many teams` (or many students), respectively.

:class:`LoadSubmissions` is a utility class to quickly populate a :class:`SubmissionGroup` from
sources like `web portal`, `filesystem` or `databases`.
"""

import os
import re
import json
import fnmatch
from os import listdir
from typing import Union
from os.path import isfile, join
import urllib.request as urllib2

import requests
from bs4 import BeautifulSoup

from gradefast.exceptions import *
from gradefast import utils

from urllib.response import addinfourl

class Submission(object):
    """
    Represents a team (or student) submission information

    A :class:`Submission` contains information about a team's uploaded task items like images, 
    text files or zips, on the web, filesystem or databases. Gradefast uses this information 
    in utility classes like :class:`~gradefast.utils.Download` to download files locally. It 
    also uses it to search and provide files to a :class:`~gradefast.test.GFTest` when executed 
    from within an :class:`~gradefast.test.Evaluate` 
    
    Parameters
    ----------
    team_id : int
        Identifier of a team (or student)
    items : dict
        Dictionary of uploaded items. ``e.g. {'zip': {'url': 'https://e-yantra.org/some.zip'}, 
        'png': {'url': 'https://e-yantra.org/some.zip'}}``

    Attributes
    ----------
    team_id : int
    items : dict

    """
    def __init__(self, team_id: int, items: dict):
        # Identified by team id. should be a number
        if type(team_id) == str and utils.is_string_number(team_id):
            self.team_id = int(team_id)
        else:
            self.team_id = team_id
        # Dictionary of items uploaded and their metadata like path on filesystems
        self.items = items
    
    def __repr__(self):
        return "Submission(" + self.__dict__.__str__() + ")"

    def __str__(self):
        return self.__repr__()

    def __eq__(self, value):
        if not isinstance(value, Submission):
            return False
        if self.team_id != value.team_id:
            return False
        if self.items != value.items:
            return False
        return True

    def __ne__(self, value):
        return not self.__eq__(value)

    def to_dict(self):
        """
        Converts from :class:`Submission` to a :class:`dict`

        Returns
        -------
        dict

        """
        return self.__dict__

    @staticmethod
    def from_dict(submission_dict: dict):
        """
        Creates a :class:`Submission` from a :class:`dict`.

        Parameters
        ----------
        result: dict
            Should contain `keys` `team_id`, `file` and `result_dict`. Can optionally contain
            `comment` and `pkg_path`. 

        Returns
        -------
        :class:`Result`
            A :class:`Result` built from the result dictionary

        """
        return Submission(submission_dict['team_id'], submission_dict['items'])

class SubmissionGroup:
    """
    Groups many :class:`Submission` together

    A :class:`SubmissionGroup` clubs multiple :class:`Submission` together and includes 
    additional information like ``task_name`` and ``theme_name``. 

    Parameters
    ----------
    task_name: str
    theme_name: str
    submissions: list, dict
        List or dictionary of submissions. If dictionary, key should be a team_id 
        and value should be a :class:`Submission`

    Attributes
    ----------
    task_name: str
    theme_name: str
    dict_of_submissions: dict
        A dictionary of submissions where `key` is a team_id and `value` is a :class:`Submission`

    Warnings
    ---------    
    :class:`SubmisisonGroup` is an iterator. Try not to mutate it and expect it to work fabulously thereafter.
    
    """
    def __init__(self, task_name: str, theme_name: str, submissions: Union[list, dict]):
        self.task_name = task_name
        self.theme_name = theme_name
        if type(submissions) == list:
            submissions = {int(submission.team_id) if type(submission.team_id) == str else submission.team_id: submission for submission in submissions}
        self.dict_of_submissions = submissions
        self._iter = iter(self.dict_of_submissions)

    # TODO: need to safely remove this
    def sort_by_team_id(self):
        # used for finding submissions faster
        self.dict_of_submissions = sorted(
            self.dict_of_submissions, 
            key = lambda submission: submission.team_id)

    def __iter__(self):
        return self
    
    def __len__(self):
        return len(self.dict_of_submissions)

    def __next__(self):
        try:
            self.curr_idx = next(self._iter)
            idx = self.curr_idx
            return self.dict_of_submissions[self.curr_idx]
        except StopIteration:
            self._iter = iter(self.dict_of_submissions)
            raise StopIteration
    
    def __getitem__(self, team_id: int) -> Submission:
        try:
            if isinstance(team_id, slice):
                dict_of_submissions = {}
                for ii in range(*team_id.indices(team_id.stop)):
                    if self[ii] != None:
                        dict_of_submissions[ii] = self[ii]
                return SubmissionGroup(self.task_name, self.theme_name, dict_of_submissions)
            elif type(team_id) == str:
                if self.dict_of_submissions.get(team_id) != None:
                    return self.dict_of_submissions[team_id]
                elif self.dict_of_submissions.get(int(team_id)) != None:
                    return self.dict_of_submissions[int(team_id)]
            elif type(team_id) == int:
                if self.dict_of_submissions.get(team_id) != None:
                    return self.dict_of_submissions[team_id]
                elif self.dict_of_submissions.get(str(team_id)) != None:
                    return self.dict_of_submissions[str(team_id)]
        except KeyError:
            return None

    def __eq__(self, value) -> bool:
        if not isinstance(value, SubmissionGroup):
            return False
        if self.task_name != value.task_name:
            return False
        if self.theme_name != value.theme_name:
            return False
        if self.dict_of_submissions != value.dict_of_submissions:
            return False
        return True

    def __ne__(self, value):
        return not self.__eq__(value)

    def __repr__(self):
        return "SubmissionGroup(task_name: {}, theme_name: {}, dict_of_submissions: {})".format(self.task_name, self.theme_name, self.dict_of_submissions)

    def __str__(self):
        return self.__repr__()

    # TODO: need to safely remove this
    def find_by_id(self, team_id):
        # find submission quickly by exploiting the fact that submissions are stored in sorted order
        try:
            return self.dict_of_submissions[team_id]
        except KeyError:
            return None

    @staticmethod
    def from_dict(group_dict):
        """
        Creates a :class:`SubmissionGroup` from a :class:`dict`

        Parameters
        ----------
        group_dict: dict

        Returns
        -------
        :class:`SubmissionGroup`

        """
        dict_of_submissions = {}
        for team_id, submission in group_dict['dict_of_submissions'].items():
            if type(team_id) == str:
                dict_of_submissions[int(team_id)] = Submission.from_dict(submission)
            else:
                dict_of_submissions[team_id] = Submission.from_dict(submission)
        return SubmissionGroup(group_dict['task_name'], group_dict['theme_name'], dict_of_submissions)

    def to_dict(self):
        """
        Converts from :class:`SubmissionGroup` to a :class:`dict`
        
        Returns
        -------
        dict

        """
        group_dict = {}
        group_dict['task_name'] = self.task_name
        group_dict['theme_name'] = self.theme_name
        group_dict['dict_of_submissions'] = {}
        # print(self.dict_of_submissions)
        for team_id, submission in self.dict_of_submissions.items():
            group_dict['dict_of_submissions'][team_id] = submission.__dict__

        return group_dict

    @staticmethod
    def from_json(file_path):
        """
        Create a :class:`SubmissionGroup` from a json file

        Parameters
        ----------
        file_path: str
            Path to json file

        Returns
        -------
        :class:`SubmissionGroup`

        """
        if os.path.isdir(file_path):
            file_path = os.path.join(file_path, 'submission.json')
        # print(file_path)
        with open(file_path, 'r') as json_file:
            group_dict = json.load(json_file)
            return SubmissionGroup.from_dict(group_dict)

    def to_json(self, save_path):
        """
        Save a :class:`SubmissionGroup` object to json file

        Parameters
        ----------
        save_path: str
            Path to json file or directory

        Returns
        -------
        None

        """
        if os.path.isdir(save_path):
            save_path = os.path.join(save_path, 'submission.json')
        with open(save_path, 'w+') as json_file:
            group_dict = self.to_dict()
            json.dump(group_dict, json_file)

class LoadSubmissions:
    """
    A utility class to load submission information from web portal, filesystem or databases

    Use this class to populate information about submission from web page or filesystem. Unless 
    you want to create only a few :class:`Submission` objects for testing, :attr:`~LoadSubmissions.get_submissions()`
    of this class should be the preferred way to load and create a :class:`SubmissionGroup`.

    .. note::

        :class:`LoadSubmissions` is never instantiated directly. Use either :attr:`LoadSubmissions.from_url`
        or :attr:`LoadSubmissions.from_fs` 

    Parameters
    ----------
    cookie: str
        HTTP cookie obtained from the logged in session on the web portal
    task_url: str
        Url of the web page showing information to download files. 
        ``e.g. 'http://old.e-yantra.org/admin/grade/task0'``
    task_name: str
    theme_name: str
    fs_location: str
        Filesystem location where the downloaded files were stored. You can use this option for 
        testing by creating the directory structure according to downloading conventions
    types: list
        List of items to download from all the items available. ``e.g. ['zip', 'png2', 'txt1']``
    scraper: str, :class:`Scraper`
        If 'default', then use :class:`DefaultScraper`, else use provided :class:`Scraper`

    Attributes
    ----------
    cookie: str
    task_url: str
    task_name: str
    theme_name: str
    fs_location: str
    types: list
    scraper: str, :class:`Scraper`

    """
    def __init__(self, cookie: str = '', task_url: str = '', task_name: str = '', theme_name: str = '', 
    fs_location: str = '', types: list = ['zip'], scraper: Union[str, object] = 'default'):
        # Top level LoadSubmissions
        # Not supposed to be used directly
        # Use either LoadSubmissions.from_fs or LoadSubmissions.from_url
        self.cookie = cookie
        self.task_url = task_url
        self.task_name = task_name
        self.theme_name = theme_name
        self.fs_location = fs_location
        # file types to download
        self.types = types
        self.scraper = scraper

    @staticmethod    
    def from_url(task_url: str, cookie: str, task_name: str, theme_name: str, types: list = ['zip'], 
    method: Union[str, object]='default'):
        """
        Creates a :class:`LoadSubmissions` object with information necessary to fetch submissions
        from a web page

        Parameters
        ----------
        task_url: str
        cookie: str
        task_name: str
        theme_name: str
        types: list

        Returns
        -------
        :class:`LoadSubmissions`
        """
        # Constructor used to create submission objects from url
        return LoadSubmissions(task_url=task_url, task_name=task_name, cookie=cookie, types=types, 
        scraper = method, theme_name=theme_name)

    @staticmethod
    def from_fs(fs_location: str, task_name: str, theme_name: str):
        """
        Creates a :class:`LoadSubmissions` object with information necessary to fetch submissions
        from a filesystem location

        Parameters
        ----------
        fs_location: str
        task_name: str
        theme_name: str

        Returns
        -------
        :class:`LoadSubmissions`
        """
        # Constructor used to create submission objects from fs
        return LoadSubmissions(fs_location=fs_location, theme_name=theme_name, task_name=task_name)
  
    def _make_submissions_from_fs(self):
        submissions = []
        for idx, dir_item in enumerate(os.listdir(self.fs_location)):
            # convention 1: names of folders are team ids
            if not utils.is_string_number(dir_item):
                continue    
            print('Team-id = ', int(dir_item))
            team_id = dir_item

            # go inside the folder and store the file_paths of downloaded items for offline working only               
            items = {}

            file_paths = {}
            size_dict = {}
            
            # go over the items of the student team submission
            # if it's a file make an entry for it in size_dict
            # if it's a directory named <team_id>_unzipped* then add it to file_paths
            for idx, team_item in enumerate(os.listdir(os.path.join(self.fs_location, dir_item))):
                file_full_path = os.path.join(self.fs_location, dir_item, team_item)
                
                if os.path.isfile(file_full_path):
                    # remember all the extensions and file names with that particular extension
                    file_name, file_extension = os.path.splitext(os.path.basename(file_full_path))
                    # removing the . from extension. e.g. .txt to txt
                    file_extension = file_extension[1:]
                    if size_dict.get(file_extension) == None:
                        size_dict[file_extension] = []
                        # items[file_extension] = {}
                    size_dict[file_extension].append(file_full_path)
                    # items[file_extension]['path'] = file_full_path
                    # print('File paths = {} \n' % 5)
                elif team_item.startswith(team_id + "_unzipped"):
                    # a proper file name will consist of <team_id>_<extension><number>
                    parition_name = team_item.split(team_id + "_unzipped")
                    if len(parition_name) > 2:
                        continue
                    else:
                        if parition_name[0] == '':
                            if utils.is_string_number(parition_name[1]) or parition_name[1] == '':
                                self._add_to_paths_and_items(items, "unzipped" + parition_name[1], 
                                file_paths, file_full_path)

            for file_extension, file_list in size_dict.items():
                if len(file_list) == 1:
                    self._add_to_paths_and_items(items, file_extension, file_paths, file_list[0])
                else:
                    for file_path in file_list:
                        match_pattern = team_id + "_" + file_extension
                        file_name, _ = os.path.splitext(os.path.basename(file_path))
                        # a proper file name will have <team_id>_<extension><number>
                        file_name_parts = file_name.split(match_pattern)
                        if len(file_name_parts) > 2:
                            continue
                        else:
                            if file_name_parts[0] == '' and self.is_string_number(file_name_parts[1]):
                                self._add_to_paths_and_items(items, file_extension + file_name_parts[1], file_paths, file_full_path)
            submission = Submission(team_id, items)
            submissions.append(submission)
        return SubmissionGroup(self.task_name, self.theme_name, submissions)

    def _add_to_paths_and_items(self, items: dict, item_name: str, file_paths: dict, file_full_path: str):
        file_paths[item_name] = file_full_path
        if (item_name) not in items:
            items[item_name] = {}
        items[item_name]['path'] = file_full_path
        items[item_name]['downloaded'] = True

    def get_submissions(self):
        """
        Returns a :class:`SubmissionGroup` after populating it with information from
        web page or filesystem

        Based on the method used for fetching, `url` or `fs`, the resulting :class:`SubmissionGroup`
        will differ. For example, a :class:`SubmissionGroup` created from manually made directory
        structure won't contain a url key in :attr:`~Submission.items` 

        Returns
        -------
        :class:`SubmissionGroup`

        """
        # scrape urls and other data from webpage
        # returned by the scraper being used
        submissions = []
        if self.task_url != '':
            if self.scraper == '' or self.scraper == 'default':
                self.scraper = DefaultScraper
            else:
                # TODO (manjrekarom): Use custom scraper
                pass

            team_ids, id_tags = self.scraper(self.task_url, self.cookie, self.types).scrape_data_from_page()
            
            # fill all data inside the submission object
            # TODO:
            for team_id in team_ids:
                items = {}
                for j in id_tags[team_id]:
                    if j.get_text() not in items:
                        items[j.get_text()] = {}
                    items[j.get_text()]['url'] = j['href']
                # convert team_id into number
                submissions.append(Submission(team_id, items))

        elif self.fs_location != '':
            # file_list = os.listdir(self.fs_location)
            # Make changes acc to download for file
            # convert submissions array to json array
            submission_file_path = os.path.abspath(self.fs_location)
            # print(submission_file_path)
            if not os.path.isfile(submission_file_path):
                if any(i == 'submission.json' for i in listdir(submission_file_path)) == True:
                    submission_file_path = os.path.join(self.fs_location, 'submission.json')
                    return SubmissionGroup.from_json(submission_file_path)
                else:
                    return self._make_submissions_from_fs()
                # find submission.json inside the given directory
                # else fallback to some easy way to construct submissions from the data stored on filesystem
            else:
                # search through the directory for all folders whose name starts with a number
                return SubmissionGroup.from_json(submission_file_path)
        else:
            print("Neither URL nor File location found.Try again")
            raise CannotMakeSubmissionsFS()
        
        return SubmissionGroup(self.task_name, self.theme_name, submissions)


class Scraper:
    def get_task_name(self):
        """
        Get name of task from web page

        Returns
        -------
        str

        """
        # fetch task name from task url
        # OR
        # use data from portal page
        raise NotImplementedError()

    def scrape_data_from_page(self):
        """
        Scrape data from the page regarding urls of file

        Returns
        -------
        dict
        
        """
        raise NotImplementedError()

class DefaultScraper(Scraper):
    def __init__(self, task_url: str, cookie: str, types: list = ['zip']):
        self.task_url = task_url
        self.cookie = cookie
        self.types = types

    def get_task_name(self):
        # TODO: filter name from URL
        '''
        A method to get name of the task from the URL.        
        '''
        try:
            task_name = re.search('task([a-z A-Z 0-9])+', self.task_url).group()
        except:
            task_name = 'Task'
        return task_name
    
    def get_latest(self, urls: list):
        latest_urls = {}
        for i in range(0, len(urls)):
            if latest_urls.get(urls[i].get_text(), 'False') == 'False':
                latest_urls[urls[i].get_text()] = urls[i]
            else:
                if urls[i]['data-tooltip'] > latest_urls[urls[i].get_text()]['data-tooltip']: 
                    latest_urls[urls[i].get_text()] = urls[i]
        
        t = []
        uu = list(latest_urls.keys())               
        for u in uu:
            t.append(latest_urls[u])
        return t   

    # TODO: Accept team_ids and file urls 
    # also incorporate other data like time of download etc
    def scrape_data_from_page(self):
        '''
        Get the required data from the page.
        '''
        
        # if cookie is expired or invalid, the server makes a redirect
        # we can check if the server redirected and throw an exception
        class NoRedirectHandler(urllib2.HTTPRedirectHandler):
            def http_error_302(self, req, fp, code, msg, headers):
                infourl = addinfourl(fp, headers, req.get_full_url())
                infourl.status = code
                infourl.code = code
                return infourl
            http_error_300 = http_error_302
            http_error_301 = http_error_302
            http_error_303 = http_error_302
            http_error_307 = http_error_302

        opener = urllib2.build_opener(NoRedirectHandler())
        opener.addheaders.append(('Cookie', self.cookie['name'] + '=' + self.cookie['value']))
        # data.task_url = 'http://23.253.205.190/eyrc18/public/admin/grade/task0'
        # data.task_url = 'http://23.253.205.190/eyrc18/public/admin/grade/task1b'

        web_page = opener.open(self.task_url)
        # check if cookie is valid? or the request succeeded
        # 2xx is correct code
        if web_page.getcode() / 100 != 2:
            raise ServerOrScraperException()

        parsed_web_page = BeautifulSoup(web_page, 'html.parser')

        a_list = parsed_web_page.find_all('a', {'class': 'gradeTeam'})
        id_tags = {}
        team_ids = []
        # urls = []
        for a in a_list:
            temp_url = a.parent.parent.find_all('a', {'class': 'waves-effect'})
            temp_url2 = temp_url[:]
            for t in temp_url2:
                if t.get_text() not in self.types:
                    temp_url.remove(t)
                # else:
                #   urls.append(t['href'])
            temp_url_latest = self.get_latest(temp_url)
            team_ids.append(a['data-teamid'])
            id_tags[a['data-teamid']] = temp_url_latest 
        
        task_name = self.get_task_name()
        return team_ids, id_tags
