#!/usr/bin/python

#MUST specify field names with ids in this sdk

# RMI commits to python 3.6.5+
import urllib.request, urllib.parse #Use this for Python > 3
import xml.etree.ElementTree as elementree
import re
import datetime
from rmi_qb_sdk import error_codes

class QBConn:
	def __init__(self,url,appid,app_token=None, user_token=None,realm=None):
		self.url = url
		self.app_token = app_token
		self.user_token = user_token
		self.appid = appid
		self.username = None
		self.password = None
		self.ticket = None 
		self.realm = realm	#This allows one QuickBase realm to proxy for another
		self.error = 0		#Set after every API call. A non-zero value indicates an error. A negative value indicates an error with this library
		self.tables = {}

	def authenticate(self,username=None,password=None):
		if self.user_token:
			self.tables = self._getTables()
			return self.tables
						
		if username == None:
			username = self.username
		if password == None:
			password = self.password
		params = {'act':'API_Authenticate','username':username,'password':password}
		# QB tickets expire every 12 hours by default
		# so let's get a new ticket after 11 hours and 59 minutes
		self.ticket_expires_after = datetime.datetime.now() + datetime.timedelta(0,43140)
		resp = self.request(params,'main')
		if self.error != 0:
			return

		else:
			self.username = username
			self.password = password
			self.ticket = resp["results"].find("ticket").text
			self.tables = self._getTables()
			return self.tables

	#Adds the appropriate fields to the request and sends it to QB
	#Takes a dict of parameter:value pairs and the url extension (main or your table ID, mostly)
	def request(self,params,url_ext):
		if datetime.datetime.now() > self.ticket_expires_after:
			# ticket has expired; reauthenticate
			self.authenticate()
		url = self.url
		url += url_ext		
		if self.user_token:
			params['usertoken'] = self.user_token
		else:
			params['ticket'] = self.ticket
			
		params['apptoken'] = self.app_token
		if self.realm:
			params['realmhost'] = self.realm
		urlparams = urllib.parse.urlencode(params)
		final_url = url+"?"+urlparams
		resp = urllib.request.urlopen(final_url).read()
		if re.match(r'^\<\?xml version=',resp.decode("utf-8")) == None:
			print("No useful data received")
			self.error = -1		#No XML data returned
		else:
			tree = elementree.fromstring(resp)
			self.error = int(tree.find('errcode').text)
			results = tree
			if self.error != 0:
				results =  tree.find('errdetail').text
			return {
				"results": results,
				"error": error_codes.codes[self.error]
			}

	#Creates a record with the given data in the table specified by tableID
	#Takes a tableID (you can get this using qb.tables["yourtable"])
	def addRecord(self,tableID,data):
		params = {'act':'API_AddRecord'}
		for field_id in data:
			params["_fid_"+str(field_id)] = data[field_id]
		results = self.request(params,tableID)
		if results["error"]["response_code"] == 200:
			results["error"]["response_code"] = 201
		return results

	#Updates a reord with the given data
	#Takes the record's table ID, record ID, a dict containing field:newvalue pairs, and an optional dict with param:value pairs
	def editRecord(self,tableID,rid,newdata,options={}):
		params = {'act':'API_EditRecord','rid':rid}
		for key,value in list(newdata.items()):
			params["_fid_"+key] = value
		params = dict(params,**options)
		return self.request(params,tableID)

	#Deletes the record specified by rid from the table given by tableID
	def deleteRecord(self,tableID,rid):
		params = {'act':'API_DeleteRecord','rid':rid}
		return self.request(params,tableID)

	#Deletes every record from tableID selected by query
	def purgeRecords(self,tableID,query):
		params = {'act':'API_PurgeRecords','query':query}
		return self.request(params,tableID)

	#Returns a dict containing table metadata
	def getTableMetadata(self,tableID):
		params = {'act':'API_GetSchema'}
		schema = self.request(params,tableID)
		table = schema["results"].find('table')
		ret = {}
		ret["name"] = table.find('name').text
		ret["desc"] = table.find('desc').text
		original = table.find('original')
		ret["creation_date"] = original.find('cre_date').text
		ret["modify_date"] = original.find('mod_date').text
		ret["next_record_id"] = original.find('next_record_id').text
		ret["next_field_id"] = original.find('next_field_id').text
		ret["next_report_id"] = original.find('next_query_id').text
		return ret

	#Returns a dict containing fieldname:fieldid pairs
	#Field names will have spaces replaced with not spaces
	def getFields(self,tableID):
		params = {'act':'API_GetSchema'}
		schema = self.request(params,tableID)
		fields = schema["results"].find('table').find('fields')
		fieldlist = {}
		for field in fields:
			label = field.find('label').text.lower().replace(' ','')
			fieldlist[label] = {
				"id": field.attrib['id'],
				"type": field.attrib['field_type']
			}
		return fieldlist

	#Returns a dict containing fieldid:choices associated with that field
	#(for multiselect)
	#ideally, this wouldn't need a separate GetSchema call
	#but I didn't want to rewrite the getFields api at this time
	def getChoices(self,tableID):
		params = {'act':'API_GetSchema'}
		schema = self.request(params,tableID)
		# it would be really nice if there were a caching policy
		# we'll use cachetools or equivalent in rmiAPI
		fields = schema["results"].find('table').find('fields')
		fieldlist = {}
		for field in fields:
			choices = None
			if field.find('choices'):
				choices = []
				for choice in field.find('choices'):
					choices.append(choice.text)
				fieldlist[field.attrib['id']] = choices
		return fieldlist

	#Returns a dict of tablename:tableID pairs
	#This is called automatically after successful authentication
	def _getTables(self):
		if self.appid == None:
			return {}
		params = {'act':'API_GetSchema'}
		schema = self.request(params,self.appid)
		chdbs = schema["results"].find('table').find('chdbids')
		tables = {}
		for chdb in chdbs:
			tables[chdb.attrib['name'][6:]] = chdb.text
		return tables

	#Executes a query on tableID
	#Returns a list of dicts containing fieldname:value pairs. record ID will always be specified by the "rid" key
	def query(self,tableID,query,qid, clist=None):
		params = dict()
		params['query'] = query
		if clist:
			params['clist'] = clist
		if qid:
			params['qid'] = qid
		params['act'] = "API_DoQuery"
		params['includeRids'] = '1'
		params['fmt'] = "structured"
		results = self.request(params,tableID)
		ret = {
			"error": results["error"]
		}
		# not crazy about this...
		if results["error"]["message"] == "No error":
			records = results["results"].find('table').find('records')
			data = []
			fields = {fid["id"]:name for name,fid in list(self.getFields(tableID).items())}
			for record in records:
				temp = {}
				temp['rid'] = record.attrib['rid']
				for field in record:
					if(field.tag == "f"):
						temp[fields[field.attrib['id']]] = field.text
				data.append(temp)
			ret["results"] = data
		else:
			ret["results"] = None
		return ret

	#Emulates the syntax of basic (SELECT,DELETE) SQL queries
	#Example: qb.sql("SELECT * FROM users WHERE name`EX`John\_Doe OR role`EX`fakeperson") #The \_ represents a space. This is a very basic function that doesn't use state machines. Note: field and table names will not have spaces
	#Example: qb.sql("SELECT firstname|lastname FROM users WHERE paid`EX`true ORDER BY lastname ASC LIMIT 100")
	#Example: qb.sql("DELETE FROM assets WHERE value`BF`0")
	#RMI: Not sure that I see the point of this for us, but leaving it in for now.
	def sql(self,querystr):
		tokens = querystr.split(" ")
		if tokens[0] == "SELECT":
			query = {}
			tid = self.tables[tokens[3]]
			tfields = self.getFields(tid)
			if tokens[1] != "*":
				clist = ""
				for field in tokens[1].split("|"):
					clist += tfields[field]+"."
				query['clist'] = clist[:len(clist)-1]
			if len(tokens) > 4:
				try:
					where = tokens.index("WHERE")
					querystr = ""
					for i in range(where+1,len(tokens)):
						if (i-where+1)%2 == 0:
							filt = tokens[i].split("`")
							querystr += "{'"+tfields[filt[0]]+ \
							"'."+filt[1]+".'"+filt[2].replace(r"\_"," ")+"'}"
						elif tokens[i] == "AND" or tokens[i] == "OR":
							querystr += tokens[i]
						else:
							break
					query['query'] = querystr
				except ValueError:
					pass
				except:
					print("SQL error near WHERE")
					self.error = -2
					return

				try:
					orderby = tokens.index("ORDER")+1
					orderings = tokens[orderby+1].split("|")
					slist = ""
					for ordering in orderings:
						slist += tfields[ordering]+"."
					query['slist'] = slist[:len(slist)-1]
					query['options'] = (query['options']+"." if 'options' in query else "")+"sortorder-"+("A" if tokens[orderby+2] == "ASC" else "D")
				except ValueError:
					pass
				except:
					print("SQL error near ORDER")
					self.error = -2
					return

				try:
					limit = tokens[tokens.index("LIMIT")+1]
					limit = limit.split(",")
					if(len(limit) > 1):
						query['options'] = (query['options']+"." if 'options' in query else "")+"skp-"+limit[0]+".num-"+limit[1]
					else:
						query['options'] = (query['options']+"." if 'options' in query else "")+"num-"+limit[0]
				except ValueError:
					pass
				except:
					print("SQL error near LIMIT")
					self.error = -2
					return

			return self.query(tid,query)

		elif tokens[0] == "DELETE":
			tid = self.tables[tokens[2]]
			tfields = self.getFields(tid)
			where = 3
			querystr = ""
			for i in range(where+1,len(tokens)):
				if (i-where+1)%2 == 0:
					filt = tokens[i].split("`")
					querystr += "{'"+tfields[filt[0]]+"'."+filt[1]+".'"+filt[2]+"'}"
				elif tokens[i] == "AND" or tokens[i] == "OR":
					querystr += tokens[i]
				else:
					break
			return self.purgeRecords(tid,querystr)