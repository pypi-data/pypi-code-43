import mysql.connector

class MySQL_Helper:

	def __init__ (self, p_mysql_creds, p_sw=None):
		self.host    = p_mysql_creds ['host']   if 'host'   in p_mysql_creds.keys() else 'localhost'
		self.user    = p_mysql_creds ['user']   if 'user'   in p_mysql_creds.keys() else None
		self.passwd  = p_mysql_creds ['passwd'] if 'passwd' in p_mysql_creds.keys() else None
		self.db      = p_mysql_creds ['db']     if 'db'     in p_mysql_creds.keys() else None
		self.sw      = p_sw
		self.connected = False
		self.connected_to_db = False
		self.tables  = []

	def connect (self):
		if self.host and self.user and self.passwd:
			self.sw.echo ("Connecting to MySQL. Host[" + self.host + "], User[" + self.user + "]")
			self.mysql = mysql.connector.connect (host=self.host, user=self.user, passwd=self.passwd)
			self.connected = True
			self.connected_to_db = False
			self.sw.echo ("MySQL Connected")
		else:
			self.sw.echo ("ERROR: Missing one or more of [host, user, passwd]")

	def connect_db (self):
		if self.host and self.user and self.passwd and self.db:
			self.sw.echo ("Connecting to MySQL Database. Host[" + self.host + "], User[" + self.user + "], DB[" + self.db + "]")
			self.mysql = mysql.connector.connect (host=self.host, user=self.user, passwd=self.passwd, database=self.db)
			self.connected = False
			self.connected_to_db = True
			mycursor = self.mysql.cursor (buffered=True)
			mycursor.execute ("SHOW TABLES")
			for x in mycursor:
				self.tables.append (x[0].lower())
			self.sw.echo ("MySQL Database Connected. Database has " + str(len(self.tables)) + " Tables")
		else:
			self.sw.echo ("ERROR: Missing one or more of [host, user, passwd, db]")

	def create_database_if_not_exists (self):
		if not self.connected:
			self.connect ()
		if self.connected:
			mycursor = self.mysql.cursor (buffered=True)
			mycursor.execute ("SHOW DATABASES")
			for x in mycursor:
				if (x[0] == self.db):
					self.sw.echo ("Found Pre-Existing Database [" + x[0] + "]")
					return True
			mycursor.execute ("CREATE DATABASE " + self.db)
			self.sw.echo ("Created Database [" + self.db + "]")

	def table_exists (self, table_name):
		for tabname in self.tables:
			if tabname.lower() == table_name.lower():
				self.sw.echo ("Found Pre-Existing Table [" + tabname + "]")
				return True
		self.sw.echo ("Table Missing [" + table_name + "]")
		return False

	def create_table_and_indexes (self, table_name, create_table_stmt, create_index_stmts):
		if self.connected_to_db:
			mycursor = self.mysql.cursor (buffered=True)
			mycursor.execute(create_table_stmt)
			self.sw.echo ("Created Table [" + table_name + "]")
			for index_stmt in create_index_stmts:
				mycursor.execute (index_stmt)
				self.sw.echo ("Created Index Using [" + index_stmt + "]")
				

	def get_max_value (self, tablename, colname, default_min):
		mycursor = self.mysql.cursor (buffered=True)
		mycursor.execute ('SELECT MAX(' + colname + ') FROM ' + tablename)
		myresult = mycursor.fetchall()
		for x in myresult:
			if x[0]:
				return x[0]
		return default_min

	def insert_rec (self, tablename, rec, pk_col_name):
		deletesql = "DELETE FROM " + tablename  + " WHERE Id = '" + rec[pk_col_name] + "'"
		mycursor = self.mysql.cursor (buffered=True)
		try:
			mycursor.execute (deletesql)
		except:
			self.sw.error ('Failed for: ' + deletesql)
			raise
		delCount = mycursor.rowcount

		insertsql = "INSERT INTO " + tablename + " (" + ",".join(rec.keys()) + ") VALUES ("
		arr = []
		for k in rec.keys():
			arr.append ('%s')
		insertsql += ",".join(arr) + ")"
		insertvals = []
		for colName in rec.keys():
			if isinstance(rec[colName], str):
				insertvals.append (str(rec[colName])[:255],)
			else:
				insertvals.append (rec[colName])
#		print (insertsql)
#		print (insertvals)
		try:
			mycursor.execute(insertsql, insertvals)
		except:
			self.sw.error ('Failed for: ' + insertsql)
			raise
		return delCount

	def commit (self):
		self.mysql.commit()
