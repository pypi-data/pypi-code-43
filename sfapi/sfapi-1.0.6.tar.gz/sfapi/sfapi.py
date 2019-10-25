import xml.etree.ElementTree as ET
import os
import re
import time
import requests
import json
import csv
import datetime

from . import utils


class SFApiException(Exception):
    pass


class BulkJob:
    def __init__(self, api):
        self.api = api

    def run_job(self, operation, object_type, data):
        """Run a complete job with specified parameters.
        data is an array of dictionaries."""
        (jobid, batchid) = self._start_job(operation, object_type, data)
        self._close_job(jobid)
        self._wait_for_batch(jobid, batchid)
        return self._get_batch_result(jobid, batchid)

    def update_result(self, data, result, result_key, error_key='Error'):
        """Update rows in data with the job result (as returned by run_job)"""
        for i in range(len(result)):
            if result[i]['Success'] == 'true':
                data[i][result_key] = result[i]['Id']
            elif error_key:
                data[i][error_key] = result[i]['Error']

    def _start_job(self, operation, object_type, data):
        jobid = self._create_job(operation, object_type)
        batchid = self._create_batch(jobid, data)
        return (jobid, batchid)

    def _create_job(self, operation, object_type):
        """Create bulk job, return job id"""
        # self.async_url = 'https://na17-api.salesforce.com/services/async/v36.0/'
        url = self.api.async_url + 'job'
        payload = '''<?xml version="1.0" encoding="UTF-8"?>
        <jobInfo xmlns="http://www.force.com/2009/06/asyncapi/dataload">
            <operation>%s</operation>
            <object>%s</object>
            <contentType>CSV</contentType>
        </jobInfo>''' % (operation, object_type)
        qr = self.api.do_post_xml(url, payload)
        return qr['id']

    def _create_batch(self, jobid, data):
        """This posts the batch data in CSV format, and return the batch id"""
        csv = utils.make_csv(data)
        payload = csv.encode('utf-8')
        url = self.api.async_url + 'job/' + jobid + '/batch'
        qr = utils.decode_xml(self.api.do_post(
            url, payload, 'text/csv; charset=utf-8'))
        return qr['id']

    def _wait_for_batch(self, jobid, batchid):
        """Wait for a batch to finish processing"""
        status = self._get_batch_status(jobid, batchid)
        while status != 'Completed' and status != 'Failed':
            print('Waiting for batch...')
            time.sleep(15)
            status = self._get_batch_status(jobid, batchid)
        return status

    def _get_batch_result(self, jobid, batchid):
        """Get results for a batch, parse the CSV data into an array of dicts,
        and return the result"""
        url = self.api.async_url + 'job/' + jobid + '/batch/' + batchid + '/result'
        data = self.api.do_get(url, 'text/csv')
        if data.startswith('<'):
            m = re.search('<result>(\\w+)</result>', data)
            if m:
                # append result id, if there was a result-list
                # note, we only get the first result, right now...
                # ideally we should grab all of them
                data = self.api.do_get(url + '/' + m.group(1), 'text/csv')
        return utils.parse_csv(data)

    def _get_batch_status(self, jobid, batchid):
        url = self.api.async_url + 'job/' + jobid + '/batch/' + batchid
        qr = self.api.do_get_xml(url)
        if qr['state'] == 'Failed':
            raise SFApiException(qr['stateMessage'])
        return qr['state']

    def _close_job(self, jobid):
        url = self.api.async_url + 'job/' + jobid
        payload = '''<?xml version="1.0" encoding="UTF-8"?>
        <jobInfo xmlns="http://www.force.com/2009/06/asyncapi/dataload">
            <state>Closed</state>
        </jobInfo>'''
        self.api.do_post_xml(url, payload)


class SFApi:
    def __init__(self):
        pass

    def login(self, user, password, login_url='https://login.salesforce.com'):
        xml = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xmlns:xsd="http://www.w3.org/2001/XMLSchema"
xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
<soap:Body>
 <login xmlns="urn:partner.soap.sforce.com">
  <username>{}</username>
  <password>{}</password>
 </login>
</soap:Body>
</soap:Envelope>""".format(user, password)
        qr = requests.post(login_url + '/services/Soap/u/35.0',
                           headers={'SOAPAction': 'login',
                                    'Content-Type': 'text/xml'},
                           data=xml)

        if qr.status_code == 200:
            xml = ET.fromstring(qr.text)
            self.sessionid = xml.find(
                './/{urn:partner.soap.sforce.com}sessionId').text
            server_url = xml.find(
                './/{urn:partner.soap.sforce.com}serverUrl').text
            self.data_url = re.match('^https://[^/]*', server_url).group(0) + \
                '/services/data/v41.0/'
            # self.async_url = re.match('^(https://[^/]*?)\.salesforce\.com', server_url).group(1) + \
            #     '-api.salesforce.com/services/async/35.0/'
            self.async_url = re.match('^https://[^/]*', server_url).group(0) + \
                '/services/async/41.0/'
        else:
            raise SFApiException('Login failed: ' + qr.text)

    def do_post_xml(self, url, payload):
        return utils.decode_xml(self.do_post(url, payload, 'application/xml'))

    def do_get_xml(self, url):
        return utils.decode_xml(self.do_get(url))

    def do_post(self, url, payload, content_type):
        qr = requests.post(url,
                           headers={'X-SFDC-Session': self.sessionid,
                                    'Content-Type': content_type},
                           data=payload)
        if qr.status_code == 200 or qr.status_code == 201:
            return qr.text
        else:
            raise SFApiException('Request failed: ' + qr.text)

    def do_get(self, url, accept=None):
        headers = {'X-SFDC-Session': self.sessionid}
        if accept:
            headers['Accept'] = accept
        qr = requests.get(url, headers=headers)
        if qr.status_code == 200:
            return qr.text
        else:
            raise SFApiException('Request failed: ' + qr.text)
