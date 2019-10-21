import pymysql
import threading
import logging
from copy import deepcopy

class MysqlDBService(object):
	_instance_lock = threading.Lock()
	connection_kwargs = {}
	connect = None
	logger = None

	hasLog = False
	primaryKey = 'id'

	def __init__(self, *args, **kwargs):
		self.logger = logging.getLogger('MysqlDBService')
		self.connection_kwargs = kwargs

		self.connection()
		

	def connection(self):
		kwargs = self.connection_kwargs
		if 'host' in kwargs and 'user' in kwargs and 'passwd' in kwargs :
			host = kwargs['host']
			port = kwargs['port'] if 'port' in kwargs else 3306
			user = kwargs['user']
			passwd = kwargs['passwd']
			charset = kwargs['charset'] if 'charset' in kwargs else 'utf8'
			db = kwargs['db'] if 'db' in kwargs else 'example'

			try:
				self.connect = pymysql.connect(host=host, user=user, passwd=passwd, db=db, port=port, charset=charset)
			except pymysql.Error as e:
				print("pymysql Error:%s" % e)

	def reConnect(self):
		try:
			self.connect.ping()
		except:
			self.connection()

	@classmethod
	def instance(cls, *args, **kwargs):
		if not hasattr(MysqlDBService, "_instance"):
			with MysqlDBService._instance_lock:
				if not hasattr(MysqlDBService, "_instance"):
					MysqlDBService._instance = MysqlDBService(*args, **kwargs)
		return MysqlDBService._instance

	def setPrimaryKey(self,key):
		self.primaryKey = key
		return self

	def setShowLog(self,isShow):
		self.hasLog = isShow
		return self

	def test(self):
		return {'state':2008,'data':'this is a test'}

	def getOne(self, table,input_query={},input_field='*',input_orderby=[('id',1)]):
		query = deepcopy(input_query)
		field = deepcopy(input_field)
		orderby = deepcopy(input_orderby)
		sql = self._parse_query(table=table, query=query, field=field, orderby=orderby, limit=1)
		result = self.query_one(sql)
		return result

	def prevOne(self, table, id, input_query={}):
		result = None
		query = deepcopy(input_query)
		query['id'] = {'<':id}
		sql = self._parse_query(table=table, query=query,field='*',orderby=[('id',-1)],limit=1)
		result = self.query_one(sql)
		return result
		
	def nextOne(self, table, id, input_query={}):
		result = None
		query = deepcopy(input_query)
		query['id'] = {'>':id}
		sql = self._parse_query(table=table, query=query,field='*',orderby=[('id',1)],limit=1)
		result = self.query_one(sql)
		return result

	def getPage(self, table, input_query={},input_field='*', input_orderby=[('id',-1)], page=1, size=50,input_expect=["user"]):
		
		query = deepcopy(input_query)
		field = deepcopy(input_field)
		orderby = deepcopy(input_orderby)
		expect = deepcopy(input_expect)
		sql = self._parse_query(table=table, query=query,field=field,orderby=orderby, page=page, size=size)
		result = self.query(sql)
		total = self.getCount(table, query)
		last = int(total/size) if total%size==0 else int(total/size) + 1
		return {'data':result,'page':{"total":total,"size":size,"page":page,"last":last}}

	def getList(self, table, input_query={},input_field='*', input_orderby=[('id',-1)],limit=None,input_expect=["user"]):
		query = deepcopy(input_query)
		field = deepcopy(input_field)
		orderby = deepcopy(input_orderby)
		expect = deepcopy(input_expect)
		sql = self._parse_query(table=table, query=query,field=field,orderby=orderby, limit=limit)
		result = self.query(sql)
		return result

	def save(self, table,input_data,input_key='id'):
		result = {}
		new_id = 0
		data = deepcopy(input_data)
		if input_key in data:
			new_id = data[input_key]
			oldData = self.getOne(table, {input_key:new_id})
			if oldData:
				update_data = {}
				for key in data:
					if key not in ["id"]:
						if (key in oldData and data[key] != oldData[key]) or (key not in oldData):
							if type(data[key]).__name__=='bytes':
								update_data[key] = data[key].decode('utf-8')
							else:
								update_data[key] = data[key]
				if update_data:
					self.modify(table, {input_key:new_id}, update_data)
			else:
				new_id = self.add(table, data)
		else:
			new_id = self.add(table, data)

		if new_id:
			result = self.getOne(table, {"id":new_id})
		return result

	def add(self, table, input_data):
		result = None
		data = deepcopy(input_data)
		if data:
			sql = self._parse_insert(table, data)
			result = self.execute(sql)
		return result

	def modify(self, table,input_query,input_data):
		result = {}
		if input_data:
			query = deepcopy(input_query)
			data = deepcopy(input_data)
			sql = self._parse_update(table, query,data)
			result = self.execute(sql)
		return result
	
	def delete(self, table,input_query):
		query = deepcopy(input_query)
		sql = self._parse_del(table, query)
		result = self.execute(sql)
		return result

	def getCount(self, table, input_query={}):
		result = 0
		query = deepcopy(input_query)
		sql = 'select count(1) as count from '+ table + ' '
		where_sql = self._where(query)
		if where_sql:
			sql += 'where '+ where_sql 
		res = self.query_one(sql)
		if res:
			result = int(res['count'])
		return result

	def _parse_query(self, table, *args, **kwargs):
		query = kwargs['query'] if 'query' in kwargs else {}
		field = kwargs['field'] if 'field' in kwargs else '*'
		orderby = kwargs['orderby'] if 'orderby' in kwargs else [('id',1)]
		limit = kwargs['limit'] if 'limit' in kwargs else None
		page = int(kwargs['page']) if 'page' in kwargs else 0
		size = int(kwargs['size']) if 'size' in kwargs else 0

		if page and size:
			begin = (page -1 )* size
			limit = str(begin)+','+str(size)

		field_where = self._field(field)

		sql = 'select ' + field_where + ' from '+ table + ' '
		where_sql = self._where(query)
		if where_sql:
			sql += 'where '+ where_sql + ' '
		order_sql = self._order(orderby)
		if order_sql:
			sql += order_sql + ' '
		limit_sql = self._limit(limit)
		if limit_sql:
			sql +=  limit_sql + ' '
		return sql
	def _parse_insert(self, table, grpup):
		sql = 'insert into '+ table + ' '
		if type(grpup).__name__ == 'dict':
			grpup = [grpup]
		columns = []
		for data in grpup:
			for key in data:
				if key not in columns:
					columns.append(key)
		values = []
		for data in grpup:
			tmp = []
			for key in columns:
				if key in data:
					value = str(data[key])
					tmp.append(pymysql.escape_string(value))
				else:
					tmp.append('')
			values.append(tmp)
		sql += ' (' + ', '.join(columns) + ') values '
		value_sql = ''
		for value in values:
			value_sql += ' ("' + '", "'.join(value) + '"), '
		return sql + value_sql[0:-2]

	def _parse_update(self, table, query, data):
		sql = ''
		data_sql = ''
		for key in data:
			data_sql += key + '="'+str(data[key])+'", '
		if data_sql:
			sql = 'update '+ table + ' set ' + data_sql[0:-2]
		where_sql = self._where(query)
		if where_sql:
			sql = sql + ' where '+ where_sql + ' '
		return sql

	def _parse_del(self, table, query):
		where_sql = self._where(query)
		if where_sql:
			where_sql = 'where '+ where_sql + ' '

		sql = 'delete from  '+ table + ' ' + where_sql
		return sql
		
	def _field(self,query):
		sql = ''
		if type(query).__name__=='tuple':
			query = list(query)
		if type(query).__name__=='list':
			sql = ','.join(query)
		elif not query :
			sql = '*'
		else:
			sql = query
		return sql

	def _where(self,query):
		sql = ''
		if type(query).__name__=='dict':
			for key in query:
				opeartor = '='
				value = ''
				if type(query[key]).__name__!='dict':
					tmp = {'=':query[key]}
				else:
					tmp = query[key]
				for k in tmp:
					opeartor = k
					value = pymysql.escape_string(str(tmp[k]))
				sql += key + ' ' + opeartor + ' "'+ value + '" and '
		return sql[0:-4]

	def _order(self,orderby):
		sql = 'order by '
		for item in orderby:
			order = item[0]
			sort = 'asc' if item[1]==1 else 'desc'
			sql += order + ' ' + sort + ','

		return sql[0:-1]

	def _limit(self,limit):
		if limit:
			if type(limit).__name__ !='string':
				limit = str(limit)
			return 'limit ' + limit
		else:
			return ''
	def query_one(self, sql, params=None):
		self.reConnect()
		cur = None
		result = None
		if self.connect:
			try:
				cur = self.connect.cursor(pymysql.cursors.DictCursor)
				if self.hasLog:
					self.logger.info(sql)
				count = cur.execute(sql,params)
				result = cur.fetchone()
				self.connect.commit()
			except pymysql.Error as e:
				self.connect.rollback()
				print("pymysql Error:%s" % e)
			finally:
				if cur:
					cur.close()
		return result

	def queryAndFlag(self, table,input_query={},input_flag={}):
		self.reConnect()
		cur = None
		result = None
		query = deepcopy(input_query)
		sql1 = self._parse_query(table=table, query=query,limit=1)
		if self.connect:
			try:
				cur = self.connect.cursor(pymysql.cursors.DictCursor)
				if self.hasLog:
					self.logger.info(sql1)
					print(sql1)
				count = cur.execute(sql1)
				info = cur.fetchone()
				if info:
					data = deepcopy(input_flag)
					sql2 = self._parse_update(table,{'id':info['id']},data)
					if self.hasLog:
						self.logger.info(sql2)
						print(sql2)
					count = cur.execute(sql2)
					sql3 = self._parse_query(table,query={'id':info['id']},limit=1)
					count = cur.execute(sql3)
					if self.hasLog:
						self.logger.info(sql3)
						print(sql3)
					result = cur.fetchone()
				self.connect.commit()
			except pymysql.Error as e:
				self.connect.rollback()
				print("pymysql Error:%s" % e)
			finally:
				if cur:
					cur.close()
		return result

	def query(self, sql, params=None):
		self.reConnect()
		cur = None
		result = None
		if self.connect:
			try:
				cur = self.connect.cursor(pymysql.cursors.DictCursor)
				if self.hasLog:
					self.logger.info(sql)
					print(sql)
				count = cur.execute(sql,params)
				result = cur.fetchall()
				self.connect.commit()
			except pymysql.Error as e:
				self.connect.rollback()
				print("pymysql Error:%s" % e)
			finally:
				if cur:
					cur.close()
		return result

	def execute(self, sql, params=None):
		self.reConnect()
		cur = None
		count = 0
		if self.connect:
			try:
				cur = self.connect.cursor()
				if self.hasLog:
					self.logger.info(sql)
					print(sql)
				count = cur.execute(sql,params)
				if sql.lower().find('insert') > -1:
					count = self.connect.insert_id()
				self.connect.commit()
			except pymysql.Error as e:
				if self.connect:
					self.connect.rollback()
				print("pymysql Error:%s" % e)
			finally:
				if cur:
					cur.close()
		return count

	def close(self):
		if self.connect:
			self.connect.close()

	def __del__(self):
		self.close()
	
if __name__ == "__main__":

	db = MysqlDBService.instance(host='localhost', port=3306, user='root', passwd='123456', db='example', charset='utf8')
	result = db.query('select * from data',())
	print(result)