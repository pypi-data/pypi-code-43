"""
voQuery Module

Query TAP (and other VO) Services

@author: stelios
"""

import urllib
import time
try:
    import simplejson as json
except ImportError:
    import json
import logging
from astropy.table import Table
from io import StringIO
import xml.etree.ElementTree as ET

class VOQuery():
    """
    Run a ADQL/TAP query, does an asynchronous TAP job behind the scene
    """

    def __init__(self, endpointURL, query, mode="async", request="doQuery", lang="ADQL", voformat="votable", maxrec=None):
        self.endpointURL = endpointURL
        self.query, self.lang = query, lang
        self.mode = mode
        self.voformat = voformat
        self.request = request
        self.maxrec = maxrec
        self.votable = None
        self.error = None

    
    def get_error(self):
        """Error message"""
        return self.error


    def run(self):
        """
        Run the query
        Todo: Add synchronous query capability
        """
        if self.mode.lower()=="async":
            self.votable = self.execute_async_query(self.endpointURL, self.query, self.mode, self.request, self.lang, self.voformat, self.maxrec)
        else:
            self.votable = self.execute_sync_query(self.endpointURL, self.query, self.mode, self.request, self.lang, self.voformat, self.maxrec)


        return self.votable


    def _get_url(self, endpointURL, extension):
        """
        Open the given url and extension and read/return the result

        @param endpointURL: A URL string to open
        @param extension: An extension string to attach to the URL request
        @return: The result of the HTTP request sent to the the URL
        """

        res = ''
        try:
            req = urllib.request.Request(endpointURL + extension)
            with urllib.request.urlopen(req) as response:
                res = response.read().decode('utf-8')
        except Exception as e:
            logging.exception(e)

        return res


    def _async_loop(self, url):
        """
        Takes a TAP url and starts a loop that checks the phase URI and returns the table when completed. The loop is repeated every [delay=3] seconds

        @param url: A URL string to be used
        @return: A Votable with the table of a TAP job, or '' if error
        """

        return_vot = None
        try:
            while True:
                res = self._get_url(url,'/phase')
                if res=='COMPLETED':
                    return_vot = Table.read(url + '/results/result', format="votable")
                    break
                elif res=='ERROR' or res=='':                    
                    tree = ET.fromstring(str(self._get_url(url,'/error')))
                    self.error = (ET.tostring(tree, encoding='utf-8', method='text'))
                    return None
                time.sleep(1)
        except Exception as e:
            logging.exception(e)
            self.error = str(e)
            return None

        return return_vot


    def rowcount(self):
        """
        Get table rowcount
        """
        if not self.votable is None:
            return len(self.votable)
        else :
            return -1


    def execute_sync_query(self, url, q, mode="async", request="doQuery", lang="ADQL", voformat="votable", maxrec=None):
        """
        Execute an ADQL query (q) against a TAP service (url + mode:sync|async)
        Starts by submitting a request for an async query, then uses the received job URL to call start_async_loop, to receive the final query table

        @param url: A string containing the TAP URL
        @param mode: sync or async to determine TAP mode of execution
        @param q: The ADQL Query to execute as string

        @return: Return a votable with the table, the TAP job ID and a temporary file path with the table stored on the server
        """

        if (maxrec!=None):
            full_url = url + "/" + mode + "?QUERY=" + urllib.parse.quote_plus(q) + "&REQUEST=doQuery&LANG=ADQL&FORMAT=VOTABLE"
        else:
            full_url = url + "/" + mode + "?QUERY=" + urllib.parse.quote_plus(q) + "&REQUEST=doQuery&LANG=ADQL&FORMAT=VOTABLE"
    
        try:
            # Return table as a votable object
            self.votable = Table.read(full_url, format="votable")

        except Exception as e:
            logging.exception(e)
            self.error = str(e)

        return self.votable




    def execute_async_query(self, url, q, mode="async", request="doQuery", lang="ADQL", voformat="votable", maxrec=None):
        """
        Execute an ADQL query (q) against a TAP service (url + mode:sync|async)
        Starts by submitting a request for an async query, then uses the received job URL to call start_async_loop, to receive the final query table

        @param url: A string containing the TAP URL
        @param mode: sync or async to determine TAP mode of execution
        @param q: The ADQL Query to execute as string

        @return: Return a votable with the table, the TAP job ID and a temporary file path with the table stored on the server
        """

        if (maxrec!=None):
            params = urllib.parse.urlencode({'REQUEST': request, 'LANG': lang, 'FORMAT': voformat, 'QUERY' : q, 'MAXREC' : maxrec}).encode('utf-8')
        else:
            params = urllib.parse.urlencode({'REQUEST': request, 'LANG': lang, 'FORMAT': voformat, 'QUERY' : q}).encode('utf-8')

        full_url = url+"/"+mode
        jobId = 'None'

        try:
            #Submit job and get job id
            req = urllib.request.Request(full_url, params)
            opener = urllib.request.build_opener()

            f = opener.open(req)
            jobId = f.url
            #Execute job and start loop requests for table
            req2 = urllib.request.Request(jobId+'/phase',urllib.parse.urlencode({'PHASE' : 'RUN'}).encode("utf-8"))
            f2 = opener.open(req2) #@UnusedVariable

            # Return table as a votable object
            self.votable = self._async_loop(jobId)

        except Exception as e:
            logging.exception(e)
            self.error = str(e)

        return self.votable




