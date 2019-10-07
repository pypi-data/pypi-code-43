from simple_salesforce import Salesforce

class SFDC_Helper:

	def __init__(self, p_creds, p_sw):
		self.sf                    = None
		self.sw                    = p_sw
		self.object_labels         = {}
		self.object_desc           = {}
		self.fx_rates              = {}
		self.table_data            = {}
		self.table_data_cols       = {}
		self.conected              = False
		self.standard_object_names = set()
		self.custom_object_names   = set()
		self.custom_setting_names  = set()
		self.userid                = p_creds ['user']   if 'user'   in p_creds.keys() else None
		self.password              = p_creds ['passwd'] if 'passwd' in p_creds.keys() else None
		self.token                 = p_creds ['token']  if 'token'  in p_creds.keys() else None
		
	def connect (self):
		self.sw.echo ("Connecting to SFDC with Userid [" + self.userid + "]")
		self.sf = Salesforce(username=self.userid, password=self.password, security_token=self.token)
		self.sw.echo ("Connected")
	
	def load_metadata (self):
		if len(self.object_labels.keys()) == 0:
			self.sw.echo ("Scanning Standard & Custom Objects")
			for x in self.sf.describe()["sobjects"]:
				api_name = x["name"]
				label = x["label"]
				isCustomSetting = x["customSetting"]
				isCustomObject = x["custom"]
				self.object_labels[api_name] = label
				if isCustomSetting:
					self.custom_setting_names.add (api_name)
				elif isCustomObject:
					self.custom_object_names.add (api_name)
				else:
					self.standard_object_names.add (api_name)

	def describe_object (self, api_name):
		if api_name not in self.object_desc.keys():
			self.sw.echo ("Loading SFDC Metadata for [" + api_name + "]")
			resp = getattr(self.sf, api_name).describe()
			self.object_desc[api_name] = resp['fields']
		return self.object_desc[api_name]

	def load_fx_rates (self):
		self.sw.echo ("Loading Currency Rates..")
		qs = "SELECT ISOCode, ConversionRate FROM CurrencyType WHERE IsActive=TRUE"
		resp = self.sf.query_all (qs)
		loopIndex = 0
		while loopIndex < len(resp['records']):
			self.fx_rates [resp['records'][loopIndex]['IsoCode']] = resp['records'][loopIndex]['ConversionRate']
			loopIndex += 1
		self.sw.echo (str(len(self.fx_rates.keys())) + " Currency Rates Loaded")

	def get_amount_in_USD (self, amount, curreny_code):
		if curreny_code in self.fx_rates.keys():
			return (amount / self.fx_rates[curreny_code])
		return 0.0

	def split_list_into_array_of_lists (self, inlist, arraysize=500):
		array_of_lists = []
		list_items = []
		for member in inlist:
			if len(list_items) >= arraysize:
				array_of_lists.append (list_items)
				list_items = list()
				list_items.append (member)
			else:
				list_items.append (member)
		if len(list_items) > 0:
			array_of_lists.append (list_items)
		return array_of_lists;

	def load_data (self, objectName, colnames, filters, joincondition=[], limit=0, orderby=''):
		self.sw.echo ("Selecting from " + objectName + "..")
		if len(colnames) == 0:
			if objectName not in self.object_desc.keys():
				for field in self.describe_object (objectName):
					colnames.append (field['name'])
		self.table_data[objectName] = []
		self.table_data_cols[objectName] = colnames
		query_list = []
		qs = 'SELECT '
		qs += ','.join (colnames)
		qs += ' FROM ' + objectName
		if (len(filters) > 0):
			qs += ' WHERE ' 
			qs += ' AND '.join (filters)
		if len(orderby) > 0:
			qs += ' ORDER BY ' + orderby
		if limit > 0:
			qs += ' LIMIT ' + str(limit)
		if len(joincondition) == 3:
			joinField = joincondition[0]
			joinedObject = joincondition[1]
			joinedObjectCol = joincondition[2]
			joinVals = []
			for rec in self.table_data[joinedObject]:
				joinVals.append ("'" + rec[joinedObjectCol] + "'")
				if len(joinVals) >= 500:
					qsj = qs + ' AND ' + joinField + ' IN (' + ",".join(joinVals) + ")"
					query_list.append (qsj)
					joinVals = []
			if len(joinVals) > 0:
				qsj = qs + ' AND ' + joinField + ' IN (' + ",".join(joinVals) + ")"
				query_list.append (qsj)
		else:
			query_list.append (qs)

		for qs in query_list:
			resp = self.sf.query_all(qs)
			arrLen = len(resp['records'])
			loopIndex = 0
			while loopIndex < arrLen:
				rec = {}
				for col in colnames:
					if '.' in col:
						colparts = col.split ('.')
						if len(colparts) == 2:
							rec[col] = resp['records'][loopIndex][colparts[0]][colparts[1]]
					else:
						rec[col] = resp['records'][loopIndex][col]
				loopIndex += 1
				self.table_data[objectName].append (rec)
			self.sw.echo (str(len(self.table_data[objectName])) + " rows Selected from " + objectName)

	def calculate_usd_column (self, objectName, amtcol, currencycol, newcol):
		if amtcol in self.table_data_cols[objectName] and currencycol in self.table_data_cols[objectName]:
			self.sw.echo ("Calculating USD Amount in " + newcol)
			newrecs = []
			if newcol not in self.table_data_cols[objectName]:
				self.table_data_cols[objectName].append (newcol)
			for rec in self.table_data [objectName]:
				rec[newcol] = self.get_amount_in_USD (rec[amtcol], rec[currencycol])
				newrecs.append (rec)
			self.table_data[objectName] = newrecs
			self.sw.echo ("USD Amounts calculated for " + str(len(newrecs)) + " records")
