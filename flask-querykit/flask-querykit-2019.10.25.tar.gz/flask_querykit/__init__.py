#coding:utf8

__version__='2019.10.25'

from flask import request
from mongoengine.queryset.visitor import Q
import traceback

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def queryset(model):
	def wrapper1(func):
		def wrapper2(*args, **kwargs):
			request.queryset = model.objects.all()
			return func(*args, **kwargs)
		return wrapper2
	return wrapper1


def get_query_string():

	params = request.environ['QUERY_STRING'].split("&")


	l = []

	if params != ['']:
		l = [
			{
				p.split('=')[0]:p.split('=')[1]
			} for p in params
		]
	else:
		l = []
	d = {}
	for ll in l:
		d.update(ll)

	return d

def get_queryset(model):
	if not hasattr(request,'queryset'):
		request.queryset = model.objects()

def ordering(model,key='ordering',allow_field=[]):
	def wrapper1(func):
		def wrapper2(*args, **kwargs):

			d = get_query_string()

			get_queryset(model)

			if d.get(key) in allow_field:
					request.queryset = request.queryset.order_by(d.get(key))
			return func(*args, **kwargs)
		return wrapper2
	return wrapper1

def searching(model,key='searching',allow_field=[]):
	def wrapper1(func):
		def wrapper2(*args, **kwargs):

			get_queryset(model)

			keys = [v+'__contains' for v in allow_field]

			_dict = {}
			_list = [{k:request.args.get(key)} for k in keys]
			arg = [
				Q(**_dict) for _dict in _list
			]

			_arg = None
			for a in arg:
				if _arg == None:
					_arg = a
				else:
					_arg = _arg|a

			if request.args.get(key):
				request.queryset = request.queryset.filter(_arg)

			return func(*args, **kwargs)
		return wrapper2
	return wrapper1

def paginating(model,page_field='page',page_size_field='page_size',force=False):
	def wrapper1(func):
		def wrapper2(*args, **kwargs):

			get_queryset(model)

			page = int(request.args.get(page_field,0))

			page_size = int(request.args.get(page_size_field,10))	

			request.page_count = len(request.queryset)

			try:
				pass
				#request.queryset.paginating(page=page, per_page=page_size)
				request.queryset = request.queryset[(page)*page_size:(page+1)*page_size]
			except Exception as e:
				raise e
				logger.error(e)
				if force is False:
					request.queryset = []

			return func(*args, **kwargs)
		return wrapper2
	return wrapper1



def filting(model,domains,f=None):
	def wrapper1(func):
		def wrapper2(*args, **kwargs):
			
			get_queryset(model)

			if f is not None:
				f()

			_domains = _filting(domains)

			logger.debug(_domains)

			#request.queryset = model.objects(_domains)
			request.queryset = request.queryset.filter(_domains)

			return func(*args, **kwargs)
		return wrapper2
	return wrapper1






from mongoengine.queryset.visitor import Q
def _filting(domains):

	options = {
		'=':'exact',
		'!=':'ne',
		'<':'lt',
		'<=':'lte',
		'>':'gt',
		'>=':'gte',
		'in':'in',
		'nin':'nin',
		'like':'contains',
		#'not':'not',
		#'mod':'mod',
		#'v':'all',
		#'size':'size',
		#'exist':'exist',
	}


	q = None
	for index,domain in enumerate(domains):

		if index % 2 != 1:

			#
			# 2层及以上
			#
			if type(domains[index][0]) == tuple:
				_q = _filting(domains[index])

			#
			# 1层
			#
			if type(domain[0]) == str:
				#logger.error(domain)
				key = str(domain[0]) + '__' + options[domain[1]]
				
				# flask-restkit
				try:
					value = eval(domain[2])
				except:
					value = domain[2]

				if value is None:
					continue

				_q = Q(**{key:value})

			if q == None:
				q = _q
			else:
				if domains[index-1] == '|':
					q = (q|_q)
				else:
					q = (q&_q)

	return q