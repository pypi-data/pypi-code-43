#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  1 09:06:06 2018

@author: jonasg
"""
import re
from os import listdir
from os.path import isdir,join
import fnmatch
from pyaerocom import const, logger
from pyaerocom._lowlevel_helpers import BrowseDict
from pyaerocom.exceptions import DataSearchError

class AerocomBrowser(BrowseDict):
    """Interface for browsing all Aerocom data direcories
    
    Note
    ----
    Use :func:`browse` to find directories matching a 
    certain search pattern.
    The class methods :func:`find_matches` and :func:`find_dir` both use 
    :func:`browse`, the only difference is, that the :func:`find_matches` adds
    the search result (a list with strings) to 
    
    """
# =============================================================================
#     def __getitem__(self, name_or_pattern):
#         try:
#             return super(AerocomBrowser, self).__getitem__(name_or_pattern)
#         except KeyError:
#             raise Exception
# =============================================================================
            
    def _browse(self, name_or_pattern, ignorecase=True, return_if_match=True):
        """Search all Aerocom data directories that match input name or pattern
        
        Note
        ----
        Please do not use this function but either 
        Parameters
        ----------
        name_or_pattern : str
            name or pattern of data (can be model or obs data)
        ignorecase : bool
            if True, upper / lower case is ignored
        return_if_match : bool
            if True, then the data directory is returned as string, if it can
            be found, else, only a list is returned that contains all 
            matches. The latter takes longer since the whole database is 
            searched.
            
        Returns
        -------
        :obj:`str` or :obj:`list`
            Data directory (str, if ``return_if_match`` is True) or list 
            containing valid Aerocom names (which can then be used to 
            retrieve the paths)
            
        Raises
        ------
        DataSearchError
            if no match or no unique match can be found
        """
        pattern = fnmatch.translate(name_or_pattern)
        _candidates = []
        _msgs = []
        _warnings = []
        
        for obs_id in const.OBS_IDS:
            if ignorecase:
                match = name_or_pattern.lower() == obs_id.lower()
            else:
                match = name_or_pattern == obs_id
            if match:
                logger.info("Found match for search pattern in obs network "
                            "directories {}".format(obs_id))
                self[obs_id] = const.OBSCONFIG[obs_id]["PATH"]
                if return_if_match:
                    return self[obs_id]
            else:
                if ignorecase:
                    match = bool(re.search(pattern, obs_id, re.IGNORECASE))
                else:
                    match = bool(re.search(pattern, obs_id))
            if match:
                self[obs_id] = const.OBSCONFIG[obs_id]["PATH"]
                _candidates.append(obs_id)
                
        for search_dir in const.MODELDIRS:
            # get the directories
            if isdir(search_dir):
                #subdirs = listdir(search_dir)
                subdirs = [x for x in listdir(search_dir) if 
                           isdir(join(search_dir, x))]
                for subdir in subdirs:
                    if ignorecase:
                        match = bool(re.search(pattern, subdir,re.IGNORECASE))
                    else:
                        match = bool(re.search(pattern, subdir))
                    if match:
                        _dir = join(search_dir, subdir)
                        ok = True 
                        if const.GRID_IO.USE_RENAMED_DIR:
                            logger.info("Checking if renamed directory exists")
                            _dir = join(_dir, "renamed")
                            if not isdir(_dir):
                                ok = False
                                _warnings.append("Renamed folder does not exist "
                                                 "in {}".format(join(search_dir, 
                                                     subdir)))
                        # directory exists and is candidate since it matches 
                        # the pattern
                        if ok:
                            # append name of candidate ...
                            _candidates.append(subdir)
                            # ... and the corresponding data directory
                            self[subdir] = _dir
                            
                            # now check if it is actually an exact match, if 
                            # applicable
                            if return_if_match:
                            
                                if ignorecase:
                                    match = name_or_pattern.lower() == subdir.lower()
                                else:
                                    match = name_or_pattern == subdir
                                if match:
                                    logger.info("Found match for ID {}".format(name_or_pattern))
                                    if return_if_match:
                                        return _dir
                                
                                
                        
            else:
                _msgs.append('directory %s does not exist\n'
                                 %search_dir)
        for msg in _msgs:
            logger.info(msg)
            
        for warning in _warnings:
            logger.warning(warning)
        
        if len(_candidates) == 0:
            raise DataSearchError('No matches could be found for search pattern '
                          '{}'.format(name_or_pattern))
        if return_if_match: 
            if len(_candidates) == 1:
                logger.info("Found exactly one match for search pattern "
                            "{}: {}".format(name_or_pattern, _candidates[0]))
                return self[_candidates[0]]
            raise DataSearchError('Found multiple matches for search pattern {}. '
                          'Please choose from {}'.format(name_or_pattern, 
                                              _candidates))
        return _candidates
        
    def find_data_dir(self, name_or_pattern, ignorecase=True):
        """Find match of input name or pattern in Aerocom database
        
        Parameters
        ----------
        name_or_pattern : str
            name or pattern of data (can be model or obs data)
        ignorecase : bool
            if True, upper / lower case is ignored
            
        Returns
        -------
        str
            data directory of match
            
        Raises
        ------
        DataSearchError
            if no matches or no unique match can be found
        """
        if name_or_pattern in self:
            logger.info('{} found in instance of AerocomBrowser'.format(name_or_pattern))
            return self[name_or_pattern]
        logger.info('Searching database for {}'.format(name_or_pattern))
        return self._browse(name_or_pattern, ignorecase=ignorecase,
                            return_if_match=True) #returns list
        
    def find_matches(self, name_or_pattern, ignorecase=True):
        """Search all Aerocom data directories that match input name or pattern
        
        Parameters
        ----------
        name_or_pattern : str
            name or pattern of data (can be model or obs data)
        ignorecase : bool
            if True, upper / lower case is ignored
            
        Returns
        -------
        list
            list of names that match the pattern (corresponding paths can be
            accessed from this class instance)
            
        Raises
        ------
        DataSearchError
            if no matches can be found
        """
        return self._browse(name_or_pattern, ignorecase=ignorecase,
                            return_if_match=False) #returns list
        
        
if __name__ == "__main__":
    browser = AerocomBrowser()
    dd = browser.find_data_dir('TM5_AP3-CTRL2016*')
    ea = browser.find_data_dir('Earli*')
    ea1 = browser.find_matches('Earlinet')
    
    print(ea)
    print(ea1)
# =============================================================================
#     try:
#         data_dir = browser.find_data_dir('*Cam5.3-Oslo*')
#     except DataSearchError as e:
#         print(repr(e))
#     
#     
#     
#     matches = browser.find_matches('*Cam5.3-Oslo*')
#     
#     for match in matches:
#         print('{}: {}'.format(match, browser[match]))
#         
#     data_dir_earlinet = browser.find_data_dir('EARLIN*')
#     
#     data_dir_earlinet = browser.find_data_dir('EARLIN*')
#     
#     browser.find_data_dir('Earlinet')
#     
#     
#     
#         
# =============================================================================
