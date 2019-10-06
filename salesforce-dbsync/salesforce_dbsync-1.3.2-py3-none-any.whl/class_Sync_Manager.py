from salesforce_dbsync.class_MySQL_Helper import MySQL_Helper
from salesforce_dbsync.class_SFDC_Helper import SFDC_Helper
import json

class Sync_Manager:

	def __init__ (self, p_sw, db_creds, sfdc_creds, control_map):
		self.sync_profile = {}
		self.sw = p_sw
		self.sf = SFDC_Helper (sfdc_creds, p_sw)
		self.mh = MySQL_Helper (db_creds, p_sw)
		default_min_dt = '2000-01-01' if 'min-SystemModstamp-date' not in control_map.keys() else control_map['min-SystemModstamp-date']
		self.min_default_ts = default_min_dt + 'T00:00:00.000+0000'
		self.dml_limit = 100 if 'dml-limit' not in control_map.keys() else control_map['dml-limit']
		self.fx_loaded = False

	def init_mysql (self):
		self.mh.create_database_if_not_exists ()

	def init_sfdc (self):
		self.sf.connect ()

	def add_sync_profile (self, table_name, columns, filters):
		prec = {}
		if 'Id' not in columns:
			columns.append ('Id')
		if 'SystemModstamp' not in columns:
			columns.append ('SystemModstamp')
		prec ['columns'] = columns
		prec ['filters'] = filters
		self.sync_profile [table_name] = prec

	def get_sql_datatype_from_sfdc_field (self, field):
		if field['name'].lower() == 'id':
			return 'CHAR (18) PRIMARY KEY'
		if field['type'] in ['id', 'reference']:
			return 'CHAR (18)'
		if field['type'] in ['boolean']:
			return 'CHAR (3)'
		if field['type'] in ['string', 'picklist', 'textarea', 'phone', 'email', 'url', 'multipicklist', 'encryptedstring']:
			if field['length'] <= 255:
				return 'CHAR (' + str(field['length']) + ')'
			else:
				return 'VARCHAR(' + str(field['length']) + ')'
		if field['type'] == 'address':
			return None
		if field['type'] in ['double', 'currency', 'location']:
			self.isdouble = True
			return 'DECIMAL (18, 3)'
		if field['type'] in ['datetime']:
			return 'CHAR (28)'
		if field['type'] in ['int', 'date']:
			return field['type'].upper()
		print ('ERROR! ' + field['name'] + ': INVALID TYPE: ' + str(field['type']) + ', ' + str(field['length']))
		exit(1)

	def create_missing_db_tables (self):
		if not self.mh.connected_to_db:
                        self.mh.connect_db ()
		for table_name in self.sync_profile.keys():
			if not self.mh.table_exists (table_name):
				prec = self.sync_profile[table_name]
				ddl_columns = []
				indexable_columns = []
				for field in self.sf.describe_object (table_name):
					if field['name'] in prec['columns']:
						ddl_columns.append (field['name'] + ' ' + self.get_sql_datatype_from_sfdc_field (field))
						if field['type'] in ['id', 'reference', 'datetime', 'date']:
							indexable_columns.append (field['name'])
				if 'USD' in prec.keys():
					ddl_columns.append (prec['USD'][2] + ' DECIMAL (18, 3)')
				ddl_stmt = 'CREATE TABLE ' + table_name + ' (\n' + ",\n".join(ddl_columns) + '\n)'
				index_stmts = []
				for i_col in indexable_columns:
					index_stmts.append ('CREATE INDEX idx_' + i_col + ' ON ' + table_name + ' (' + i_col + ')')
				self.mh.create_table_and_indexes (table_name, ddl_stmt, index_stmts)

	def add_USD_col (self, table_name, amt_col, curr_col, new_col):
		prec = self.sync_profile [table_name]
		prec ['USD'] = (amt_col, curr_col, new_col)
		self.sync_profile [table_name] = prec

	def sync_table (self, table_name, dump_records_onscreen=False):
		last_ts = str (self.mh.get_max_value (table_name, 'SystemModstamp', self.min_default_ts))
		self.sw.echo ("Syncing " + table_name + " [SystemModstamp >= " + last_ts + "]")
		prec = self.sync_profile [table_name]
		conditions = ['SystemModstamp >= ' + last_ts]
		for f in prec['filters']:
			conditions.append (f)
		self.sf.load_data (table_name, prec['columns'], conditions, [], self.dml_limit, 'SystemModstamp')
		if 'USD' in prec.keys():
			if not self.fx_loaded:
				self.sf.load_fx_rates ()
				self.fx_loaded = True
				self.sf.calculate_usd_column (table_name, prec['USD'][0], prec['USD'][1], prec['USD'][2])
		delete_count = 0
		unique_ts = set()
		for rec in self.sf.table_data [table_name]:
			if dump_records_onscreen:
				print (json.dumps (rec, default=lambda o: o.__dict__, sort_keys=True, indent=4))
			delete_count += self.mh.insert_rec (table_name, rec, 'Id')
			unique_ts.add (rec ['SystemModstamp'])
		num_synced = len(self.sf.table_data [table_name])
		self.sw.echo (table_name + " Inserted: " + str(num_synced - delete_count))
		self.sw.echo (table_name + " Updated:  " + str(delete_count))
		self.mh.commit ()
		if len(unique_ts) == 1 and num_synced == delete_count and num_synced == self.dml_limit:
			self.sw.error ("Repeat records selected.. This will turn into an infinite loop. Aborting!")
			exit (1)

	def sync (self):
		for table_name in self.sync_profile.keys():
			self.sync_table (table_name)
