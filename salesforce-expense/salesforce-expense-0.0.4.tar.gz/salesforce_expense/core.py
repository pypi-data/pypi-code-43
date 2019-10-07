#!/usr/bin/env python

import sys
import logging
import base64
from datetime import datetime, timedelta, date
import os
import requests
from simple_salesforce import Salesforce
import json

logger = logging.getLogger("salesforce_expense")


class TimecardEntry(object):


    def __init__(self, cfg="~/.pse.json"):

        self.cfg_file = os.path.expanduser(cfg)
        with open(self.cfg_file) as f:
            self.cfg = json.load(f)
        
        credential_store = self.cfg.get('credential_store', 'default')
        if credential_store == 'default':
            password = base64.b64decode(self.cfg["password"]).decode()
            security_token = self.cfg["token"]
        elif credential_store == 'keyring':
            password = keyring.get_password("salesforce_cli", f"{self.cfg["username"]}_password")
            security_token = keyring.get_password("salesforce_cli", f"{self.cfg["username"]}_token")

        self.sf = Salesforce(username=self.cfg["username"],
                             password=password,
                             security_token=security_token,
                             sandbox=self.cfg.get("sandbox", None),
                             client_id="FF"
                             )

        self.contact_id = self.get_contact_id(self.cfg["username"])
        self.assignments = self.get_assignments_active()

        today = date.today()
        day = today.strftime("%d-%m-%Y")
        self.get_week(day)

    def get_week(self, day):
        dt = datetime.strptime(day, "%d-%m-%Y")
        self.start = dt - timedelta(days=dt.weekday())
        self.end = self.start + timedelta(days=6)

    def safe_sql(self, sql):
        logger.debug(sql)
        try:
            return self.sf.query_all(sql)
        except:
            logger.error("error on query:{}".format(sql))
            logger.error(sys.exc_info()[1])
            sys.exit(1)

    def _upload_image(self, name, parent_id):
        body = self._get_file_body(name)
        upload_url = 'https://%s/services/data/v%s/sobjects/Attachment/' % (self.sf.sf_instance, self.sf.sf_version)

        response = requests.post(upload_url,
                                 headers={'Content-Type': 'application/json',
                                          'Authorization': 'Bearer %s' % self.sf.session_id},
                                 data=json.dumps({
                                     'ParentId': parent_id,
                                     'Name': name,
                                     'body': body
                                 })
                                 )
        r = json.loads(response.text)
        if r['success']:
            return r['id']


    def _get_file_body(self, filename):
        body = ""
        with open(filename, "rb") as f:
            body = base64.b64encode(f.read()).decode()
        return body


    def _upload_expense(self, data, dry_run=False):
        if dry_run:
            print(data)
        else:
            r = self.sf.pse__Expense__c.create(data)
            if r['success']:
                return r['id']            

    def get_contact_id(self, email):
        name_part = email.split("@")[0]
        r = self.safe_sql(
            "select Id, Name, Email from Contact where pse__Is_Resource__c = true and Email LIKE '{}@%'".format(
                name_part))
        return r["records"][0]["Id"]



    def get_assignments_active(self, contact_id = None):
        if not contact_id:
            contact_id = self.contact_id

        SQL = '''select Id, Name, pse__Project__c, pse__Project__r.Name, pse__Project__r.pse__Is_Billable__c from pse__Assignment__c 
        where pse__Resource__c = '{}' and 
        Open_up_Assignment_for_Time_entry__c = false and 
        pse__Closed_for_Time_Entry__c = false and
        pse__Exclude_from_Planners__c = false and
        pse__End_Date__c > {}
        '''.format(
            contact_id,
            date.today().strftime("%Y-%m-%d")
            )

        return self.get_assignments(SQL)        


    def get_assignments(self, SQL):

        results = self.safe_sql(SQL)
        assignments = {}
        for r in results["records"]:
            assignments[r["Id"]] = {"assignment_id": r["Id"], 
                                    "assignment_name": r["Name"], 
                                    "project_id": r["pse__Project__c"],
                                    "project_name": r["pse__Project__r"]["Name"],
                                    "billable": r["pse__Project__r"]["pse__Is_Billable__c"]}
        return assignments



