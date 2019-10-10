import os
import csv
import numpy as np
import pandas as pd

from time import strftime, localtime, time

def getEventLogDateFormat():
    return "%d-%b-%Y %H:%M:%S"

def postToCSVEventLog(file_path,header_list,new_row_list):
    
    #check for csv file existence, store as boolean
    bl_write_header = not (os.path.isfile(file_path))
    
    #open csv file in append mode (creates file if missing)
    with open(file_path,'a',newline='') as csv_file:
        writer = csv.DictWriter(csv_file,fieldnames = header_list,delimiter = ',')
        #write header if required
        if bl_write_header:
            writer.writeheader()
        #append new row
        writer.writerow(dict(zip(header_list,new_row_list)))
        
    
def postToEventLog(event_log_folder_path,event_label,log_file_stub_name,site_name,custom_event_log_header_list,custom_event_log_value_list):

    #get current time
    log_write_time = localtime()
    #set log file name and path
    log_file = log_file_stub_name + '_{}.csv'    
    log_file = os.path.join(event_log_folder_path,log_file.format(strftime("%Y%m", log_write_time)))
    
    date_format = getEventLogDateFormat()
    
    #set csv headers
    csv_headers = ['LogEntryDate','ProcessID','EventLabel','SiteName'] + custom_event_log_header_list
    #set log entry
    log_entry_list = [strftime(date_format, log_write_time),os.getpid(),event_label,site_name] + custom_event_log_value_list
    
    #store log data in CSV
    postToCSVEventLog(log_file,csv_headers,log_entry_list)
    
    #return log message as appended to publish log file    
    return log_entry_list
    
 
def getLatestEventLogEntry_forSiteName(event_log_folder_path,log_file_stub_name,site_name):
    
    ret = []
    
    try:
        #use pandas to open event log CSV

        #get event log file name
        #loop through files in event_log_folder_path starting with log_file_stub_name, get file with max string length
        log_files = [f for f in os.listdir(event_log_folder_path) if os.path.isfile(os.path.join(event_log_folder_path, f)) and f.startswith('{}_'.format(log_file_stub_name)) and f.endswith('.csv')]

        if len(log_files)>0:
        
            csv_log_file = os.path.join(event_log_folder_path,(str(max(log_files))))
            
            df = pd.read_csv(csv_log_file)
        
            df = df[df['SiteName']==site_name]
            max_log_timestamp = df['LogEntryDate'].max()
            df = df[df['LogEntryDate']==max_log_timestamp]
            
            ret = df.values.tolist()[0]
        
    finally:
        return ret