#This module documentation follows the conventions set out in http://pythonhosted.org/an_example_pypi_project/sphinx.html
#and is built into the automatic documentation
'''

/****************************************************************************/
/* Metapraxis Limited                                                       */
/*                                                                          */
/* Copyright (©) Metapraxis Ltd, 1991 - 2017, all rights reserved.          */
/****************************************************************************/
/* NOTICE:  All information contained herein is, and remains the property   */
/* of Metapraxis Limited and its suppliers, if any.                         */
/* The intellectual and technical concepts contained herein are proprietary */
/* to Metapraxis Limited and its suppliers and may be covered by UK and     */
/* Foreign Patents, patents in process, and are protected by trade secret   */
/* or copyright law.  Dissemination of this information or reproduction of  */
/* this material is strictly forbidden unless prior written permission is   */
/* obtained from Metapraxis Limited.                                        */
/*                                                                          */
/* This file is subject to the terms and conditions defined in              */
/* file "license.txt", which is part of this source code package.           */
/****************************************************************************/                              

'''
# ------------------------------------
# import libraries
import os
import sys
import subprocess
import csv
import datetime
from time import time, localtime, strftime

from empower_utils import process_utilities as prcu

# ------------------------------------
# set constants
lock_file_name_mask = 'lock-P{:0>6}.txt'

# ------------------------------------
#   function to check if Empower site is in use
def checkEmpowerSiteActive(site_log_path,active_timeout_seconds):
    
    live_site_timestamp_format = '%Y-%m-%d %H:%M:%S'
    
    # get latest trigger file from local inbox location (Prod inbox)
    text_files = [f for f in os.listdir(site_log_path) if f.endswith('.csv')]
    
    # get latest from list in local inbox location
    if len(text_files)>0:
        
        latest_live_log_file = (str(max(text_files)))
    
        # get latest modified time stamp from latest log file
        latest_live_log_modified_ts = os.path.getmtime(os.path.join(site_log_path,latest_live_log_file))

        current_time = time()
        latest_live_log_modified = latest_live_log_modified_ts
        seconds_since_active = current_time - latest_live_log_modified
        
        latest_live_log_modified_str = strftime(live_site_timestamp_format,localtime(latest_live_log_modified))
        current_time_str = strftime(live_site_timestamp_format,localtime(current_time))

        empower_site_active = seconds_since_active < active_timeout_seconds
        earliest_idle_time = datetime.datetime.strptime(latest_live_log_modified_str,live_site_timestamp_format) + datetime.timedelta(0,active_timeout_seconds)
        earliest_idle_time_str = earliest_idle_time.strftime(live_site_timestamp_format)
        
    else:
        empower_site_active,latest_live_log_modified_str,seconds_since_active = (False,'No site',0,'No site')
    
    return empower_site_active,latest_live_log_modified_str,seconds_since_active,earliest_idle_time_str

# ------------------------------------
#   function to create lock file name from PID
def getSiteLockFileName(pid):
    return lock_file_name_mask.format(pid)

# ------------------------------------
#   function to extract PID from lock file name
def getPIDFromSiteLockFileName(site_lock_file):
    return site_lock_file.replace('.txt','')[-6:].lstrip('0')

# ------------------------------------
#   function to release lock of Empower site
def releaseSiteLock(lock_dir,process_id=os.getpid()):
    
    #set lock file name
    lock_file_full_path = os.path.join(lock_dir,getSiteLockFileName(process_id))
    
    #check for lock file from current process
    if os.path.exists(lock_file_full_path):
        
        #delete lock file
        os.remove(lock_file_full_path)
        
        #return success
        return True,'Lock file deleted: {}'.format(lock_file_full_path)
        
    else:
    
        #return failure
        return False,'Lock file retained at: {}'.format(lock_file_full_path)
        
# ------------------------------------
#   function to test and recover lock status of Empower site
def checkForSiteLock(lock_dir):
    
    lock_list = os.listdir(lock_dir)
    
    #if lock directory is empty (1 file permitted per lock directory)
    if not lock_list:
        
        #return success
        return False, 'No lock file found'
    
    #get process ID from lock file
    process_id = getPIDFromSiteLockFileName(lock_list[0])

    #check to see if locking process is an active Python instance
    #   this should also detect the current process, and flag it correctly as an active python process
    bl_active_python_process = prcu.checkForActivePIDForImage(process_id,'python.exe')
    
    #if lock file exists, and process_id is not an active Python process
    if not bl_active_python_process:
        
        #force release
        releaseSiteLock(lock_dir,process_id)
        
        #return success
        return False, 'Expired lock file removed: {}'.format(lock_list[0])
    
    else:
        
        #return failure
        return True, 'Live lock file found: {}, PID {}'.format(lock_list[0],process_id)

# ------------------------------------
#   function to create lock file for Empower site 
def getSiteLock(lock_dir,process_id = os.getpid()):
    
    bl_site_locked, lock_check_message = checkForSiteLock(lock_dir)
    
    #if lock directory is empty (1 file permitted per lock directory)
    if not bl_site_locked:
        
        #set lock file name
        #current_process_id = os.getpid()
        lock_file_full_path = os.path.join(lock_dir,getSiteLockFileName(process_id))

        #create lock file
        with open(lock_file_full_path,'w') as f:
            f.write('{} locked by process {:0>6}'.format(lock_dir,process_id))
        
        #return success
        return True,'{}; lock file created at {}'.format(lock_check_message,lock_file_full_path)
 
    else:

        #return failure
        return False, lock_check_message

if __name__ == "__main__":
    
    # ------------------------------------
    #   test routines for Empower site locking
    
    test_lock_dir = r'C:\Empower Sites\_lock\Sales-Analysis'
    
    print('Checking for lock...')
    blLocked, msg = checkForSiteLock(test_lock_dir)
    print ('Locked: {}, {}'.format(blLocked,msg))

    print('Locking (dummy)...')
    blLocked, msg = getSiteLock(test_lock_dir,1000)
    print ('Lock success: {}, {}'.format(blLocked,msg))
        
    print('Checking for lock....')
    blLocked, msg = checkForSiteLock(test_lock_dir)
    print ('Locked: {}, {}'.format(blLocked,msg))
    
    print('Locking...')
    blLocked, msg = getSiteLock(test_lock_dir)
    print ('Lock success: {}, {}'.format(blLocked,msg))

    print('Checking for lock....')
    blLocked, msg = checkForSiteLock(test_lock_dir)
    print ('Locked: {}, {}'.format(blLocked,msg))

    print('Releasing...')
    blLocked, msg = releaseSiteLock(test_lock_dir)
    print ('Release success: {}, {}'.format(blLocked,msg))

    print('Checking for lock....')
    blLocked, msg = checkForSiteLock(test_lock_dir)
    print ('Locked: {}, {}'.format(blLocked,msg))
