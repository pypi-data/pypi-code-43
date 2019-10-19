'''
Created on Jul 17, 2018

@author: stelios
'''

try:
    
    import urllib.request
    import os
    import sys
except Exception as e:
    logging.exception(e)



class Utility(object):
    '''
    Utility functions
    '''

    def __init__(self):
        '''
        Constructor
        '''
        return

    def sendMail(from_email, to_email, subject, body):
        sendmail_location = "/usr/sbin/sendmail" # sendmail location
        p = os.popen("%s -t" % sendmail_location, "w")
        p.write("From: %s\n" % from_email)
        p.write("To: %s\n" % to_email)
        p.write("Subject: " + subject +"\n")
        p.write("\n") # blank line separating headers from body
        p.write(body)
        status = p.close()
        if status != None:
            print ("Sendmail exit status", status)


