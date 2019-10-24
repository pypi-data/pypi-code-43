# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 20:51:29 2019

@author: Praneeth Ponnekanti - praneeth.ponnekanti@gmail.com 

Use cases : 
    To create logfiles and write to multiple log files from the same script.
    

    Create an object of the CreateLogs class in your script with the required arguments, use "object.logger.logging_level" as a wrapper around the process for which you wish to capture the logs.
    

    Arguments : 
        log_dest_dir = Path to the directory where the log file is to be saved. 
        log_file_name = Name of the log file. [The log file can be accessed at log_dest_dir/log_file_name]
        log_format = Can be defined while intiallizing the class object, however the default argument is '%(asctime)s %(name)-12s%(levelname)s:%(message)s'
        log_set_level = User - defined set levels. Default value = 'DEBUG'. For all other valid inputs, please refer "https://stackoverflow.com/questions/2031163/when-to-use-the-different-log-levels"
        

        
"""
import logging
#import pathlib

#logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
#logging.root.setLevel(logging.INFO)


class CreateLogs : 
    #def __init__(self,*argv) :
    #def __init__(self, log_dest_dir, log_file_name, log_set_level) :
    def __init__(self, log_dest_dir, log_file_name, log_format = '%(asctime)s %(name)-12s%(levelname)s:%(message)s', log_set_level = 'DEBUG') :
        self.log_dest_dir = log_dest_dir
        #self.log_dest_dir = pathlib.Path
        self.log_file_name = log_file_name
        self.log_format = log_format
        #self.log_set_level = log_set_level
        self.logger = logging.getLogger(log_dest_dir + log_file_name)
        print ("Dataype of log_set_level variable : " )
        print (type(log_set_level))
        _loglevel = logging.getLevelName(log_set_level)
        self.logger.setLevel(_loglevel)
        print ("Logger level set to : " + log_set_level)
        #self.logger.setLevel(self.log_set_level)
        self.formatter = logging.Formatter(self.log_format)          
        self.f_handler = logging.FileHandler(self.log_dest_dir + "/" + self.log_file_name, mode = 'w')
        self.f_handler.setFormatter(self.formatter)
        #f_handler = logging.FileHandler(self.log_source_dir + "/" + self.log_file_name, mode = 'a')
        self.logger.addHandler(self.f_handler)
        #self.logger = logging.getLogger(__name__ + ": ")
        #self.execute_something()
    
    '''
    def create_logs(self):
        try :
            self.logger.info("You have opened the log file that you just created!")
        except :
            self.logger.info("Oops, you just entered an exception block!")
            '''
        