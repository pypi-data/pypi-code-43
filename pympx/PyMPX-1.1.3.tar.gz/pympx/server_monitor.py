r'''
The Server Monitor pings web instances checks logs and schedules AD and Publication checks
it also collects statistics.

The architecture is divided into multiple processes, that communicate by sending each other messages.

Event Generators generate messages:
- they schedule AD and Publication requests
- they parse logs
- they monitor general server health, and empower web server health

The Consolidator consolidates the state information from all of these message generators to form an overall picture of what state the server is in.
it creates new messages for the Notifier and the Server Manipulator to act on

The Notifier decides whether messages should be sent out to real people, whom to send them to and how to send them. It asks the Emailer to email messages that need sending.

The Server Manipulator controls publication of the site and starting and stopping of IIS.

#As of 2017-12-12 only the log parsers and Emailers are doing real work. The Server Manipulator is not yet turning IIS on and off.

example config.yml file:

%YAML 1.1
---
smtp server : cluster8out.eu.messagelabs.com
email mode  : powershell
iis root : 'C:\inetpub\wwwroot' #The root from which iis is serving Empower web sites

empower sites : 
    Sales-Analysis :
        #Part of the iis directory for the site "${iis root}\${iis subdirectory}\Logs" should hold the Empower Server logs
        iis subdirectory : Sales-Analysis 
        #We could get this by parsing the webconfig - it is the location of the .eks or .beks file being served
        #For now just write it in
        site file        : 'C:\Users\jonathan.treloar\Desktop\Sunrise Brands Limited v1.0 - EF\consuma.eks'
        iis logs         : 'C:\inetpub\logs\LogFiles\W3SVC1'
        #The schedules use the international iCalendar standard - not something I made up or some pythonista made up, so there are plenty of resources on t'internet
        #Work out simple rule strings with this handy tool:https://www.textmagic.com/free-tools/rrule-generator
        #More complex examples at http://recurrance.sourceforge.net/
        #Also see https://dateutil.readthedocs.io/en/stable/examples.html#rrulestr-examples
        #Also see https://en.wikipedia.org/wiki/ICalendar for background on iCalendar
        #Note that specifying multiple rules will create a rule set - which can get as complicated as you need
        #The rule in the example runs every day at 1'o'clock in the morning
        ad sync schedule : | 
                            DTSTART:20100101T010000
                            RRULE:FREQ=DAILY;INTERVAL=1
        #The publish rule checks for sites to publish, it doesn't publish if there are no sites
        #This ruleset runs every hour at half past the hour, but not between 9 a.m. and 8 p.m.
        publish schedule : RRULE:FREQ=DAILY;INTERVAL=1;BYHOUR=0,1,2,3,4,5,6,7,8,20,21,22,23;BYMINUTE=30
        #How many seconds a site must be idle before publishing it
        publish idle seconds : 600

'''

import argparse
from fnmatch import fnmatch
import os
import time
import csv
import datetime
from   dateutil import relativedelta, rrule
import sched
import json
import yaml
#We need pkg_resources to find the Powershell scripts we've included with the package
import pkg_resources
import subprocess
import multiprocessing
CTX=multiprocessing.get_context()

from empower_utils import logconfig
log=logconfig.get_logger()
CompletelyLoggedError=logconfig.CompletelyLoggedError

#class User():
#    def __init__(self):
#        pass

class ServerMonitor():
    def __init__(self,server_monitor_root_directory,config_file_path=None):
    
        self.server_monitor_root_directory = server_monitor_root_directory
        
        if config_file_path is None:
            config_file_path = os.path.join(self.server_monitor_root_directory,'config.yml')
            
        self.config_dict         = {}
        with open(config_file_path,'r') as config_file:
            self.config_dict = yaml.load(config_file)

        
        
        
    def run_report(self):
                
        report_event=Event()
        report_event._datetime=datetime.datetime.now()
        report_event._type='REPORT'
        
        self.consolidator_queue.put(report_event)
        
    def run(self):
        
        self.logging_queue       = multiprocessing.Queue()
        self.consolidator_queue  = multiprocessing.Queue()
        self.notifier_queue      = multiprocessing.Queue()
        self.manipulator_queue   = multiprocessing.Queue()
        self.email_queue         = multiprocessing.Queue()
        
        #iis root : "C:\inetpub\wwwroot" #The root from which iis is serving Empower web sites
        #iis logs : "C:\inetpub\logs\LogFiles" #location of W3SVC1, W3SVC2 and so on
        #empower sites : 
        #    Sales-Analysis :
        #        #Part of the iis directory for the site "${iis root}\${iis subdirectory}\Logs" should hold the Empower Server logs
        #        iis subdirectory : Sales-Analysis 
        #        #We could get this by parsing the webconfig - it is the location of the .eks or .beks file being served
        #        site file        : "C:\Users\jonathan.treloar\Desktop\Sunrise Brands Limited v1.0 - EF\consuma.eks"
        #    

        smtp_server         = self.config_dict['smtp server']
        email_mode          = self.config_dict['email mode']
        iis_root_dir        = self.config_dict['iis root']
                              
        empower_sites_dict  = self.config_dict['empower sites']
        
        self.empower_log_parsers = []
        self.server_log_parsers  = []
        self.iis_log_parsers     = []
        self.site_schedulers     = []

        
        for site_name, site_dict in empower_sites_dict.items():
            
            log.info('Creating log parsers for site: '+str(site_name))
            
            completed_work_directory=os.path.join(self.server_monitor_root_directory,'completed_work',site_name)
            try:
                os.mkdir(os.path.join(self.server_monitor_root_directory,'completed_work'))
            except FileExistsError:
                pass
            try:
                os.mkdir(completed_work_directory)
            except FileExistsError:
                pass
                
            empower_site_file = site_dict['site file']
            p = EmpowerLogParser(root_directory=os.path.join(os.path.dirname(empower_site_file),'Log Files'),completed_work_directory=os.path.join(completed_work_directory,'empower_logs'))
            empower_log_parser=multiprocessing.Process(target=p.run
                                           ,kwargs={'target_queue': self.consolidator_queue
                                                   ,'logging_queue': self.logging_queue
                                                   }                                                
                                           ,name='Parse Empower Logs')
            self.empower_log_parsers.append(empower_log_parser)
            
            iis_subdirectory             = site_dict['iis subdirectory']
            if iis_subdirectory is not None:
                server_log_root_directory    = os.path.join(iis_root_dir, iis_subdirectory, "Logs")
            else:
                server_log_root_directory    = os.path.join(iis_root_dir, "Logs")
           
            p = EmpowerServerLogParser(root_directory=server_log_root_directory,completed_work_directory=os.path.join(completed_work_directory,'empower_server_logs'),server_name=site_name)
            server_log_parser=multiprocessing.Process(target=p.run
                                           ,kwargs={'target_queue': self.consolidator_queue
                                                   ,'logging_queue': self.logging_queue
                                                   }                                                
                                           ,name='Parse Empower Server Logs')
            self.server_log_parsers.append(server_log_parser)

            iis_log_root_directory    = site_dict['iis logs']
            p = IISLogParser(root_directory=iis_log_root_directory,completed_work_directory=os.path.join(completed_work_directory,'iis_logs'))
            iis_log_parser=multiprocessing.Process(target=p.run
                                           ,kwargs={'target_queue': self.consolidator_queue
                                                   ,'logging_queue': self.logging_queue
                                                   }                                                
                                           ,name='Parse IIS Logs')
            self.iis_log_parsers.append(iis_log_parser)
            
            try:
                ad_rrule_string = site_dict['ad sync schedule']
            except KeyError:
                ad_rrule_string = None
                
            if ad_rrule_string is not None:
                
                uss = SiteScheduler(site=site_name, rrulestr=ad_rrule_string , event_type='AD_SYNC')
                user_synchronisation_scheduler=multiprocessing.Process(target=uss.run
                                               ,kwargs={'consolidator_queue': self.consolidator_queue
                                                       ,'logging_queue': self.logging_queue
                                                       }                                                
                                               ,name='Schedule User Sync')
                self.site_schedulers.append(user_synchronisation_scheduler)
            
            
            try:
                publish_rrule_string = site_dict['publish schedule']
            except KeyError:
                publish_rrule_string = None
                
            if publish_rrule_string is not None:
                
                ps  = SiteScheduler(site=site_name, rrulestr=publish_rrule_string, event_type='PUBLISH_REQUEST')
                publication_scheduler=multiprocessing.Process(target=ps.run
                                               ,kwargs={'consolidator_queue': self.consolidator_queue
                                                       ,'logging_queue': self.logging_queue
                                                       }                                                
                                               ,name='Schedule Publication')
                self.site_schedulers.append(publication_scheduler)
            
        
        saved_notifications_directory = os.path.join(self.server_monitor_root_directory, 'saved_notifications')
        notification_rule_directory   = os.path.join(self.server_monitor_root_directory, 'notification_rules' )
        notifiee_details_directory    = os.path.join(self.server_monitor_root_directory, 'notifiee_details'   )
        
        
        #TODO - put a python schedule object in here - and get it neatly serialised
        #TODO - put a python schedule object in here - and get it neatly serialised
        
        ec = EventConsolidator()
        sm = ServerManipulator()
        em = Emailer(smtp_server=smtp_server, mode=email_mode)
        nt = Notifier(saved_notifications_directory = saved_notifications_directory
                     ,notification_rule_directory   = notification_rule_directory
                     ,notifiee_details_directory    = notifiee_details_directory
                     )
                    
        self.emailer=multiprocessing.Process(target=em.run
                                       ,kwargs={'email_queue'   : self.email_queue
                                               }                                                
                                       ,name='Send Email')
        
        self.server_manipulator=multiprocessing.Process(target=sm.run
                                       ,kwargs={'source_queue': self.manipulator_queue
                                               ,'consolidator_queue': self.consolidator_queue
                                               ,'logging_queue': self.logging_queue
                                               }                                                
                                       ,name='Manipulate Server')

        
        self.event_consolidator=multiprocessing.Process(target=ec.run
                                       ,kwargs={'source_queue': self.consolidator_queue
                                               ,'notifier_queue': self.notifier_queue
                                               ,'logging_queue': self.logging_queue
                                               }                                                
                                       ,name='Handle Events')

        self.notifier=multiprocessing.Process(target=nt.run
                                       ,kwargs={'source_queue'  : self.notifier_queue
                                               ,'logging_queue' : self.logging_queue
                                               ,'email_queue'   : self.email_queue
                                               }                                                
                                       ,name='Notifier')
                                       
                                       
        #Start the parsers and the event consolidator
        
        self.emailer.start()
        self.server_manipulator.start()
        self.notifier.start()
        self.event_consolidator.start()  
        
        for scheduler in self.site_schedulers:
            scheduler.start()
        
        for empower_log_parser in self.empower_log_parsers:
            empower_log_parser.start()
        for server_log_parser  in self.server_log_parsers:
            server_log_parser.start()  
        #The iis log parsers are CPU hungry
        #for iis_log_parser     in self.iis_log_parsers:
        #    iis_log_parser.start()
        


    def terminate(self):        
        for scheduler in self.site_schedulers:
            scheduler.terminate()
        
        for empower_log_parser in self.empower_log_parsers:
            empower_log_parser.terminate()
            
        for server_log_parser  in self.server_log_parsers:
            server_log_parser.terminate()  
        
        #for iis_log_parser     in self.iis_log_parsers:
        #    iis_log_parser.terminate()
      
        self.event_consolidator.terminate()
        self.notifier.terminate()
        self.emailer.terminate()
    
#Object Model        
        
class Event():
    def __init__(self):
        self._server=None
        self._datetime=None
        self._user=None
        self._site=None
        self._panel=None
        self._duration=None
        self._subevents=None
        self._thread=None
        self._http_response=None
        self._type=None
    
    @property
    def head_type(self):
        return self._type.split('/')[0]
    
    def copy(self):
        copy = Event()
        copy._server = self._server
        copy._datetime = self._datetime
        copy._user = self._user
        copy._site = self._site
        copy._panel = self._panel
        copy._duration = self._duration
        copy._subevents = self._subevents
        copy._thread = self._thread
        copy._http_response = self._http_response
        copy._type = self._type
        return copy
    
    def __str__(self):
        return str(self.__dict__)


class NotificationRequest():

    def __init__(self,target,subject,message,type,subevents):
        self.target=target
        self.subject=subject
        self.message=message
        self.type=type
        self.subevents=subevents
        
    @property
    def head_type(self):
        return self.type.split('/')[0]
        
    def __str__(self):
        return str(self.type)+' : '+str(self.subject)
        
    def to_json_dct(self):
        return {'type': self.type,'target': self.target,'subject': self.subject,'message': self.message}
    
    #Static method
    def from_json_dct(dct):
        return NotificationRequest(target=dct['target'],subject=dct['subject'],message=dct['message'],type=dct['type'],subevents=[])

class EmpowerPanel():
    def __init__(self,empower_web_instance,name):
        self.name = name
        self.empower_web_instance = empower_web_instance

class EmpowerPanelHourlyStats():
    def __init__(self,empower_panel,datehour):
        self.empower_panel     = empower_panel
        self.datehour = datehour
        
        #Stats is just a dictionary, so taht we can easily add to it
        self.stats = {'hits'    :0,
                      'duration':0
                     }
        
class EmpowerWebHourlyStats():
    def __init__(self,empower_web_instance,datehour):
        self.empower_web_instance = empower_web_instance
        self.datehour = datehour
        
        self.stats={'GETS':0
                   ,'POSTS':0
                   ,'GET duration':0
                   ,'POST duration':0
                   ,'MAX users':0
                   ,'MIN users':0
                   }
        
class EmpowerUserHourlyStats():
    def __init__(self,empower_user,datehour):
        self.empower_user = empower_user
        self.datehour = datehour
        
        self.stats={'actions' :0,
                    'duration':0
                   }
    
class EmpowerSite():
    def __init__(self,name):
        self.version=None
        self.name=name
        self.users={}
        self.panels={}
        
        #The key to hourly stats is a datetime at hour granularity
        self.hourly_stats={}
        
        #Find out where the site is living, based on the webconfig
        self.site=None
    
    def consolidate_event(self,event):
        pass
        
class EmpowerWebInstance():
    def __init__(self,name):
        self.version=None
        self.name=name
                
        #The key to hourly stats is a datetime at hour granularity
        self.hourly_stats={}
        
        #Find out where the sites are living, based on the webconfig
        self.sites={}

    def consolidate_event(self,event):
        
        #figure out state
        
        #update stats
        head_event_type=event.head_type.split('/')[0]
        
        dd=event._datetime
        datehour=datetime.datetime(dd.year,dd.month,dd.day,dd.hour)
        try:
            hourly_stat=self.hourly_stats[datehour]
        except KeyError:
            hourly_stat=EmpowerWebHourlyStats(empower_web_instance=self,datehour=datehour)
            self.hourly_stats[datehour]=hourly_stat
        
        if head_event_type=='GET':
            hourly_stat.stats['GETS']+=1
            if event._duration:
                hourly_stat.stats['GET duration'] +=event._duration
                
        if head_event_type=='POST':
            hourly_stat.stats['POSTS']+=1
            if event._duration:
                hourly_stat.stats['POST duration']+=event._duration
            
        
        #Return new events to create off the back of this one
        return []
    
    def report(self):
        #TODO - write these down to the reporting directory
        print('Webinstance Report: '+self.name+' ------------------------')
        for s in self.hourly_stats.values():
            for k,v in s.stats.items():
                print(s.datehour, k, v)
        
        #TODO - remove old stats once they have been reported
        
class EmpowerUser():
    def __init__(self,name):
        self.name = name
        self.state=None
        self.last_logged_in=None
        self.last_logged_out=None
        
        #The key to hourly stats is a datetime at hour granularity
        self.hourly_stats={}
    
    def consolidate_event(self,event):
        
        return_events=[]
        
        #figure out state
        
        if event._type=='ERROR/userSiteCacheLogoff' and event._datetime :
            #TODO store message body and subject in a separate store
            subject = 'User Site Cache Logoff Error for {}'.format(str(event._server))
            message = 'User {} has had a Site Cache Logoff error. Please fix.'.format(event._user)
            
            nr=NotificationRequest(subject=subject
                                  ,message=message
                                  ,target='site_support'
                                  ,type='ERROR/userSiteCacheLogoff',subevents=[self])
            
            return_events.append(nr)
            
        #update stats
        
        #Return new events to create off the back of this one
        return return_events
        
###################################################################

# Event Generators

###################################################################
        
class LogParser():
    def __init__(self,root_directory,completed_work_directory):
        '''
        :param root_directory: where to look for work to do
        :param completed_work_directory: where to put empty files signifying the work we've done
        '''
        self._events = []
        self._states = []
        #must be passed in a way to find new files
        
        self._current_file_name   = None
        self._current_file        = None
        self._current_position    = 0
        self._current_chunk       = None
        
        self.root_directory       = root_directory
        self.completed_work_directory = completed_work_directory
        self._log_file_fn         = None

        try:
            os.mkdir(completed_work_directory)
        except FileExistsError:
            pass
    
        self.processed_file_names = []
        for f in os.listdir(completed_work_directory):
            log.info('Will skip file as it has been processed before :'+os.path.join(completed_work_directory,f))
            self.processed_file_names.append(f)
        
    def parse_next(self):
        self._previous_file_name= self._current_file_name
        self._previous_position = self._current_position
        
        self.check_for_new_files()
        
        chunk = self.get_next_chunk()
        if chunk is None or not self.parse_chunk(chunk=chunk):
            if datetime.datetime.now().second % 5 == 0:
                print('-')
            else:    
                print('.')
            time.sleep(1)
        
        
        return True
        
    def get_next_chunk(self):
        if self._current_file:
            return self._current_file.readline()
        else:
            return None
           
            
    def check_for_new_files(self):
        '''Check if a new log file has been added to the directory - if it has then we will switch current logfile.
        The calling code will finish processing the previous log file before moving on to the current log file'''
        for f in os.listdir(self.root_directory):
            if fnmatch(f,self._log_file_fn):
                #
                if  self._current_file_name is None or (f >= self._current_file_name and f not in self.processed_file_names):
                    #Finish parsing the current file before starting a new one
                    if self._current_file is not None:
                        try:
                            for line in self._current_file:
                                self.parse_chunk(chunk=line)
                        except Exception:
                            log.warning('Error reading file '+self._current_file_name)
                        finally:        
                            self._current_file.close()
                        #Record completed work as an empty file with the same name
                        with open(os.path.join(self.completed_work_directory, self._current_file_name),'w') as completed_file:
                            #Opening and closing the file is all we want to do
                            pass
                            
                    
                    self._current_file_name = f
                    self.processed_file_names.append(f)
                    
                    self._current_file=open(os.path.join(self.root_directory,f),'r')
                    log.info('LogParser current file set to "'+self._current_file_name+'"')
                    break
        
    def parse_chunk(self,chunk):
        #This function must be overridden
        assert False
        pass

    def run(self,target_queue=None,logging_queue=None):
        self._target_queue=target_queue
        self._logging_queue=logging_queue 
        while self.parse_next():
            pass   
            
class EmpowerServerLogParser(LogParser):

    def __init__(self,server_name,root_directory,completed_work_directory):
        log.info('Initialising EmpowerServerLogParser for log directory "'+root_directory+'"' )
        super(EmpowerServerLogParser, self).__init__(root_directory=root_directory,completed_work_directory=completed_work_directory)
        #fnmatch string for a log file
        self._log_file_fn='EmpowerServerLog*.csv'
        #It's easier to get the server name when setting up the log parser, since it is in the initial directory, not in the logs
        if server_name is None:
            self.server_name='default'
        else:
            self.server_name=server_name
            
        
    #don't need to override check_for_new_files
    
    def parse_chunk(self,chunk):
        '''Return True if parsed a chunk, False if there was nothing to parse'''
        if chunk is None or len(chunk)==0:
            return False
        else:
            #2017-12-04 11:36:52.1,ERROR,317,,[userSiteCache] RegisterLogoff() Error for user: 'Joe Bloggs'| error: Thread was being aborted.
            lines=chunk.split('\n')
            reader = csv.reader(lines[:-1])
            
            #The reader will produce lists
            for l in reader:
                if l != []:
                    e=None
                    try:
                        #Create an object and put it on the target queue
                        if l[1]=='ERROR':
                            square_brackets, rest_of_line = EmpowerServerLogParser.split_square_brackets_section(l[4])
                            if square_brackets=='[userSiteCache]' and rest_of_line[1:17]=='RegisterLogoff()':
                                #User is the bit between the single quotes
                                e = Event()
                                e._server=self.server_name
                                e._datetime=datetime.datetime.strptime(l[0],'%Y-%m-%d %H:%M:%S.%f')
                                #print(e._datetime)
                                e._user=rest_of_line.split("'")[1]
                                #print(e._user)
                                e._site=None
                                e._panel=None
                                e._duration=None
                                e._subevents=None
                                e._type='ERROR/userSiteCacheLogoff'
                                
                        else:
                            pass
                    except IndexError:
                        log.warning('IndexError raised when reading list '+str(l))
                
                    if e is not None:# and self._target_queue is not None:
                        self._target_queue.put(e)
                        #print(e)
                        pass
                
            return True

    def split_square_brackets_section(string):
        '''Get the [] bit off the front of the string, and return it, and the rest of the bits in a tuple of two strings'''
        l = string.split(']')
        return l[0]+']', ']'.join(l[1:])

class EmpowerLogParser(LogParser):

    def __init__(self,root_directory,completed_work_directory):
        log.info('Initialising EmpowerLogParser for log directory "'+root_directory+'"' )
        super(EmpowerLogParser, self).__init__(root_directory=root_directory,completed_work_directory=completed_work_directory)
        #fnmatch string for a log file
        self._log_file_fn='empower*.log'
        self._current_event = None
        #keep track of the latest site we parsed
        self._latest_site=None
        
    #don't need to override check_for_new_files
    
    def parse_chunk(self,chunk):
        '''Return True if parsed a chunk, False if there was nothing to parse'''
        if chunk is None or len(chunk)==0:
            return False
        else:
            lines=chunk.split('\n')
        
            for line in lines[:-1]:
                #self._current_event
                if len(line)==0:
                    #We have hit a newline - that means the previous event is finished    
                    if self._current_event is not None:
                        self._target_queue.put(self._current_event)
                        self._current_event=None
                        
                elif line[:2]=='>>':
                    
                    #use a csv reader to parse the line, since it contains quoted characters
                    reader = csv.reader([line[2:]],delimiter='-', quotechar='"',skipinitialspace=True)
                    
                    self._current_event=Event()
                    self._current_event._duration=0
                    #The reader will produce lists
                    for l in reader:
                        ##User is the bit between the single quotes
                        #e._server=None
                        self._current_event._datetime=datetime.datetime.strptime('-'.join(l[0:3]).strip(),'%Y-%m-%d %H:%M:%S')
                        self._current_event._user=l[3].strip()
                        ##print(e._user)
                        #e._panel=None
                        #e._duration=None
                        #e._subevents=None
                        if l[4].strip()=='Viewed dashboard panel':
                            self._current_event._type='VIEW/viewed_dashboard_panel'
                            self._current_event._panel=l[6].strip()
                        
                        try:
                            self._current_event._site=l[5].strip()
                            self._latest_site=self._current_event._site
                        except IndexError:
                            self._current_event._site=self._latest_site
                        
                elif line[:2]=='\t\t':
                    #use a csv reader to parse the line, since it contains quoted characters
                    reader = csv.reader([line[2:]],delimiter='-', quotechar='"',skipinitialspace=True)
                    for l in reader:
                        if self._current_event is not None: # and l[0].strip()=='RefreshFocus':
                            try:
                                self._current_event._duration+=int(l[2].split(':')[1].strip().split(' ')[0])
                            except IndexError:
                                pass
                        
                #>> 2016-09-01 09:01:25 - "Harry Spencer" - Viewed dashboard panel - ConsumaBrand 2016 v7 - Home Page (1/81).
                #        SelectImage - Panel load - duration: 213 ms
                #        RefreshFocus - Refreshing instrument data - duration: 32 ms
                #        get_json_text - Building JSON structure - duration: 3 ms
                #        get_json_text - Writing JSON text - duration: 5 ms
                #        draw_panel - Updating browser - duration: 212 ms
                #        get_json_text - Building JSON structure - duration: 1 ms
                #        get_json_text - Writing JSON text - duration: 4 ms
                #        draw_panel - Updating browser - duration: 142 ms
                #        process_json - Building JSON structure - duration: 0 ms
                #        process_json - Writing JSON text - duration: 0 ms
                            
            return True

class IISLogParser(LogParser):

    def __init__(self,root_directory,completed_work_directory):
        log.info('Initialising IISLogParser for log directory "'+root_directory+'"' )
        super(IISLogParser, self).__init__(root_directory=root_directory,completed_work_directory=completed_work_directory)
        #fnmatch string for a log file
        self._log_file_fn='u_ex*.log'
        
    #don't need to override check_for_new_files
    
    def parse_chunk(self,chunk):
        '''Return True if parsed a chunk, False if there was nothing to parse'''
        if chunk is None or len(chunk)==0:
            return False
        else:
            #2017-12-04 11:29:52 127.0.0.1 GET /empweb93 - 443 - 127.0.0.1 python-requests/2.18.4 - 200 0 0 6
            #2017-12-04 11:30:26 172.31.24.138 GET /empweb93/ - 443 - 35.176.210.12 Mozilla/5.0+(compatible;+MSIE+9.0;+Windows+NT+6.1;+Trident/5.0) - 302 0 0 226
            #2017-12-04 11:35:39 172.31.24.138 POST /empweb93/services/dashboard/setpanelaction - 443 Test117 35.176.210.12 Mozilla/5.0+(compatible;+MSIE+9.0;+Windows+NT+6.1;+Trident/5.0) - 200 0 0 8

            lines=chunk.split('\n')
            reader = csv.reader(lines[:-1],delimiter = ' ')
            
            #The reader will produce lists
            for l in reader:
                e=None
                try:
                    #Create an object and put it on the target queue
                    if l[0][0]!='#' and l[3] not in ['HEAD','OPTIONS']:
                        try:
                            #    #User is the bit between the single quotes
                            e = Event()
                            try:
                                resource_list = l[4].split('/')
                                if len(resource_list) >= 2 and resource_list[-1]=='setpanelaction':
                                    e._server=resource_list[1]
                                    
                            except IndexError:
                                log.warning('IndexError raised when reading server from '+str(l[4].split('/')))
                    
                            e._datetime=datetime.datetime.strptime(l[0]+' '+l[1],'%Y-%m-%d %H:%M:%S')
                            user = l[7]
                            if user != '-':
                                e._user=user

                            e._http_response=int(l[11])
                            
                            #    #print(e._user)
                            #e._site=l[4].split('/')[1]
                            #    e._panel=None
                            e._duration=int(l[-1])
                            #    e._subevents=None
                            if l[3]=='POST':
                                e._type='POST'
                            elif l[3]=='GET':
                                if l[9][:6]=='python':
                                    e._type='TESTING/warm_empower'
                                else:
                                    e._type='GET'
                            else:
                                e=None
                        except IndexError:
                            log.warning('IndexError raised when reading list '+str(l))        
                    else:
                        pass
                except IndexError:
                    log.warning('IndexError raised when reading l[0][0] of list '+str(l))
            
                if e is not None:# and self._target_queue is not None:
                    self._target_queue.put(e)
                    #print(e)
                    pass
                
            return True

class EmpowerWebPinger():
    '''The pinger tries to get a reply from Empower Web by calling ~/services/dashboard/active. it can be run locally or from afar'''
    def __init__(self,seconds_between_pings=30,instances_to_ping=[]):
        self.seconds_between_pings=seconds_between_pings
        self.instances_to_ping=instances_to_ping
    
    def run(self,consolidator_queue,logging_queue):
        self._consolidator_queue=consolidator_queue
        self.logging_queue=logging_queue
    
        while True:
            for instance in self.instances_to_ping:
                self.ping_instance(instance)
            time.sleep(self.seconds_between_pings)
            
    def ping_instance(self,instance):
        pass
        #TODO - send a message to ~/services/dashboard/active
        #Parse the result and send an event to the notification queue

class SiteScheduler():
    def __init__(self,site, rrulestr, event_type):
        '''
        :oaram site: Site name 
        :param site_sync_schedule: a dictionary of site names and RRULE strings - see https://dateutil.readthedocs.io/en/stable/examples.html#rrulestr-examples and http://recurrance.sourceforge.net/
        :param event_type: Event.type string to put on the outgoing queue during .run()
        '''
        self.site = site
        #recurrence rule for scheduling
        try:
            self.rrule = rrule.rrulestr(rrulestr)
        except Exception:
            log.error('Exception raised while parsing recurrence rule string:'+str(rrulestr))
            raise
        
        self._event_type = event_type
    
    def run(self,consolidator_queue,logging_queue):
        self._consolidator_queue=consolidator_queue
        self.logging_queue=logging_queue
    
        self.scheduler = sched.scheduler()
        self.rrule.cache=True
        
        #self.rrule will keep on generating events forever
        #Stick on date on the scheduler at a time and call run() which runs all of the scheduled events (i.e. this one)
        for dt in self.rrule:
            right_now = datetime.datetime.now()
            seconds = (dt - right_now).seconds
            days    = (dt - right_now).days
            total_seconds = days*24*60*60 + seconds
            #print(total_seconds)
            if total_seconds >= 0:
                print(dt)
                self.scheduler.enterabs(time=total_seconds, priority = 1, action = self.queue_request)
                #Run will block until the task is run
                self.scheduler.run()
            
    def queue_request(self):
        #Queue up our request for AD_Sync, site publish or other site event
        sync_event=Event()
        sync_event._site=self.site
        sync_event._type=self._event_type
        print(str(sync_event))
        self._consolidator_queue.put(sync_event)
     
######################################################################
        
            
class EventConsolidator():
    
    def __init__(self):
        self.server        = None
        self.other_servers = []
        self.empower_web_instances = {}
        self.empower_sites = {}
        self.empower_users = {}
        
    def run(self,source_queue,notifier_queue,logging_queue):
        
        self._source_queue = source_queue
        self._notifier_queue = notifier_queue
        self._logging_queue = logging_queue
        
        while True:
            msg = self._source_queue.get()
            self.consolidate(msg)
    
    def consolidate(self,event):
        
        #A list of new events we will be creating - we will comb through these, not naively pass them on
        new_events=[]
        
        
        if event._type=='REPORT':
            for web_instance in self.empower_web_instances.values():
                web_instance.report()
            
        else:
            
            #Create and add new users, sites, panels and web_instances
            if event._server is not None:
                try:
                    web_instance = self.empower_web_instances[event._server]
                except KeyError:
                    web_instance = EmpowerWebInstance(name=event._server)
                    self.empower_web_instances[event._server] = web_instance
                    log.info('Consolidator discovered new web instance '+web_instance.name)
                
                new_events += web_instance.consolidate_event(event)
            
            if event._user is not None:
                try:
                    user = self.empower_users[event._user]
                except KeyError:
                    user = EmpowerUser(name=event._user)
                    self.empower_users[event._user] = user
                    #log.info('Consolidator discovered new user '+user.name)
                
                new_events += user.consolidate_event(event)
            
            #Go through the new events that have been created
            
            #Generate new events and place them on the relevant queues
            for event in new_events:
                #Send notification requests to the Notifier
                if isinstance(event,NotificationRequest):
                    self._notifier_queue.put(event)
                    

class Notifier():   
    def __init__(self,saved_notifications_directory,notification_rule_directory,notifiee_details_directory):
        self.saved_notifications_directory  = saved_notifications_directory
        self.notification_rule_directory    = notification_rule_directory
        self.notifiee_details_directory     = notifiee_details_directory
        
    def run(self,source_queue,logging_queue,email_queue):
        self._source_queue                  = source_queue
        self.email_queue                    = email_queue     
    
        #Read in notifiees
        self._notifiees = {}
    
        while True:
            msg = self._source_queue.get()
            self.handle_notification_request(msg)
            
    def handle_notification_request(self,msg):
        #Need to work out whether we want to send this message on to this particular notifiee
    
        #Lookup the notifiee rules
        notifiee_string = msg.target
        try:
            notifiee=self._notifiees[notifiee_string]
        except KeyError:
            
            notifiee=Notifiee(name=notifiee_string, saved_notifications_directory=self.saved_notifications_directory, notification_rule_directory=self.notification_rule_directory, notifiee_details_directory=self.notifiee_details_directory)
            self._notifiees[notifiee_string]=notifiee
        
        #Check whether we have passed the rules regarding sending it on
        if notifiee.accept_reject_messaging_request(msg):

            #get the batch file that sends emails
            
            #Look up the notifiee email from/to
            #The emailer will know the smtp server
            
            _from    = notifiee._from
            _to      = notifiee._to
            _subject = msg.subject
            _message = msg.message
            
            self.email_queue.put((_from,_to,_subject,_message))
            
            #write the sent message into the 
            file_name = msg.head_type + '_' + datetime.datetime.strftime(datetime.datetime.now(),'%Y%m%d_%H%M%S_%f')+'.json'
            with open(os.path.join(notifiee.saved_notifications_directory,file_name),'w') as msg_file:
                json.dump(msg.to_json_dct(),msg_file)
                msg_file.flush()
                
    
    def read_notification_rules(self, notifiee_string):
    
        return []
    
class Notifiee():
    def __init__(self,name, saved_notifications_directory, notification_rule_directory, notifiee_details_directory):
        self.name = name 
        
        self.notifiee_details_directory    = os.path.join(notifiee_details_directory,   self.name)
        self.saved_notifications_directory = os.path.join(saved_notifications_directory,self.name)
        #discover rule files for this user
        #Files will be in a directory with the notifiee name
        self.notification_rule_directory = os.path.join(notification_rule_directory,name)
        self._notification_rules = []
        
        self._to   = None
        self._from = None
        
        try:
            os.mkdir(self.notifiee_details_directory)
        except FileExistsError:
            try:
                #Try to read the notification rules yaml
                with open(os.path.join(self.notifiee_details_directory,'config.yml')) as config_yml_file:
                    config_dct=yaml.load(config_yml_file)
                
                self._from = config_dct['from']
                self._to   = ','.join(config_dct['to'])
                
            except FileNotFoundError:
                pass
        
        try:
            os.mkdir(self.saved_notifications_directory)
        except FileExistsError:
            pass
        
        try:
            os.mkdir(self.notification_rule_directory)
        except FileExistsError:
            #if the notification rule directory exists, read the ruls from it (if they are there)
            if os.path.isdir(self.notification_rule_directory): 
                for f in self.notification_rule_directory:
                    if os.path.splitext(os.path.join(self.notification_rule_directory,f))=='.json':
                        #Load a dictionary from the file using json.load
                        #Convert the dictionary into a notification rule
                        nr = NotificationRule.as_notification_rule(json.load(rule_file, object_hook=NotificationRule.as_notification_rule))
                        self._notification_rules.append(nr)
            
        self.days_to_retain_sent_messages = 7
        
        if self._notification_rules==[]:
            #If we don't have a notification rule directory and stored data with rules, then create a default Notification Rule
            self._notification_rules = [NotificationRule()]
        
    def accept_reject_messaging_request(self,msg):
        #See if there is a matched message that has previously gone out, with a timestamp
        
        #read in previous messages from the directory
        previous_messages=[]
        
        #Delete mssages in directory greater than certain date
        #self.days_to_retain_sent_messages
        for f in os.listdir(self.saved_notifications_directory):
            
            p_msg_time=datetime.datetime.strptime(os.path.splitext(f)[0][-22:-7],'%Y%m%d_%H%M%S')
            
            with open(os.path.join(self.saved_notifications_directory,f),'r') as msg_file:
                p_msg = json.load(msg_file,object_hook=NotificationRequest.from_json_dct)
                p_msg.time = p_msg_time
                previous_messages.append(p_msg)
                
            #Delete files that have hung around beyond their retention period
            if p_msg_time < datetime.datetime.now() - relativedelta.relativedelta(days=self.days_to_retain_sent_messages):
                os.remove(os.path.join(self.saved_notifications_directory,f))

        #self.saved_notifications_directory
        #
        accept_reject = True
        
            #print(previous_message.type, msg.type)
            #print(previous_message.subject, msg.subject)
            #print(previous_message.message, msg.message)
        for nr in self._notification_rules:
            accept_reject = accept_reject and nr.accept_reject_messaging_request(msg,previous_messages)

        return accept_reject
            
class NotificationRule():

    def __init__(self):

        self.no_messages_ever = False
    
        #base number of hours before repeating an email, if the same message and 
        self.info_repeat_email_hours = 1
        #The second time the email comes through wait this factor times the original number of hours
        #so if info_repeat_email_tailoff_factor=2 then wait twice as longbefore sending and email with the same content
        self.info_repeat_email_tailoff_factor = 2

        self.warning_repeat_email_hours = 1
        self.warning_repeat_email_tailoff_factor = 1
        
        self.error_repeat_email_hours = 0.5
        self.error_repeat_email_tailoff_factor = 1
            
    def as_notification_rule(dct):
    
        nr = NotificationRule()
        
        try:
            nr.no_messages_ever                     = dct['no messages ever']
        except KeyError:
            pass
            
        try:
            nr.info_repeat_email_hours              = dct['info repeat email hours']
        except KeyError:
            pass
            
        try:
            nr.info_repeat_email_tailoff_factor     = dct['info repeat tailoff factor']
        except KeyError:
            pass
                                                  
        try:
            nr.warning_repeat_email_hours           = dct['warning repeat email hours']
        except KeyError:
            pass
            
        try:
            nr.warning_repeat_email_tailoff_factor  = dct['warning repeat tailoff factor']
        except KeyError:
            pass
                                                  
        try:
            nr.error_repeat_email_hours             = dct['error repeat email hours']
        except KeyError:
            pass
        
        try:
            nr.error_repeat_email_tailoff_factor    = dct['error repeat tailoff factor']
        except KeyError:
            pass
        
        return nr

    def accept_reject_messaging_request(self,msg,previous_messages):
        if self.no_messages_ever:
            return False
        
        number_of_same_message_sent_before = 0
        hours_since_last_message=999999999
        
        for previous_message in previous_messages:
            if previous_message.type == msg.type and previous_message.subject == msg.subject and previous_message.message == msg.message:
                number_of_same_message_sent_before += 1
                #Track how many hours since the last message, and the number of messages we've sent
                td = datetime.datetime.now() - previous_message.time
                
                hours_since_message = td.days*24 + td.seconds/3600
                
                if hours_since_message < hours_since_last_message:
                    hours_since_last_message  = hours_since_message
                
         
        if number_of_same_message_sent_before==0:
            return True
        
        if msg.head_type == 'ERROR':
            if hours_since_last_message >= (self.error_repeat_email_hours * self.error_repeat_email_tailoff_factor ** number_of_same_message_sent_before) :
                return True
            else:
                return False
        
        if msg.head_type == 'WARNING':
            if hours_since_last_message >= (self.warning_repeat_email_hours * self.warning_repeat_email_tailoff_factor ** number_of_same_message_sent_before):
                return True
            else:
                return False

        if msg.head_type == 'INFO':
            if hours_since_last_message >= (self.info_repeat_email_hours * self.info_repeat_email_tailoff_factor ** number_of_same_message_sent_before):
                return True
            else:
                return False
                
class Emailer():
    def __init__(self,smtp_server,mode):
        self._smtp_server = smtp_server
        
        if mode not in ['powershell','exe','python']:
            raise ArgumentError("mode parameter of Emailer class must be one of 'powershell','exe' or 'python'")
        self._mode = mode
        
        self.send_methods = {'powershell' : self.send_email_via_powershell
                            ,'exe'        : self.send_email_via_exe
                            ,'python'     : self.send_email_via_python
                            }
        
    def run(self,email_queue):
    
        self._email_queue = email_queue
        
        while True:
            _from,_to,_subject,_message = self._email_queue.get()
            self.send(_from,_to,_subject,_message)
            
    def send(self,_from,_to,_subject,_message):
        #Send the message via powershell, the email.exe written by Richard, or 
        
        #Three ways to send email
        #powershell
        #email
        #python
        log.info('Sending message '+str((_from,_to,_subject,_message))+' on outgoing server '+str(self._smtp_server))
        result_code, message_str = self.send_methods[self._mode](subj=_subject,msg=_message,smtp=self._smtp_server,frm=_from,to=_to)
        if result_code != 0:
            log.error('Error sending message '+str((_from,_to,_subject,_message))+' on outgoing server '+str(self._smtp_server))
            log.error(message_str)

    def send_email_via_exe(self,subj,msg,smtp,frm,to):   
        raise SystemError('send_email_via_exe not yet coded')
    def send_email_via_python(self,subj,msg,smtp,frm,to):   
        raise SystemError('send_email_via_python not yet coded')
        
    def send_email_via_powershell(self,subj,msg,smtp,frm,to):
        #TODO email script path should be in utils same as the importer script paths
        
        #Build the powershell command
        emailScriptPath=pkg_resources.resource_filename('empower_utils','powershell_scripts/BatchEmailer.ps1')

        args =[subj,msg,smtp,frm,to]
        #Quote arguments and separate with spaces
        ps_cmd = r'powershell.exe -ExecutionPolicy Bypass -command "'+ emailScriptPath +'"'+ "".join([" '" + i + "'" for i in args])
        
        #run the powershell command to send the email
        result = subprocess.run(ps_cmd
                               ,shell=True
                               ,stdout = subprocess.PIPE
                               ,stderr = subprocess.PIPE
                               )
         
        return result.returncode, 'STDOUT:'+result.stdout.decode('utf-8')+', STDERR:'+result.stderr.decode('utf-8')
            
#TODO - move this to a separate script
class ServerManipulator():
    
    def __init__(self):
        pass
        
    def run(self,source_queue,consolidator_queue,logging_queue):
        self._source_queue       = source_queue
        self._consolidator_queue = consolidator_queue
        self.logging_queue       = logging_queue
    
    #TODO - handle messages and use Tim's script to publish, sync_ad and switch iis services on or off


def parse_and_run():
    
    '''Read the arguments from the command line, check that required files are in place and run all of the requested batch processes.
    
    The 'parse' in parse_and_run() refers to parsing the options on the command line.
    To see the latest list of options run the following on the command line::
    
        python server_monitor.py --help
    '''

    try:
        
        default_log_location='.'
        
        #main process date string is passed to all subprocesses, allowing them to write to the same folder
        main_process_date_str=datetime.datetime.strftime(datetime.datetime.now(),'%Y%m%d_%H%M%S_%f')

        
        parser = argparse.ArgumentParser(description='Monitor an Empower web environment')

        parser.add_argument("-d"
                           ,"--root"
                           ,action='store'
                           ,metavar='FILE'
                           ,default=None
                           ,help="specify a valid root directory to store configuration and data")

        parser.add_argument("-y"
                           ,"--config"
                           ,action='store'
                           ,metavar='FILE'
                           ,default=None
                           ,help="specify a valid YAML file to hold the configuration")

        
        parser.add_argument("-g"
                           ,"--logdir"
                           ,action='store'
                           ,metavar='FILE'
                           ,default=None
                           ,help="Directory for the log file (default: %(default)s)")
                           
        args = parser.parse_args()

        server_monitor_root_directory   = args.root
        
        if args.root is None:
            print('You must set a root directory when calling this script')
            print()
            parser.print_help()
            return
        
        config_file_path                = args.config
        
        listener = None
        if args.logdir is not None:
            logging_queue,listener=logconfig.add_file_handler(log,log_directory=args.logdir)
            
        try:    
            sm = ServerMonitor(server_monitor_root_directory=server_monitor_root_directory
                              ,config_file_path=config_file_path
                              )
                              
            sm.run()
        finally:
            #Stop listening for new log messages
            if listener:
                listener.stop()                                      


    except CompletelyLoggedError:
        log.error('Previous errors caused job to fail - please review log')

    
if __name__=='__main__':
    
    parse_and_run()
    