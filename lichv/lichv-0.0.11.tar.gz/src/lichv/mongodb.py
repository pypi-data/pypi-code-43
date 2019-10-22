import pymongo
import threading
import time
import sys
import logging
from copy import deepcopy
from bson.objectid import ObjectId
from urllib.parse import quote_plus
from gridfs import GridFS

class MongoDBService(object):
	_instance_lock = threading.Lock()
	connect = None
	database = None

	modulename = None
	module = None

	def __init__(self, *args, **kwargs):
		self.logger = logging.getLogger('MongoDBService')
		connection = ''
		db = kwargs['db'] if 'db' in kwargs else 'example'

		if 'host' in kwargs and 'user' in kwargs and 'passwd' in kwargs :
			host = kwargs['host']
			port = kwargs['port']
			user = kwargs['user']
			passwd = kwargs['passwd']
			connection = "mongodb://%s:%s@%s" % (quote_plus(user), quote_plus(passwd), host+':'+str(port))
		elif 'connection' in kwargs :
			connection = kwargs['connection']

		if connection:
			try:
				self.connect = pymongo.MongoClient(connection)
			except:
				self.logger.info("cannot connect mongodb"+connection)
				print("cannot connect mongodb"+connection)

		self.setDatabase(db)
		
	@classmethod
	def instance(cls, *args, **kwargs):
		if not hasattr(MongoDBService, "_instance"):
			with MongoDBService._instance_lock:
				if not hasattr(MongoDBService, "_instance"):
					MongoDBService._instance = MongoDBService(*args, **kwargs)
		return MongoDBService._instance

	def setDatabase(self,db):
		if self.connect:
			self.database = self.connect[db]
		return self

	def getOne(self, module, query={},field='*', orderby=[('_id',1)]):
		result = None
		collection = self.database[module]
		if '_id' in query:
			query['_id'] = ObjectId(query['_id'])
		if 'id' in query:
			query['_id'] = ObjectId(query['id'])
			del query['id']
		lists = cursor = collection.find(query).sort(orderby).limit(1)
		for item in lists:
			result = {}
			for key in item:
				if key not in ["user"]:
					if key=='_id':
						result["id"] = str(item["_id"])
					else:
						result[key] = item[key]
		return result

	def prevOne(self, module, code, input_query={}):
		result = None
		query = deepcopy(input_query)
		query['_id'] = {'$lt':ObjectId(code)}
		collection = self.database[module]
		lists = collection.find(query).sort([('_id',-1)]).limit(1)
		for item in lists:
			result = {}
			for key in item:
				if key=='_id':
					result = str(item["_id"])
		return result
		
	def nextOne(self, module, code, input_query={}):
		result = None
		query = deepcopy(input_query)
		query['_id'] = {'$gt':ObjectId(code)}
		collection = self.database[module]
		lists = collection.find(query).sort([('_id',1)]).limit(1)
		for item in lists:
			result = {}
			for key in item:
				if key=='_id':
					result = str(item["_id"])
		return result

	def getPage(self, module, input_query={},input_field='*', input_orderby=[('_id',-1)], page=1, size=50,input_expect=['passwd','password']):
		result = []
		query = deepcopy(input_query)
		field = deepcopy(input_field)
		orderby = deepcopy(input_orderby)
		expect = deepcopy(input_expect)
		collection = self.database[module]

		if '_id' in query:
			query['_id'] = ObjectId(query['_id'])
		if 'id' in query:
			query['_id'] = ObjectId(query['id'])
			del query['id']
		cursor = collection.find(query)
		total = collection.count_documents(query)
		last = int(total/size) if total%size==0 else int(total/size) + 1
		lists = cursor.sort(orderby).limit(size).skip((page - 1) * size)
		for item in lists:
			tmp = {}
			for key in item:
				if key not in expect:
					if key=='_id':
						tmp["id"] = str(item["_id"])
					else:
						tmp[key] = item[key]
			result.append(tmp)
		return {"data":result,"page":{"total":total,"size":size,"page":page,"last":last},'query':query}

	def getList(self, module, input_query={}, input_field='*', input_orderby=[('_id',-1)],limit=None,input_expect=['passwd','password']):
		result = []
		query = deepcopy(input_query)
		field = deepcopy(input_field)
		orderby = deepcopy(input_orderby)
		expect = deepcopy(input_expect)
		collection = self.database[module]

		if '_id' in query:
			query['_id'] = ObjectId(query['_id'])
		if 'id' in query:
			query['_id'] = ObjectId(query['id'])
			del query['id']
		lists = collection.find(query).sort(orderby)
		if limit:
			if type(limit).__name__=='int':
				lists = lists.limit(limit)
			elif type(limit).__name__ == 'tuple':
				lists = lists.limit(limit[0]).skip(limit[1])
			
		for item in lists:
			tmp = {}
			for key in item:
				if key not in expect:
					if key=='_id':
						tmp["id"] = str(item["_id"])
					else:
						tmp[key] = item[key]
			result.append(tmp)
		return result

	def save(self, module, input_data, key='id'):
		result = {}
		newid = ''
		data = deepcopy(input_data)
		collection = self.database[module]
		if key in data:
			value = data[key]
			newid = value
			if key=='id':
				key = '_id'
				value = ObjectId(value)
			oldData = collection.find_one({key:value})
			update_data = {}
			for ke in data:
				if ke not in ["id"]:
					if oldData and (ke in oldData and data[ke] != oldData[ke]) or (ke not in oldData):
						if type(data[ke]).__name__=='bytes':
							update_data[ke] = data[ke].decode('utf-8')
						else:
							update_data[ke] = data[ke]
			update_data["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
			collection.update_one({key:value}, {"$set":update_data})
		else:
			newObj = collection.insert_one(data)
			newid = str(newObj.inserted_id)

		newData = collection.find_one({"_id":ObjectId(newid)})
		for key in newData:
			if key not in ["user"]:
				if key=="_id":
					result["id"]= str(newData["_id"])
				else:
					result[key] = newData[key]
		return result

	def add(self, module, input_data):
		result = {}
		collection = self.database[module]
		data = deepcopy(input_data)
		if data:
			newObj = collection.insert_one(data)
			newData = collection.find_one({"_id":ObjectId(newObj.inserted_id)})
			if newData:
				for key in newData:
					if key not in ['passwd','password']:
						if key=="_id":
							result["id"]= str(newData["_id"])
						else:
							result[key] = newData[key]
		return result

	def modify(self, module,input_query,input_data):
		query = deepcopy(input_query)
		data = deepcopy(input_data)
		collection = self.database[module]
		if '_id' in query:
			query['_id'] = ObjectId(query['_id'])
		if 'id' in query:
			query['_id'] = ObjectId(query['id'])
			del query['id']
		result = collection.update_many(query,{"$set":data})
		return result.modified_count
	
	def delete(self, module,input_query):
		query = deepcopy(input_query)
		collection = self.database[module]
		if '_id' in query and type(query['_id']).__name__=='string':
			query['_id'] = ObjectId(query['_id'])
		if 'id' in query and type(query['id']).__name__=='string':
			query['_id'] = ObjectId(query['id'])
			del query['id']
		result = collection.delete_many(query,{'multi':1})
		return result.deleted_count

	def getCount(self, module, input_query={}):
		query = deepcopy(input_query)
		collection = self.database[module]
		if '_id' in query:
			query['_id'] = ObjectId(query['_id'])
		if 'id' in query:
			query['_id'] = ObjectId(query['id'])
			del query['id']
		result = collection.count_documents(query)
		return result

	def queryAndFlag(self, module,input_query={},input_flag={}):
		result = None
		query = deepcopy(input_query)
		collection = self.database[module]
		if '_id' in query:
			query['_id'] = ObjectId(query['_id'])
		if 'id' in query:
			query['_id'] = ObjectId(query['id'])
			del query['id']
		result = self.getOne(module,query)
		if result:
			code = str(result['id'])
			collection.update_one({'_id':ObjectId(code)},{"$set":input_flag})
			result = self.getOne(module,{'_id':ObjectId(code)})
		return result

	def server(self,module=''):
		result = {}
		if module:
			collection = self.database[module]
			result = collection.stats();
		else:
			result = self.database.stats()
		return result

	def write(self,table,filename,data,content_type='',metadata={}):
		gridfs_col = GridFS(self.database, collection=table)
		filter_condition = {'filename':filename}
		if content_type:
			filter_condition['content_type'] = content_type
		if len(metadata):
			filter_condition['metadata'] = metadata
		result = gridfs_col.put(data=data,encoding='utf-8', **filter_condition)
		return result


	def readByName(self,table,filename):
		gridfs_col = GridFS(self.database, collection=table)
		data = gridfs_col.get_version(filename=filename, version=0)
		return str(data._id),data.filename,data.content_type,data.length,data.chunk_size,data.upload_date,data.metadata,data.read().decode('utf-8')

	def readByID(self,table,file_id):
		gridfs_col = GridFS(self.database, collection=table)
		data = gridfs_col.get(file_id=ObjectId(file_id))
		return str(data._id),data.filename,data.content_type,data.length,data.chunk_size,data.upload_date,data.metadata,data.read().decode('utf-8')

	def getCollectionNames(self):
		result = self.database.collection_names()
		return result

	def close(self):
		if self.connect:
			self.connect.close()

	def __del__(self):
		self.close()
	
if __name__ == "__main__":

	db = MongoDBService.instance(connection='mongodb://root:123456@127.0.0.1:27017/', db='data')
	result = db.setModule('github').getPages()
	print(result)