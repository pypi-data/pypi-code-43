'''
Created on Jul 17, 2018

@author: stelios
'''

try:
    
    import urllib.request
    import firethorn
    import json    
    import logging
    import os
    import sys
    import uuid
    import time
    from argparse import ArgumentParser
    from .util import Utility
    from .slack_sender import SlackSender
except Exception as e:
    logging.exception(e)



class FirethornCheckerResults(object):
    '''
    Firethorn Health Checker Results Class, stores information from a health check run
    '''

    def __init__(self, exceptions={}, message=""):
        '''
        Constructor
        '''
        self.exceptions = exceptions
        self.message = message

        return



class FirethornHealthChecker(object):
    '''
    FirethornHealthChecker class, used to health check a Firethorn System
    '''


    def __init__(self, firethorn_url, verbose = True):
        '''
        Constructor
        '''
        self.verbose = verbose
        self.firethorn_url = firethorn_url
        return


    def check_memory(self, max_percent=None, min_available_bytes=None):     

        exceptions = {}
        message = ""

        try:
            if (self.verbose):
                print ("Checking Firethorn System: " + self.firethorn_url)

            total_bytes = int(self.get_system_info()["java"]["memory"]["total"])
            max_bytes = int(self.get_system_info()["java"]["memory"]["max"])
            free_bytes = int(self.get_system_info()["java"]["memory"]["free"])
           
            used_memory = total_bytes-free_bytes
            usable_bytes = max_bytes - used_memory
            usage_percent = 100-(usable_bytes/max_bytes*100)
            usable_bytes_in_gb = usable_bytes/1024/1024/1024

            if (min_available_bytes!=None):
                if (usable_bytes<float(min_available_bytes)):
                    if (self.verbose):
                        print ("Memory usage is too high! Available Memory: " + ("%.2f" % usable_bytes_in_gb) + " GB  (" + ("%.2f" % usage_percent) + "% Full)")
                    message = "Memory usage is too high! Available Memory: " + ("%.2f" % usable_bytes_in_gb) + " GB  (" + ("%.2f" % usage_percent) + "% Full)"
                    exceptions["mem"] = message

            elif (max_percent!=None):
                if (usage_percent>float(max_percent)):
                    if (self.verbose):
                        print("Memory is too high! Available Memory: " + ("%.2f" % usable_bytes_in_gb) + " GB  (" + ("%.2f" % usage_percent) + "% Full)")
                    message = "Memory usage is too high! Available Memory: " + ("%.2f" % usable_bytes_in_gb) + " GB  (" + ("%.2f" % usage_percent) + "% Full)"
                    exceptions["mem"] = message


        except Exception as e:
            exceptions["vm"] = str(e)
            message = str(e)
            logging.exception(e)

        return FirethornCheckerResults(exceptions = exceptions, message = message)



    def check_disk_space (self, max_percent=None, min_available_bytes=None):

        exceptions = {}
        message = ""

        try:
            if (self.verbose):
                print ("Checking Firethorn System: " + self.firethorn_url)
           
            usable_bytes = int(self.get_system_info()["java"]["disk"]["usable"])
            total_bytes = int(self.get_system_info()["java"]["disk"]["total"])
            usage_percent = 100-(usable_bytes/total_bytes*100)
            usable_bytes_in_gb = usable_bytes/1024/1024/1024

            if (min_available_bytes!=None):
                if (usable_bytes<float(min_available_bytes)):
                    if (self.verbose):
                        print ("Disk space usage is too high! Available Disk Space: " + ("%.2f" % usable_bytes_in_gb) + " GB  (" + ("%.2f" % usage_percent) + "% Full)")
                    message = "Disk space usage is too high! Available Disk Space: " + ("%.2f" % usable_bytes_in_gb) + " GB  (" + ("%.2f" % usage_percent) + "% Full)"
                    exceptions["disk"] = message

            elif (max_percent!=None):
                if (usage_percent>float(max_percent)):
                    if (self.verbose):
                        print("Disk space usage is too high! Available Disk Space: " + ("%.2f" % usable_bytes_in_gb) + " GB  (" + ("%.2f" % usage_percent) + "% Full)")
                    message = "Disk space usage is too high! Available Disk Space: " + ("%.2f" % usable_bytes_in_gb) + " GB  (" + ("%.2f" % usage_percent) + "% Full)"
                    exceptions["disk"] = message
            

        except Exception as e:
            exceptions["vm"] = str(e)
            message = str(e)
            logging.exception(e)

        return FirethornCheckerResults(exceptions = exceptions, message = message)

        
    def get_system_info(self):
        """Wrapper function to send a GET request to get the status of a resource and return the JSON
        
                   
        Returns    
        -------
        query_json:
            The JSON response as a string
        
        """
 
        request = urllib.request.Request(self.firethorn_url + "/system/info")
        query_json = {}

        with urllib.request.urlopen(request) as response:
            query_json = json.loads(response.read().decode('utf-8'))

        return query_json            
            

def main():

    '''
    Validator Arguments
    '''
    parser = ArgumentParser()
    parser.add_argument("-ft", "--firethorn_url", dest="firethorn_url",
                    help="Firethorn Instance URL", metavar="FIRETHORN")
    parser.add_argument("-disk_per", "--disk_max-percent", dest="disk_max_percent",
                    help="Disk Space Max Percentage", metavar="DISK_MAX PERCENT")
    parser.add_argument("-mem_per", "--mem_max_percent", dest="mem_max_percent",
                    help="Memory Max Percentage", metavar="MEM_MAX PERCENT")
    parser.add_argument("-from", "--from", dest="from_email",
                    help="Email from which to send Validation email", metavar="FROM")
    parser.add_argument("-to", "--to", dest="to_email",
                    help="Email to which to send Validation email", metavar="TO")
    parser.add_argument("-slack", "--slack", dest="slack",
                    help="Slack Web Hook to which to send validation message", metavar="SLACK")
    parser.add_argument("-v", "--verbose", dest="verbose",
                    help="Print status messages to stdout")
    

    args = parser.parse_args()    


    fHC_obj = FirethornHealthChecker(args.firethorn_url)

    if (args.disk_max_percent!=None):
        disk_health_check_results = fHC_obj.check_disk_space(max_percent=args.disk_max_percent)
    else : 
        disk_health_check_results = fHC_obj.check_disk_space(max_percent=85)

    if (args.mem_max_percent!=None):
        mem_health_check_results = fHC_obj.check_memory(max_percent=args.mem_max_percent)
    else :
        mem_health_check_results = fHC_obj.check_memory(max_percent=85)

    print ("Disk usage")
    print ("------------------------")

    print (disk_health_check_results.exceptions)
    print (disk_health_check_results.message)

    print ("")
    print ("")
    print ("")


    print ("Memory usage")
    print ("------------------------")


    if (args.mem_max_percent!=None):
        mem_health_check_results = fHC_obj.check_memory(max_percent=args.mem_max_percent)
    else :
        mem_health_check_results = fHC_obj.check_memory(max_percent=85)

    print ("Disk usage")
    print ("------------------------")

    print (disk_health_check_results.exceptions)
    print (disk_health_check_results.message)

    print ("")
    print ("")
    print ("")


    print ("Memory usage")
    print ("------------------------")

    print (mem_health_check_results.exceptions)
    print (mem_health_check_results.message)

    '''
    Send exceptions by email
    '''
    if ((len(disk_health_check_results.exceptions)>0 or len(mem_health_check_results.exceptions)>0) and (args.from_email!=None) and (args.to_email!=None)):
        print ("Sending email with exceptions to: " + args.to_email)
        results = str(disk_health_check_results.message) + " / " + str(mem_health_check_results.message)
        Utility.sendMail(args.from_email, args.to_email, "Health Check Results for: " + args.firethorn_url, results)
    elif ((len(disk_health_check_results.exceptions)>0 or len(mem_health_check_results.exceptions)>0) and (args.slack!=None)):
        print ("Sending email with exceptions to Slack channel..")
        results = str(disk_health_check_results.message) + " / " + str(mem_health_check_results.message)
        slack_sender = SlackSender(args.slack)
        slack_sender.send("Health Check Results for: " + args.firethorn_url + "/system/info " + "\n" + results)



if __name__ == "__main__":
    main()


